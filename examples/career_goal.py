from __future__ import annotations

from dataclasses import asdict, dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Job, JobMatch, Preference
from app.services.utils import normalize_text


# Strongest directions are intentionally broader than exact titles. The gate
# decides whether a role advances the user's career, not whether keywords match.
FAMILY_SIGNALS: dict[str, tuple[str, ...]] = {}

OFF_TARGET: tuple[str, ...] = ()

ADJACENT: tuple[str, ...] = ()


ROLE_STOPWORDS = {
    "de", "da", "do", "das", "dos", "e", "em", "para", "com", "the", "of", "and",
    "junior", "jr", "pleno", "senior", "sr", "i", "ii", "iii", "a",
}


def _role_title_match(role: str, title: str) -> bool:
    """Match preferred career titles even when companies add level/gender qualifiers.

    Exact substring matching misses common Brazilian titles such as
    ``Desenvolvedor(a) Júnior de Automações`` for the preferred route
    ``Desenvolvedor de Automações``. Only significant role tokens participate,
    keeping the career gate deterministic and conservative.
    """
    role_norm = normalize_text(role)
    title_norm = normalize_text(title)
    if not role_norm or not title_norm:
        return False
    if role_norm in title_norm or title_norm in role_norm:
        return True
    role_tokens = {token for token in role_norm.replace("(", " ").replace(")", " ").split() if token not in ROLE_STOPWORDS}
    title_tokens = {token for token in title_norm.replace("(", " ").replace(")", " ").split() if token not in ROLE_STOPWORDS}
    if len(role_tokens) < 2:
        return False
    overlap = len(role_tokens & title_tokens) / len(role_tokens)
    return overlap >= 0.8


def _family_signals(family: str) -> tuple[str, ...]:
    """Return deterministic signals for built-in *or user-defined* families.

    Built-in families keep curated aliases. A new career family entered in the
    profile is reduced to meaningful tokens so the gate adapts without a code
    release. This is intentionally conservative: custom-family tokens improve
    discovery/direction, but never create evidence for resume claims.
    """
    curated = FAMILY_SIGNALS.get(family)
    if curated:
        return curated
    norm = normalize_text(family)
    tokens = tuple(
        token for token in norm.replace("/", " ").replace("-", " ").split()
        if len(token) >= 3 and token not in ROLE_STOPWORDS
    )
    return tuple(dict.fromkeys((norm, *tokens))) if norm else ()


@dataclass(slots=True)
class CareerGoalDecision:
    score: int
    status: str
    family: str
    reasons: list[str]
    off_target_hits: list[str]
    strong_hits: list[str]

    def as_dict(self) -> dict:
        return asdict(self)


class CareerGoalService:
    """Deterministic career-direction gate.

    This is deliberately independent from LLMs. It protects the user from a
    technically compatible vacancy that would pull the search into a career
    direction they do not want.
    """

    def __init__(self, db: Session):
        self.db = db

    def _positioning_rules(self) -> dict:
        item = self.db.scalar(select(Preference).where(Preference.key == "positioning_rules"))
        return dict(item.value or {}) if item else {}

    def evaluate(self, job: Job, match: JobMatch | None = None) -> CareerGoalDecision:
        title = normalize_text(job.title or "")
        text = normalize_text(f"{job.title} {job.description[:12000]}")
        rules = self._positioning_rules()
        preferred_roles = [normalize_text(x) for x in rules.get("preferred_roles", [])]
        preferred_families = {str(x).strip() for x in rules.get("preferred_families", []) if str(x).strip()}
        excluded_focus = [normalize_text(x) for x in rules.get("excluded_focus", [])]

        # If no career direction exists yet, do not inherit the product author's
        # original automation/AI bias. The job stays review-only until onboarding
        # establishes the user's preferred roles/families.
        if not preferred_roles and not preferred_families:
            return CareerGoalDecision(
                score=40,
                status="review",
                family=(job.title or "Perfil não configurado"),
                reasons=["Configure cargos ou famílias profissionais no perfil antes de priorizar esta vaga."],
                off_target_hits=[],
                strong_hits=[],
            )

        off_hits = sorted({term for term in (*OFF_TARGET, *excluded_focus) if term and term in text})
        candidate_families = list(FAMILY_SIGNALS)
        candidate_families.extend(f for f in preferred_families if f not in FAMILY_SIGNALS)
        family_scores: dict[str, int] = {}
        family_hits: dict[str, list[str]] = {}
        for family_name in candidate_families:
            signals = _family_signals(family_name)
            hits = sorted({signal for signal in signals if signal and signal in text})
            title_hits = [signal for signal in signals if signal and signal in title]
            family_scores[family_name] = min(100, len(hits) * 8 + len(title_hits) * 15)
            family_hits[family_name] = hits
        family = max(family_scores, key=family_scores.get) if family_scores else (next(iter(preferred_families), job.title or "Revisão"))
        strong_hits = family_hits.get(family, [])

        preferred_title = any(_role_title_match(role, title) for role in preferred_roles)
        preferred_signal_set = {
            signal
            for preferred_family in preferred_families
            for signal in _family_signals(preferred_family)
            if signal
        }
        broad_preferred = preferred_title or any(signal in text for signal in preferred_signal_set)
        adjacent_hits = sorted({term for term in ADJACENT if term in text})

        score = 35
        reasons: list[str] = []
        if preferred_title:
            score += 30
            reasons.append("O título está dentro das rotas profissionais priorizadas.")
        if broad_preferred:
            score += min(30, 6 + len(strong_hits) * 4)
            reasons.append(f"A vaga conversa principalmente com {family.lower()}.")
        if family in preferred_families and len(strong_hits) >= 2:
            score += 15
            reasons.append("Essa família profissional está marcada como prioridade no seu perfil.")
        if match and match.score >= 75:
            score += 10
            reasons.append("A aderência técnica atual é forte.")
        elif match and match.score < 55:
            score -= 12
            reasons.append("A aderência atual é baixa para priorização.")
        if adjacent_hits and not broad_preferred:
            score += 8
            reasons.append("É uma rota adjacente; vale apenas se a descrição mantiver o foco desejado.")
        if off_hits:
            score -= min(70, 30 + len(off_hits) * 12)
            reasons.append("Há sinais de foco profissional que você explicitamente não prioriza.")

        score = max(0, min(100, score))
        if off_hits and score < 55:
            status = "off_target"
        elif score >= 72:
            status = "target"
        elif score >= 58:
            status = "adjacent"
        else:
            status = "review"
        if not reasons:
            reasons.append("A direção profissional precisa de revisão antes de priorizar esta vaga.")
        return CareerGoalDecision(score, status, family, reasons, off_hits, strong_hits)

    def persist(self, match: JobMatch, decision: CareerGoalDecision, *, commit: bool = True) -> JobMatch:
        match.career_goal_score = decision.score
        match.career_goal_status = decision.status
        match.career_goal_family = decision.family
        match.career_goal_reasons = decision.reasons
        if commit:
            self.db.commit()
        return match

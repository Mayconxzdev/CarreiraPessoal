from __future__ import annotations

"""Standalone, synthetic demonstration of three CarreiraPessoal decision gates.

This file intentionally uses only the Python standard library and synthetic data.
It is not the private production implementation; it makes the public decision
contracts executable without exposing personal data, credentials or private code.
"""

from dataclasses import asdict, dataclass
import json
import re
import unicodedata


def normalize(text: str) -> str:
    value = unicodedata.normalize("NFKD", text or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value.lower()).strip()


@dataclass(frozen=True)
class Job:
    title: str
    description: str
    fit_score: int
    opportunity_value: int = 75


@dataclass(frozen=True)
class CareerPreferences:
    preferred_roles: tuple[str, ...]
    preferred_families: tuple[str, ...]
    excluded_focus: tuple[str, ...] = ()


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    text: str


@dataclass(frozen=True)
class CareerGoalDecision:
    score: int
    status: str
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceDecision:
    allowed: bool
    supporting_ids: tuple[str, ...]
    unsupported_fragments: tuple[str, ...]


@dataclass(frozen=True)
class ResumeRouteDecision:
    action: str
    score: int
    reason: str


ROLE_STOPWORDS = {
    "de", "da", "do", "das", "dos", "e", "em", "para", "com", "the", "of", "and",
    "junior", "jr", "pleno", "senior", "sr", "i", "ii", "iii", "a",
}

SENSITIVE_PATTERNS = (
    r"\bliderei\b", r"\bgerenciei\b", r"\bcoordenei\b", r"\bsenior\b",
    r"\bespecialista\b", r"\bproducao\b", r"\b\d+[.,]?\d*\s*%",
    r"\b\d+\s+(?:pessoas|usuarios|clientes|projetos|anos)\b",
)


def meaningful_tokens(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9+#.\-]+", normalize(text))
        if len(token) >= 3 and token not in ROLE_STOPWORDS
    }


def role_match(preferred: str, title: str) -> bool:
    preferred_n, title_n = normalize(preferred), normalize(title)
    if preferred_n in title_n or title_n in preferred_n:
        return True
    wanted = meaningful_tokens(preferred_n)
    found = meaningful_tokens(title_n)
    return len(wanted) >= 2 and len(wanted & found) / len(wanted) >= 0.8


def career_goal(job: Job, preferences: CareerPreferences) -> CareerGoalDecision:
    if not preferences.preferred_roles and not preferences.preferred_families:
        return CareerGoalDecision(40, "review", ("Configure uma direção profissional antes de priorizar.",))

    text = normalize(f"{job.title} {job.description}")
    score = 35
    reasons: list[str] = []

    preferred_title = any(role_match(role, job.title) for role in preferences.preferred_roles)
    family_tokens = {
        token
        for family in preferences.preferred_families
        for token in meaningful_tokens(family)
    }
    family_hits = sorted(token for token in family_tokens if token in text)
    excluded_hits = sorted(term for term in map(normalize, preferences.excluded_focus) if term and term in text)

    if preferred_title:
        score += 30
        reasons.append("O título está dentro das rotas profissionais priorizadas.")
    if family_hits:
        score += min(25, 8 + len(family_hits) * 5)
        reasons.append("A descrição contém sinais da família profissional priorizada.")
    if job.fit_score >= 75:
        score += 10
        reasons.append("A aderência técnica é forte.")
    elif job.fit_score < 55:
        score -= 12
        reasons.append("A aderência técnica precisa de revisão.")
    if excluded_hits:
        score -= min(70, 30 + 12 * len(excluded_hits))
        reasons.append("Há foco explicitamente excluído da direção profissional.")

    score = max(0, min(100, score))
    status = "off_target" if excluded_hits and score < 55 else "target" if score >= 72 else "adjacent" if score >= 58 else "review"
    return CareerGoalDecision(score, status, tuple(reasons or ["Revisão manual necessária."]))


def _sensitive(text: str) -> bool:
    return any(re.search(pattern, normalize(text)) for pattern in SENSITIVE_PATTERNS)


def _fragments(claim: str) -> list[str]:
    return [part.strip() for part in re.split(r"[.;]|\s+e\s+|\s+and\s+", normalize(claim)) if len(part.strip()) >= 4]


def evidence_guard(claim: str, evidence: tuple[Evidence, ...]) -> EvidenceDecision:
    if not claim.strip():
        return EvidenceDecision(False, (), (claim,))

    supported: list[str] = []
    unsupported: list[str] = []
    for fragment in _fragments(claim):
        fragment_tokens = meaningful_tokens(fragment)
        matches: list[str] = []
        for item in evidence:
            candidate = normalize(item.text)
            if fragment == candidate or fragment in candidate:
                matches.append(item.evidence_id)
                continue
            if _sensitive(fragment):
                continue
            candidate_tokens = meaningful_tokens(candidate)
            if fragment_tokens and len(fragment_tokens & candidate_tokens) / len(fragment_tokens) >= 0.8:
                matches.append(item.evidence_id)
        if matches:
            supported.extend(matches[:3])
        else:
            unsupported.append(fragment)

    return EvidenceDecision(
        allowed=not unsupported,
        supporting_ids=tuple(dict.fromkeys(supported)),
        unsupported_fragments=tuple(unsupported),
    )


def resume_route(job: Job, goal: CareerGoalDecision, *, evidence_ok: bool, existing_ready_resume: bool = False) -> ResumeRouteDecision:
    if goal.status == "off_target":
        return ResumeRouteDecision("blocked", goal.score, "A vaga foge da direção profissional configurada.")
    if job.fit_score < 60:
        return ResumeRouteDecision("review", job.fit_score, "A aderência está abaixo do limite automático da demonstração.")
    if job.opportunity_value < 55:
        return ResumeRouteDecision("review", job.opportunity_value, "O valor da oportunidade ainda exige revisão humana.")
    if goal.score < 65:
        return ResumeRouteDecision("review", goal.score, "A direção profissional ainda não é forte o bastante para automação.")
    if not evidence_ok:
        return ResumeRouteDecision("review", min(job.fit_score, goal.score), "Há afirmações sem evidência suficiente.")
    if existing_ready_resume:
        return ResumeRouteDecision("reuse", 100, "A versão atual já corresponde à vaga e às evidências aprovadas.")
    return ResumeRouteDecision("generate", max(job.fit_score, goal.score), "Preparar uma composição baseada apenas nas evidências aprovadas.")


def run_demo() -> dict:
    preferences = CareerPreferences(
        preferred_roles=("Analista de Automação e Integrações", "Analista de Automação e IA"),
        preferred_families=("automação integrações", "processos IA"),
        excluded_focus=("vendas porta a porta", "suporte call center"),
    )
    job = Job(
        title="Analista Júnior de Automação e Integrações",
        description="Automação de processos, APIs REST, webhooks, Python e acompanhamento de workflows.",
        fit_score=82,
        opportunity_value=78,
    )
    evidence = (
        Evidence("fact:automation", "Automação de processos com APIs REST, webhooks e Python."),
        Evidence("fact:deployment", "Implantação e sustentação de soluções internas."),
    )
    supported_claim = evidence_guard("Automação de processos com APIs REST, webhooks e Python.", evidence)
    unsupported_claim = evidence_guard("Liderei 20 pessoas em produção.", evidence)
    goal = career_goal(job, preferences)
    route = resume_route(job, goal, evidence_ok=supported_claim.allowed)
    return {
        "career_goal": asdict(goal),
        "supported_claim": asdict(supported_claim),
        "unsupported_claim": asdict(unsupported_claim),
        "resume_route": asdict(route),
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), ensure_ascii=False, indent=2))

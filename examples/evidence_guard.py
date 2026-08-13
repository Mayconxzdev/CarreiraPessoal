from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import ProfileFact, Project
from app.services.utils import normalize_text


ALLOWED_STATUSES = {"verified", "user_asserted"}
SENSITIVE_PATTERNS = (
    r"\bliderei\b", r"\bgerenciei\b", r"\bcoordenei\b", r"\bchefiei\b",
    r"\bequipe\b", r"\btime de\b", r"\bespecialista\b", r"\bavancad[oa]\b",
    r"\bproducao\b", r"\balta disponibilidade\b", r"\bmilh(?:ao|oes|ar)\b",
    r"\b\d+[.,]?\d*\s*%", r"\b\d+\s+(?:pessoas|usuarios|clientes|projetos|anos)\b",
)
STOPWORDS = {
    "para", "com", "como", "uma", "uns", "das", "dos", "que", "por", "em", "de",
    "do", "da", "e", "ou", "no", "na", "nos", "nas", "ao", "aos", "as", "os",
    "the", "and", "for", "with", "from", "into", "using",
}


@dataclass(slots=True)
class EvidenceCheck:
    allowed: bool
    supporting_ids: list[str]
    reason: str
    unsupported_fragments: list[str]


class EvidenceGuard:
    """Validates claims against immutable, current evidence.

    It intentionally rejects loose keyword overlap. Claims with leadership, scale, metrics,
    seniority or production assertions require near-exact evidence.
    """

    def __init__(self, db: Session):
        self.db = db

    def current_facts(self) -> list[ProfileFact]:
        return list(
            self.db.scalars(
                select(ProfileFact).where(
                    ProfileFact.is_current.is_(True),
                    ProfileFact.evidence_status.in_(ALLOWED_STATUSES),
                )
            )
        )

    def verified_projects(self) -> list[Project]:
        return list(
            self.db.scalars(
                select(Project)
                .options(selectinload(Project.latest_version))
                .where(Project.is_current.is_(True))
            )
        )

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {
            token for token in re.findall(r"[a-z0-9+#.\-]+", normalize_text(text))
            if len(token) >= 3 and token not in STOPWORDS
        }

    @staticmethod
    def _fragments(claim: str) -> list[str]:
        fragments = re.split(r"[.;]|\s+e\s+|\s+and\s+", normalize_text(claim))
        return [fragment.strip() for fragment in fragments if len(fragment.strip()) >= 4]

    @staticmethod
    def _sensitive(text: str) -> bool:
        normalized = normalize_text(text)
        return any(re.search(pattern, normalized) for pattern in SENSITIVE_PATTERNS)

    def _evidence_candidates(self) -> list[tuple[str, str]]:
        candidates: list[tuple[str, str]] = []
        for fact in self.current_facts():
            candidates.append((f"fact:{fact.id}:{fact.key}", fact.value))
        for project in self.verified_projects():
            version = project.latest_version
            if not version or version.evidence_status not in ALLOWED_STATUSES:
                continue
            candidates.append((f"project:{project.id}:{project.name}", project.name))
            candidates.append((f"project:{project.id}:{project.name}:description", version.description))
            for technology in version.technologies or []:
                candidates.append((f"project:{project.id}:{project.name}:technology", technology))
        return candidates

    @staticmethod
    def _candidate_supports(fragment: str, candidate: str, sensitive: bool) -> bool:
        fragment_n = normalize_text(fragment)
        candidate_n = normalize_text(candidate)
        if not fragment_n or not candidate_n:
            return False
        if fragment_n == candidate_n or fragment_n in candidate_n:
            return True
        if sensitive:
            return False
        fragment_tokens = EvidenceGuard._tokens(fragment_n)
        candidate_tokens = EvidenceGuard._tokens(candidate_n)
        if not fragment_tokens:
            return False
        coverage = len(fragment_tokens & candidate_tokens) / len(fragment_tokens)
        return coverage >= 0.8 and len(fragment_tokens & candidate_tokens) >= min(3, len(fragment_tokens))

    def check_claim(self, claim: str) -> EvidenceCheck:
        if not claim or not claim.strip():
            return EvidenceCheck(False, [], "Afirmação vazia.", [claim])
        candidates = self._evidence_candidates()
        fragments = self._fragments(claim)
        supporting: list[str] = []
        unsupported: list[str] = []
        for fragment in fragments:
            sensitive = self._sensitive(fragment)
            matches = [
                evidence_id
                for evidence_id, evidence_text in candidates
                if self._candidate_supports(fragment, evidence_text, sensitive)
            ]
            if matches:
                supporting.extend(matches[:3])
            else:
                unsupported.append(fragment)
        if unsupported:
            return EvidenceCheck(
                False,
                list(dict.fromkeys(supporting)),
                "Afirmação bloqueada: um ou mais trechos não possuem evidência específica.",
                unsupported,
            )
        return EvidenceCheck(
            True,
            list(dict.fromkeys(supporting)),
            "Afirmação sustentada por fatos ou projetos atuais.",
            [],
        )

    def require_claims(self, claims: list[str]) -> dict[str, list[str]]:
        result: dict[str, list[str]] = {}
        for claim in claims:
            check = self.check_claim(claim)
            if not check.allowed:
                raise ValueError(
                    f"Afirmação sem evidência foi bloqueada: {claim!r}. "
                    f"Trechos: {', '.join(check.unsupported_fragments)}"
                )
            result[claim] = check.supporting_ids
        return result

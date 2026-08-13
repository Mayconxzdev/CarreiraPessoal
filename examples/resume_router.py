from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models import Job, JobMatch, ResumeVariant
from app.services.career_goal import CareerGoalService
from app.services.resume_service import ResumeService


@dataclass(slots=True)
class ResumeRouteDecision:
    action: str
    family: str
    reason: str
    router_score: int
    existing_resume_id: int | None = None

    def as_dict(self) -> dict:
        return asdict(self)


class ResumeFitnessGate:
    """Checks whether a generated resume is safe to present as 'ready'."""

    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings

    def evaluate(self, job: Job, match: JobMatch, resume: ResumeVariant) -> dict:
        report = dict(resume.validation_report or {})
        pages = int(report.get("pages") or 0)
        errors = list(report.get("errors") or [])
        warnings = list(report.get("warnings") or [])
        score = 0
        checks: dict[str, dict] = {}

        def add(key: str, passed: bool, points: int, detail: str):
            nonlocal score
            checks[key] = {"passed": passed, "points": points if passed else 0, "detail": detail}
            if passed:
                score += points

        add("ats", bool(resume.ats_validated and not errors), 28, "PDF legível e sem falhas rígidas de ATS.")
        add("one_page", pages == 1, 12, "Uma página." if pages == 1 else f"{pages or '—'} página(s); uma página é preferida.")
        add("snapshot", resume.job_snapshot_id == job.current_snapshot_id and resume.match_id == match.id, 15, "Gerado sobre a versão atual da vaga e da análise.")
        add("career_goal", match.career_goal_status in {"target", "adjacent"} and (match.career_goal_score or 0) >= self.settings.fast_lane_min_goal_score, 15, "Dentro da direção profissional priorizada.")
        add("fit", match.score >= self.settings.fast_lane_min_fit, 12, f"Aderência {match.score}/100.")
        add("critical_gaps", not bool(match.critical_gaps), 10, "Sem lacunas críticas." if not match.critical_gaps else "Existem lacunas críticas para revisão.")
        add("evidence", bool(resume.facts_used) and bool(resume.projects_used), 8, "Fatos e projetos comprovados foram selecionados.")

        if pages > 1:
            warnings.append("Fast Lane não marca como ideal um currículo de duas páginas quando uma página é viável.")
        status = "ready" if score >= self.settings.resume_fitness_ready_score and not errors and not match.critical_gaps else "review"
        if match.career_goal_status == "off_target":
            status = "blocked"
        result = {
            "score": min(100, score),
            "status": status,
            "checks": checks,
            "errors": errors,
            "warnings": list(dict.fromkeys(warnings)),
            "ready_threshold": self.settings.resume_fitness_ready_score,
        }
        resume.fitness_score = result["score"]
        resume.fitness_status = status
        resume.fitness_report = result
        return result


class ResumeRouterService:
    """Routes each vacancy to the best evidence-backed resume composition."""

    def __init__(self, db: Session, settings: Settings):
        self.db = db
        self.settings = settings
        self.resume_service = ResumeService(db, settings)
        self.goal = CareerGoalService(db)
        self.fitness = ResumeFitnessGate(db, settings)

    def _latest_match(self, job: Job) -> JobMatch | None:
        return self.db.scalar(
            select(JobMatch)
            .where(JobMatch.job_id == job.id, JobMatch.is_stale.is_(False))
            .order_by(JobMatch.created_at.desc())
            .limit(1)
        )

    def route(self, job: Job, *, match: JobMatch | None = None) -> ResumeRouteDecision:
        match = match or self._latest_match(job)
        if not match:
            raise ValueError("A vaga precisa de uma análise atual antes do roteamento de currículo.")
        goal = self.goal.evaluate(job, match)
        self.goal.persist(match, goal, commit=False)
        family = goal.family or self.resume_service._family(job)

        current = self.db.scalar(
            select(ResumeVariant)
            .where(
                ResumeVariant.job_id == job.id,
                ResumeVariant.match_id == match.id,
                ResumeVariant.job_snapshot_id == job.current_snapshot_id,
                ResumeVariant.is_stale.is_(False),
            )
            .order_by(ResumeVariant.created_at.desc())
            .limit(1)
        )
        if goal.status == "off_target":
            return ResumeRouteDecision("blocked", family, "A vaga foge da direção profissional priorizada; currículo não será preparado automaticamente.", max(0, goal.score), current.id if current else None)
        if match.score < self.settings.fast_lane_min_fit:
            return ResumeRouteDecision("review", family, f"Aderência {match.score}/100 abaixo do limite automático de {self.settings.fast_lane_min_fit}.", min(79, match.score), current.id if current else None)
        if match.opportunity_value is not None and match.opportunity_value < self.settings.fast_lane_min_opportunity_value:
            return ResumeRouteDecision("review", family, f"O valor da oportunidade ({match.opportunity_value}/100) ainda não justifica preparação automática.", min(79, match.opportunity_value), current.id if current else None)
        if goal.score < self.settings.fast_lane_min_goal_score:
            return ResumeRouteDecision("review", family, f"Direção profissional precisa de revisão ({goal.score}/100).", min(79, goal.score), current.id if current else None)
        if current and current.ats_validated and current.fitness_status == "ready":
            path = self.settings.resolve_data_path(current.pdf_path)
            if Path(path).exists():
                return ResumeRouteDecision("reuse", family, "A versão atual já corresponde à vaga, ao perfil e ao snapshot vigente.", 100, current.id)
        return ResumeRouteDecision("generate", family, f"{family} é a família mais adequada e será recomposta com as evidências mais relevantes desta vaga.", max(match.score, goal.score))

    def prepare(self, job: Job, *, match: JobMatch | None = None, force: bool = False) -> dict:
        match = match or self._latest_match(job)
        if not match:
            raise ValueError("A vaga precisa de aderência calculada antes do Fast Lane.")
        decision = self.route(job, match=match)
        if decision.action == "blocked":
            self.db.commit()
            return {"prepared": False, "decision": decision.as_dict(), "fitness": None, "resume_id": None}
        if decision.action == "review" and not force:
            self.db.commit()
            return {"prepared": False, "decision": decision.as_dict(), "fitness": None, "resume_id": decision.existing_resume_id}
        if decision.action == "reuse" and decision.existing_resume_id:
            resume = self.db.get(ResumeVariant, decision.existing_resume_id)
            fitness = self.fitness.evaluate(job, match, resume)
            resume.router_score = decision.router_score
            resume.route_reason = decision.reason
            self.db.commit()
            return {"prepared": fitness["status"] == "ready", "decision": decision.as_dict(), "fitness": fitness, "resume_id": resume.id}

        resume = self.resume_service.generate(job, route_reason=decision.reason)
        fitness = self.fitness.evaluate(job, match, resume)
        resume.router_score = decision.router_score
        resume.route_reason = decision.reason
        self.db.commit()
        return {"prepared": fitness["status"] == "ready", "decision": decision.as_dict(), "fitness": fitness, "resume_id": resume.id}

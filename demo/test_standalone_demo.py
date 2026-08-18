from __future__ import annotations

import unittest

from standalone_demo import (
    CareerPreferences,
    Evidence,
    Job,
    career_goal,
    evidence_guard,
    resume_route,
)


class StandaloneDemoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.preferences = CareerPreferences(
            preferred_roles=("Analista de Automação e Integrações",),
            preferred_families=("automação integrações",),
            excluded_focus=("vendas porta a porta",),
        )
        self.evidence = (
            Evidence("fact:automation", "Automação de processos com APIs REST, webhooks e Python."),
            Evidence("fact:deployment", "Implantação e sustentação de soluções internas."),
        )

    def test_target_job_advances(self) -> None:
        job = Job(
            "Analista Júnior de Automação e Integrações",
            "Automação de processos, APIs REST, webhooks e Python.",
            84,
            80,
        )
        decision = career_goal(job, self.preferences)
        self.assertEqual(decision.status, "target")
        self.assertGreaterEqual(decision.score, 72)

    def test_excluded_direction_is_blocked(self) -> None:
        job = Job(
            "Consultor de Vendas Porta a Porta",
            "Prospecção comercial e vendas porta a porta.",
            80,
            80,
        )
        decision = career_goal(job, self.preferences)
        self.assertEqual(decision.status, "off_target")
        route = resume_route(job, decision, evidence_ok=True)
        self.assertEqual(route.action, "blocked")

    def test_supported_claim_passes(self) -> None:
        decision = evidence_guard(
            "Automação de processos com APIs REST, webhooks e Python.",
            self.evidence,
        )
        self.assertTrue(decision.allowed)
        self.assertIn("fact:automation", decision.supporting_ids)

    def test_sensitive_unsupported_claim_is_rejected(self) -> None:
        decision = evidence_guard("Liderei 20 pessoas em produção.", self.evidence)
        self.assertFalse(decision.allowed)
        self.assertTrue(decision.unsupported_fragments)

    def test_ready_evidence_routes_to_generate(self) -> None:
        job = Job(
            "Analista de Automação e Integrações",
            "Automação, integrações e APIs REST.",
            81,
            77,
        )
        goal = career_goal(job, self.preferences)
        route = resume_route(job, goal, evidence_ok=True)
        self.assertEqual(route.action, "generate")

    def test_missing_evidence_requires_review(self) -> None:
        job = Job(
            "Analista de Automação e Integrações",
            "Automação, integrações e APIs REST.",
            81,
            77,
        )
        goal = career_goal(job, self.preferences)
        route = resume_route(job, goal, evidence_ok=False)
        self.assertEqual(route.action, "review")


if __name__ == "__main__":
    unittest.main()

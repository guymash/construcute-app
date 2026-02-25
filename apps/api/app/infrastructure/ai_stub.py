from __future__ import annotations

from app.application.ports.ai import AIClient


SAFETY_SUFFIX = (
    "\n\nThis assistant cannot provide construction instructions, measurements, "
    "or engineering advice. For safety or structural questions, consult a professional."
)


class StubAIClient(AIClient):
    def ask(
        self,
        *,
        question: str,
        project_context: str,
        stage_context: str | None,
    ) -> str:
        parts = [project_context]
        if stage_context:
            parts.append(stage_context)
        parts.append(f"Question: {question}")
        parts.append(
            "Short, simple-language explanation only. "
            "No measurements, no structural advice."
        )
        return " ".join(parts) + SAFETY_SUFFIX


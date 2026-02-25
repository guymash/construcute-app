from __future__ import annotations

from typing import Protocol


class AIClient(Protocol):
    def ask(
        self,
        *,
        question: str,
        project_context: str,
        stage_context: str | None,
    ) -> str: ...


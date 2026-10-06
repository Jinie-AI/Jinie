"""Module 02 adapter: turn raw customer input into Jinie's canonical brief."""

from modules.engine.brief import normalize_brief


class EngineReframer:
    def reframe_input(self, raw_prompt: str) -> str:
        if not raw_prompt or not raw_prompt.strip():
            raise ValueError("Prompt cannot be empty")
        return normalize_brief(raw_prompt)


def reframe_input(raw_prompt: str) -> str:
    return EngineReframer().reframe_input(raw_prompt)

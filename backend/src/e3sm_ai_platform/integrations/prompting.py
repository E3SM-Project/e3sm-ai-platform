"""Provider-neutral prompt construction shared by every LLM integration.

Keeping the system prompt, the evidence formatting, and the context bound in
one place means the evidence-first wording cannot drift between providers. A
provider module owns only the transport to its gateway; it never decides what
the model is asked.
"""

from __future__ import annotations

from typing import Protocol

from e3sm_ai_platform.domain.models import Evidence

# Deterministic context bound so prompts cannot grow without limit as corpus/retrieval expands.
MAX_EVIDENCE_PROMPT_CHARS = 8_000
SYSTEM_PROMPT = (
    "You are E3SM Compass. Answer only from the provided E3SM evidence. "
    "Do not add claims beyond the sources. If the evidence is insufficient, say so. "
    "Do not invent citations; the server attaches citations separately."
)


class ChatClient(Protocol):
    """Small provider-independent chat completion boundary."""

    def complete(self, messages: list[dict[str, str]]) -> str:
        """Return assistant text for chat messages."""


def build_messages(question: str, evidence: list[Evidence]) -> list[dict[str, str]]:
    """Build a source-constrained system/user message pair from accepted evidence."""
    evidence_text = truncate_prompt_context(
        "\n\n".join(
            f"Source {index}: {item.source.source_id}\n"
            f"Title: {item.source.title}\n"
            f"Section: {item.source.section}\n"
            f"Provenance: {item.source.provenance}\n"
            f"Text: {item.text}"
            for index, item in enumerate(evidence, start=1)
        )
    )
    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": f"Question: {question}\n\nAccepted E3SM evidence:\n{evidence_text}",
        },
    ]


def truncate_prompt_context(text: str) -> str:
    """Cut evidence context at the configured bound with an explicit marker."""
    if len(text) <= MAX_EVIDENCE_PROMPT_CHARS:
        return text
    suffix = "\n[Evidence context truncated deterministically at configured character limit.]"
    return text[: MAX_EVIDENCE_PROMPT_CHARS - len(suffix)].rstrip() + suffix

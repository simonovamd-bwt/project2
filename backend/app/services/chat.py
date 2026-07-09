"""Mock conversational "AI" for guided document drafting (issue #2).

There is intentionally **no** LLM call here — no Anthropic, no external API.
The service emulates the shape a real structured-output model would return:
given the answers collected so far, it decides the next question to ask (or
that the interview is complete) and rebuilds a live markdown preview.

The contract mirrors the issue's "one non-streaming call, structured output"
design: a single call returns both the chat reply and the extracted document
fields, so the frontend can drive the chat and a live preview from one response.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# The ordered interview. Each step maps one answer onto a document field.
# Keeping this a plain list makes "3-4 hard-coded questions" explicit and easy
# to test, and trivial to swap for a real prompt later.
QUESTIONS: list[dict[str, str]] = [
    {
        "field": "disclosing_party",
        "question": "Вітаю! Я допоможу скласти угоду про нерозголошення (NDA). "
        "Хто є стороною, що розкриває інформацію (Disclosing Party)?",
    },
    {
        "field": "receiving_party",
        "question": "Дякую. Хто є стороною, що отримує інформацію (Receiving Party)?",
    },
    {
        "field": "purpose",
        "question": "Зрозуміло. Яка мета обміну конфіденційною інформацією?",
    },
    {
        "field": "term_months",
        "question": "Останнє: на який строк діє зобовʼязання про "
        "конфіденційність (у місяцях)?",
    },
]

GREETING_FIELD = QUESTIONS[0]["field"]
DEFAULT_DOCUMENT_TYPE = "Mutual NDA"

# Ordered field list, used both to validate answers and to build the preview.
FIELDS: list[str] = [q["field"] for q in QUESTIONS]

# Human-readable labels for the live preview.
FIELD_LABELS: dict[str, str] = {
    "disclosing_party": "Disclosing Party",
    "receiving_party": "Receiving Party",
    "purpose": "Purpose",
    "term_months": "Term (months)",
}


@dataclass
class ChatTurn:
    """The single structured response the mock 'model' returns per turn."""

    reply: str
    next_field: str | None
    complete: bool
    fields: dict[str, str]
    document_type: str = DEFAULT_DOCUMENT_TYPE
    title: str = ""
    markdown: str = ""
    # Extra metadata a real structured output would not need, but handy for UI.
    total_questions: int = field(default=len(QUESTIONS))
    answered: int = 0


def _clean(answers: dict[str, str]) -> dict[str, str]:
    """Keep only known fields with non-empty, stripped string values."""
    cleaned: dict[str, str] = {}
    for key in FIELDS:
        value = answers.get(key)
        if isinstance(value, str) and value.strip():
            cleaned[key] = value.strip()
    return cleaned


def _next_unanswered(answers: dict[str, str]) -> dict[str, str] | None:
    """The first question whose field has no answer yet, or None if done."""
    for q in QUESTIONS:
        if q["field"] not in answers:
            return q
    return None


def build_preview(answers: dict[str, str]) -> str:
    """Render a live markdown preview from the answers gathered so far.

    Unanswered fields show a placeholder so the preview updates in step with
    the conversation rather than appearing only at the end.
    """
    disclosing = answers.get("disclosing_party", "________")
    receiving = answers.get("receiving_party", "________")
    purpose = answers.get("purpose", "________")
    term = answers.get("term_months", "____")

    return (
        "# Mutual Non-Disclosure Agreement\n\n"
        f"This Mutual Non-Disclosure Agreement is entered into between "
        f"**{disclosing}** (\"Disclosing Party\") and **{receiving}** "
        f'("Receiving Party").\n\n'
        "## 1. Purpose\n\n"
        f"The parties wish to exchange confidential information for the purpose "
        f"of **{purpose}**.\n\n"
        "## 2. Confidentiality\n\n"
        "Each party agrees to keep the other party's confidential information "
        "in strict confidence and not to disclose it to any third party.\n\n"
        "## 3. Term\n\n"
        f"The confidentiality obligations under this Agreement remain in effect "
        f"for **{term} months** from the date of signing.\n\n"
        "## 4. Legal review\n\n"
        "_This document is a draft and is subject to legal review. "
        "It is not legal advice._\n"
    )


def _title_for(answers: dict[str, str]) -> str:
    disclosing = answers.get("disclosing_party")
    receiving = answers.get("receiving_party")
    if disclosing and receiving:
        return f"NDA — {disclosing} & {receiving}"
    if disclosing:
        return f"NDA — {disclosing}"
    return "NDA (draft)"


def advance(answers: dict[str, str]) -> ChatTurn:
    """Compute the next chat turn from the answers collected so far.

    Stateless: the frontend sends the full answer map each turn and gets back
    the next question (or a completion), plus the live preview — a single
    structured response, exactly as the issue's non-streaming design requires.
    """
    cleaned = _clean(answers)
    preview = build_preview(cleaned)
    title = _title_for(cleaned)
    pending = _next_unanswered(cleaned)

    if pending is None:
        return ChatTurn(
            reply="Дякую! Я зібрав усі відповіді. Ваш чернетковий NDA готовий — "
            "перегляньте прев’ю праворуч і завантажте PDF.",
            next_field=None,
            complete=True,
            fields=cleaned,
            title=title,
            markdown=preview,
            answered=len(cleaned),
        )

    return ChatTurn(
        reply=pending["question"],
        next_field=pending["field"],
        complete=False,
        fields=cleaned,
        title=title,
        markdown=preview,
        answered=len(cleaned),
    )

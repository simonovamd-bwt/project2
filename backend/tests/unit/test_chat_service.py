"""Unit tests for the mock chat service (issue #2).

These lock in the deterministic interview logic without any LLM or HTTP layer.
"""

from app.services.chat import (
    FIELDS,
    QUESTIONS,
    advance,
    build_preview,
)


def test_greeting_is_first_question_when_no_answers():
    turn = advance({})
    assert turn.complete is False
    assert turn.answered == 0
    # The mock "AI" opens the conversation itself with the first question.
    assert turn.next_field == QUESTIONS[0]["field"]
    assert "NDA" in turn.reply


def test_there_are_between_three_and_four_questions():
    # The issue asks for 3-4 hard-coded questions.
    assert 3 <= len(QUESTIONS) <= 4


def test_questions_are_asked_in_order():
    answers: dict[str, str] = {}
    for expected in QUESTIONS:
        turn = advance(answers)
        assert turn.next_field == expected["field"]
        # Answer it and move on.
        answers[expected["field"]] = "some value"
    # After all are answered, the interview is complete.
    final = advance(answers)
    assert final.complete is True
    assert final.next_field is None


def test_complete_turn_returns_all_fields_and_markdown():
    answers = {
        "disclosing_party": "Acme Inc",
        "receiving_party": "Beta LLC",
        "purpose": "evaluating a partnership",
        "term_months": "24",
    }
    turn = advance(answers)
    assert turn.complete is True
    assert turn.fields == answers
    assert turn.answered == 4
    # The generated document embeds every collected answer.
    for value in answers.values():
        assert value in turn.markdown
    assert turn.title == "NDA — Acme Inc & Beta LLC"


def test_partial_answers_advance_to_the_next_unanswered_field():
    turn = advance({"disclosing_party": "Acme Inc"})
    assert turn.complete is False
    assert turn.next_field == "receiving_party"
    assert turn.answered == 1


def test_blank_and_unknown_answers_are_ignored():
    # Empty strings don't count as answered; unknown keys are dropped.
    turn = advance({"disclosing_party": "   ", "bogus": "x"})
    assert turn.answered == 0
    assert turn.next_field == "disclosing_party"
    assert "bogus" not in turn.fields


def test_answers_are_stripped():
    turn = advance({"disclosing_party": "  Acme Inc  "})
    assert turn.fields["disclosing_party"] == "Acme Inc"


def test_preview_shows_placeholders_before_answers():
    preview = build_preview({})
    assert "________" in preview  # unanswered party placeholder
    assert "Non-Disclosure Agreement" in preview
    # The draft/legal-review caveat is always present in the document body.
    assert "subject to legal review" in preview


def test_preview_updates_live_as_answers_arrive():
    empty = build_preview({})
    partial = build_preview({"disclosing_party": "Acme Inc"})
    assert "Acme Inc" not in empty
    assert "Acme Inc" in partial


def test_all_fields_have_labels_and_questions_align():
    from app.services.chat import FIELD_LABELS

    assert [q["field"] for q in QUESTIONS] == FIELDS
    assert set(FIELD_LABELS) == set(FIELDS)

"""Integration tests for the mock AI chat endpoint (issue #2)."""


def test_chat_opens_with_the_first_question(client):
    # Empty answers -> the AI greets and asks the first question, unauthenticated
    # (freemium: drafting via chat needs no login).
    res = client.post("/api/chat", json={"answers": {}})
    assert res.status_code == 200
    body = res.json()
    assert body["complete"] is False
    assert body["next_field"] == "disclosing_party"
    assert body["answered"] == 0
    assert body["total_questions"] >= 3
    assert "markdown" in body and body["markdown"]


def test_chat_is_public_no_auth_required(client):
    # No session cookie set; must still work.
    assert client.post("/api/chat", json={"answers": {}}).status_code == 200


def test_chat_walks_through_all_questions_to_completion(client):
    answers: dict[str, str] = {}
    fields_seen = []
    for _ in range(10):  # safety bound
        res = client.post("/api/chat", json={"answers": answers})
        body = res.json()
        if body["complete"]:
            break
        field = body["next_field"]
        fields_seen.append(field)
        answers[field] = "value"
    else:
        raise AssertionError("chat never completed")

    final = client.post("/api/chat", json={"answers": answers}).json()
    assert final["complete"] is True
    assert final["next_field"] is None
    assert final["answered"] == len(fields_seen)


def test_chat_returns_structured_fields_and_live_preview(client):
    answers = {
        "disclosing_party": "Acme Inc",
        "receiving_party": "Beta LLC",
        "purpose": "evaluating a partnership",
        "term_months": "24",
    }
    body = client.post("/api/chat", json={"answers": answers}).json()
    assert body["complete"] is True
    assert body["fields"] == answers
    assert body["document_type"] == "Mutual NDA"
    # Live preview embeds the collected answers.
    for value in answers.values():
        assert value in body["markdown"]


def test_chat_preview_updates_with_partial_answers(client):
    body = client.post(
        "/api/chat", json={"answers": {"disclosing_party": "Acme Inc"}}
    ).json()
    assert body["complete"] is False
    assert body["next_field"] == "receiving_party"
    assert "Acme Inc" in body["markdown"]


def test_chat_defaults_to_empty_answers_when_omitted(client):
    # answers is optional; omitting it is treated as a fresh conversation.
    res = client.post("/api/chat", json={})
    assert res.status_code == 200
    assert res.json()["answered"] == 0


def test_chat_completed_document_can_be_saved_when_authenticated(client):
    from tests.conftest import register

    # Drive the chat to completion (public), then persist via authed documents API.
    answers = {
        "disclosing_party": "Acme Inc",
        "receiving_party": "Beta LLC",
        "purpose": "a deal",
        "term_months": "12",
    }
    turn = client.post("/api/chat", json={"answers": answers}).json()
    assert turn["complete"] is True

    register(client)
    created = client.post(
        "/api/documents",
        json={
            "title": turn["title"],
            "document_type": turn["document_type"],
            "form_values": turn["fields"],
            "markdown": turn["markdown"],
        },
    )
    assert created.status_code == 201
    assert created.json()["markdown"] == turn["markdown"]

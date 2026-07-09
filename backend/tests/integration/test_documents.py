"""Integration tests for document history: create, list, fetch, isolation."""

from tests.conftest import register

DOC_PAYLOAD = {
    "title": "NDA with Acme",
    "document_type": "Mutual NDA",
    "form_values": {"company": "Acme"},
    "markdown": "# NDA\n\nContent here",
}


def test_documents_require_authentication(client):
    assert client.get("/api/documents").status_code == 401
    assert client.post("/api/documents", json=DOC_PAYLOAD).status_code == 401


def test_create_then_list_and_fetch(client):
    register(client)

    created = client.post("/api/documents", json=DOC_PAYLOAD)
    assert created.status_code == 201
    body = created.json()
    assert body["title"] == "NDA with Acme"
    assert body["form_values"] == {"company": "Acme"}
    assert body["markdown"] == "# NDA\n\nContent here"

    listed = client.get("/api/documents")
    assert listed.status_code == 200
    summaries = listed.json()
    assert len(summaries) == 1
    assert summaries[0]["id"] == body["id"]
    # The list view is a summary — no markdown/form_values payload.
    assert "markdown" not in summaries[0]
    assert "form_values" not in summaries[0]

    fetched = client.get(f"/api/documents/{body['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == body


def test_create_uses_defaults_when_optional_fields_omitted(client):
    register(client)

    created = client.post(
        "/api/documents", json={"title": "Minimal doc", "markdown": "# Minimal"}
    )
    assert created.status_code == 201
    body = created.json()
    assert body["document_type"] == "Mutual NDA"
    assert body["form_values"] == {}


def test_list_is_newest_first(client):
    register(client)

    first = client.post(
        "/api/documents", json={**DOC_PAYLOAD, "title": "First doc"}
    ).json()
    second = client.post(
        "/api/documents", json={**DOC_PAYLOAD, "title": "Second doc"}
    ).json()
    third = client.post(
        "/api/documents", json={**DOC_PAYLOAD, "title": "Third doc"}
    ).json()

    listed = client.get("/api/documents").json()
    assert [d["id"] for d in listed] == [third["id"], second["id"], first["id"]]


def test_history_is_isolated_between_users(client):
    register(client, "alice", "secret1")
    client.post("/api/documents", json={**DOC_PAYLOAD, "title": "Alice doc"})
    client.post("/api/auth/logout")

    register(client, "bob", "secret1")
    bob_list = client.get("/api/documents")
    assert bob_list.status_code == 200
    assert bob_list.json() == []

    client.post("/api/documents", json={**DOC_PAYLOAD, "title": "Bob doc"})
    bob_list = client.get("/api/documents")
    assert len(bob_list.json()) == 1
    assert bob_list.json()[0]["title"] == "Bob doc"


def test_get_other_users_document_returns_404_not_403(client):
    register(client, "alice", "secret1")
    alice_doc = client.post("/api/documents", json=DOC_PAYLOAD).json()
    client.post("/api/auth/logout")

    register(client, "bob", "secret1")
    res = client.get(f"/api/documents/{alice_doc['id']}")
    assert res.status_code == 404


def test_get_nonexistent_document_returns_404(client):
    register(client)
    res = client.get("/api/documents/999999")
    assert res.status_code == 404

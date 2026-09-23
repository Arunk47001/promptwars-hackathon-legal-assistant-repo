import io


def _upload(client, filename="a.pdf"):
    file_content = io.BytesIO(b"placeholder")
    resp = client.post(
        "/documents",
        files={"file": (filename, file_content, "application/pdf")},
    )
    return resp.json()["id"]


def test_compare_two_documents_flags_differences(client):
    from app.storage import store

    doc_a = _upload(client, "a.pdf")
    doc_b = _upload(client, "b.pdf")

    store.documents[doc_a].masked_text = (
        "security deposit of 10 months rent. tenant must give 3 months notice. "
        "landlord must give 1 month notice. lock-in for 11 months."
    )
    store.documents[doc_b].masked_text = (
        "security deposit of 2 months rent. tenant must give 1 months notice. "
        "landlord must give 1 month notice. lock-in for 6 months."
    )

    resp = client.post(
        "/actions/compare",
        json={"document_id_a": doc_a, "document_id_b": doc_b},
    )
    assert resp.status_code == 200
    data = resp.json()
    diffs_by_field = {d["field"]: d for d in data["diffs"]}
    assert diffs_by_field["security_deposit_months"]["differs"] is True
    assert diffs_by_field["security_deposit_months"]["value_a"] == "10"
    assert diffs_by_field["security_deposit_months"]["value_b"] == "2"
    assert diffs_by_field["lock_in_months"]["differs"] is True


def test_compare_missing_document_returns_404(client):
    resp = client.post(
        "/actions/compare",
        json={"document_id_a": "nonexistent-a", "document_id_b": "nonexistent-b"},
    )
    assert resp.status_code == 404


def test_law_mapping_ipc_to_bns(client):
    resp = client.get("/actions/law-mapping", params={"section": "302", "code": "IPC"})
    assert resp.status_code == 200
    data = resp.json()
    assert any(r["new_code"] == "BNS" and r["new_section"] == "103" for r in data["results"])


def test_law_mapping_bns_to_ipc_reverse(client):
    resp = client.get("/actions/law-mapping", params={"section": "103", "code": "BNS"})
    assert resp.status_code == 200
    data = resp.json()
    assert any(r["old_code"] == "IPC" and r["old_section"] == "302" for r in data["results"])


def test_law_mapping_works_without_any_document_uploaded(client):
    # No /documents call made in this test at all.
    resp = client.get("/actions/law-mapping", params={"section": "154", "code": "CrPC"})
    assert resp.status_code == 200
    assert resp.json()["results"]


def test_navigator_playbooks_listed(client):
    resp = client.get("/actions/navigator/playbooks")
    assert resp.status_code == 200
    ids = {p["id"] for p in resp.json()}
    assert "deposit_not_returned" in ids
    assert len(ids) >= 2


def test_navigator_deposit_not_returned_playbook(client):
    resp = client.post(
        "/actions/navigator/deposit_not_returned",
        json={
            "tenant_name": "Asha Rao",
            "landlord_name": "Mr. Gowda",
            "property_address": "123 Koramangala",
            "deposit_amount": "150000",
            "vacate_date": "2026-01-15",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "Asha Rao" in data["draft"]
    assert data["required_documents"]
    assert data["forum"]


def test_navigator_unknown_playbook_404(client):
    resp = client.post("/actions/navigator/does_not_exist", json={})
    assert resp.status_code == 404


def test_sessions_create_and_get(client):
    resp = client.post("/sessions")
    assert resp.status_code == 201
    session_id = resp.json()["id"]

    resp2 = client.get(f"/sessions/{session_id}")
    assert resp2.status_code == 200
    assert resp2.json()["document_ids"] == []

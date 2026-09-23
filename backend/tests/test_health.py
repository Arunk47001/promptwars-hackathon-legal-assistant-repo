def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_openapi_docs_render(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    paths = schema["paths"]
    assert "/health" in paths
    assert "/documents" in paths
    assert "/sessions" in paths
    assert any(p.startswith("/actions") for p in paths)

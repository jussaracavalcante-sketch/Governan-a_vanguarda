"""Testes smoke da API VANGUARDIAN."""
from fastapi.testclient import TestClient

from main import app


def test_root_endpoint():
    # O context manager dispara o lifespan (cria tabelas + seed).
    with TestClient(app) as client:
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert "app" in body
        assert body["docs"] == "/docs"


def test_health_live():
    with TestClient(app) as client:
        resp = client.get("/health/live")
        assert resp.status_code == 200


def test_prompts_requires_auth():
    # Sem token, o endpoint protegido deve negar o acesso.
    with TestClient(app) as client:
        resp = client.get("/prompts")
        assert resp.status_code in (401, 403)

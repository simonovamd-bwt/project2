"""Tests for the SPA static-file fallback that serves the Next.js export."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import _mount_frontend


def _build_app(frontend_dir, monkeypatch):
    monkeypatch.setattr("app.main.settings.frontend_dir", frontend_dir)
    app = FastAPI()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    _mount_frontend(app)
    return TestClient(app)


def test_skips_mounting_when_index_html_is_missing(tmp_path, monkeypatch):
    client = _build_app(tmp_path, monkeypatch)
    assert client.get("/anything").status_code == 404


def test_serves_index_html_at_root(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<html>home</html>")
    client = _build_app(tmp_path, monkeypatch)

    res = client.get("/")
    assert res.status_code == 200
    assert res.text == "<html>home</html>"


def test_serves_existing_static_asset_directly(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<html>home</html>")
    assets_dir = tmp_path / "_next" / "static"
    assets_dir.mkdir(parents=True)
    (assets_dir / "app.js").write_text("console.log('hi')")
    client = _build_app(tmp_path, monkeypatch)

    res = client.get("/_next/static/app.js")
    assert res.status_code == 200
    assert res.text == "console.log('hi')"


def test_falls_back_to_index_html_for_unknown_client_routes(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<html>home</html>")
    client = _build_app(tmp_path, monkeypatch)

    res = client.get("/documents/42")
    assert res.status_code == 200
    assert res.text == "<html>home</html>"


def test_does_not_shadow_api_or_health_routes(tmp_path, monkeypatch):
    (tmp_path / "index.html").write_text("<html>home</html>")
    client = _build_app(tmp_path, monkeypatch)

    assert client.get("/health").status_code == 200
    assert client.get("/api/whatever").status_code == 404

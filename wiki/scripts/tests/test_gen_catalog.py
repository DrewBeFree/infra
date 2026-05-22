import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_catalog  # noqa: E402

import json


def _make_repo(base: Path, sub: str, name: str):
    d = base / sub / name
    (d / ".git").mkdir(parents=True)
    return d


def test_scan_repos_finds_git_repos_by_type(tmp_path):
    _make_repo(tmp_path, "apps", "golf")
    _make_repo(tmp_path, "agents", "bob")
    (tmp_path / "apps" / "not-a-repo").mkdir()  # no .git -> ignored

    repos = gen_catalog.scan_repos(tmp_path)

    assert {"name": "golf", "type": "app", "path": "apps/golf"} in repos
    assert {"name": "bob", "type": "agent", "path": "agents/bob"} in repos
    assert all(r["name"] != "not-a-repo" for r in repos)


def test_load_manifest_keys_by_name(tmp_path):
    p = tmp_path / "repos.json"
    p.write_text(json.dumps({"repositories": [
        {"name": "golf", "github": "https://github.com/DrewBeFree/golf.git", "type": "app"},
    ]}), encoding="utf-8")

    manifest = gen_catalog.load_manifest(p)

    assert manifest["golf"]["github"] == "https://github.com/DrewBeFree/golf.git"


def test_load_manifest_missing_file_returns_empty(tmp_path):
    assert gen_catalog.load_manifest(tmp_path / "nope.json") == {}


def test_load_card_map(tmp_path):
    p = tmp_path / "card_map.json"
    p.write_text(json.dumps({"golf": "APP_003"}), encoding="utf-8")

    assert gen_catalog.load_card_map(p) == {"golf": "APP_003"}


def test_load_card_map_missing_file_returns_empty(tmp_path):
    assert gen_catalog.load_card_map(tmp_path / "nope.json") == {}


CARD_HTML = """
<a class="card" href="https://linksy.drewbefree.com">
  <div class="card-id">APP_003 // UTILITY</div>
  <div class="card-name">LINKSY</div>
  <div class="card-url">linksy.drewbefree.com</div>
  <div class="card-desc">Live wager tracker for golf.</div>
  <div class="card-footer"><span class="card-meta">v0.2.2 · 2026-05-10</span></div>
</a>
<a class="card" href="https://kybernet.tech">
  <div class="card-id">SITE_002 // NETWORKING</div>
  <div class="card-name">KYBERNET</div>
  <div class="card-url">kybernet.tech</div>
  <div class="card-desc">UniFi network design.</div>
  <div class="card-footer"><span class="card-meta live">LIVE</span></div>
</a>
"""


def test_parse_command_center_app_card(tmp_path):
    p = tmp_path / "index.html"
    p.write_text(CARD_HTML, encoding="utf-8")

    cards = gen_catalog.parse_command_center(p)

    assert cards["APP_003"]["version"] == "0.2.2"
    assert cards["APP_003"]["date"] == "2026-05-10"
    assert cards["APP_003"]["status"] == "active"
    assert cards["APP_003"]["display_name"] == "LINKSY"
    assert cards["APP_003"]["url"] == "linksy.drewbefree.com"
    assert cards["APP_003"]["description"] == "Live wager tracker for golf."


def test_parse_command_center_live_site_card(tmp_path):
    p = tmp_path / "index.html"
    p.write_text(CARD_HTML, encoding="utf-8")

    cards = gen_catalog.parse_command_center(p)

    assert cards["SITE_002"]["status"] == "live"
    assert cards["SITE_002"]["version"] is None


def test_parse_command_center_missing_file_returns_empty(tmp_path):
    assert gen_catalog.parse_command_center(tmp_path / "nope.html") == {}


def test_read_description_returns_first_paragraph(tmp_path):
    repo = tmp_path / "golf"
    repo.mkdir()
    (repo / "README.md").write_text("# Golf\n\n![badge](x.png)\n\nA wager tracker.\n", encoding="utf-8")

    assert gen_catalog.read_description(repo) == "A wager tracker."


def test_read_description_no_readme_returns_empty(tmp_path):
    repo = tmp_path / "golf"
    repo.mkdir()

    assert gen_catalog.read_description(repo) == ""


def test_github_web_url_strips_dot_git():
    assert gen_catalog.github_web_url("https://github.com/DrewBeFree/golf.git") == "https://github.com/DrewBeFree/golf"
    assert gen_catalog.github_web_url(None) is None


def test_enrich_mapped_repo_pulls_card_data(tmp_path):
    repo_dir = _make_repo(tmp_path, "apps", "golf")
    (repo_dir / "README.md").write_text("# Golf\n\nReadme desc.\n", encoding="utf-8")
    repos = gen_catalog.scan_repos(tmp_path)
    manifest = {"golf": {"github": "https://github.com/DrewBeFree/golf.git", "type": "app"}}
    cards = {"APP_003": {"display_name": "LINKSY", "url": "linksy.drewbefree.com",
                         "description": "Card desc.", "version": "0.2.2",
                         "date": "2026-05-10", "status": "active"}}
    card_map = {"golf": "APP_003"}

    out = gen_catalog.enrich(repos, manifest, cards, card_map, tmp_path)
    golf = next(p for p in out if p["name"] == "golf")

    assert golf["display_name"] == "LINKSY"
    assert golf["version"] == "0.2.2"
    assert golf["status"] == "active"
    assert golf["github"] == "https://github.com/DrewBeFree/golf.git"
    assert golf["in_manifest"] is True
    assert golf["description"] == "Card desc."  # card wins over README


def test_enrich_unmapped_repo_falls_back(tmp_path):
    repo_dir = _make_repo(tmp_path, "agents", "bob")
    (repo_dir / "README.md").write_text("# Bob\n\nA Discord bot.\n", encoding="utf-8")
    repos = gen_catalog.scan_repos(tmp_path)

    out = gen_catalog.enrich(repos, {}, {}, {}, tmp_path)
    bob = next(p for p in out if p["name"] == "bob")

    assert bob["display_name"] == "bob"
    assert bob["version"] is None
    assert bob["status"] is None
    assert bob["github"] is None
    assert bob["in_manifest"] is False
    assert bob["description"] == "A Discord bot."


def test_detect_drift_reports_both_directions(tmp_path):
    _make_repo(tmp_path, "agents", "bob")  # on disk, not in manifest
    repos = gen_catalog.scan_repos(tmp_path)
    manifest = {
        "ghost": {"targetDirectory": "apps/ghost", "type": "app"},  # in manifest, not on disk
        "infra": {"targetDirectory": "infra", "type": "infra"},     # not a scan dir -> ignored
    }

    warnings = gen_catalog.detect_drift(repos, manifest, tmp_path)
    joined = "\n".join(warnings)

    assert "bob" in joined
    assert "ghost" in joined
    assert "infra" not in joined


def _sample_project(**over):
    base = {"name": "golf", "type": "app", "path": "apps/golf",
            "github": "https://github.com/DrewBeFree/golf.git", "in_manifest": True,
            "display_name": "LINKSY", "version": "0.2.2", "date": "2026-05-10",
            "status": "active", "url": "linksy.drewbefree.com", "description": "Wager tracker."}
    base.update(over)
    return base


def test_render_index_has_row_and_link(tmp_path):
    md = gen_catalog.render_index([_sample_project()])

    assert "| Project | Type | Version | Status | Repo |" in md
    assert "[LINKSY](golf.md)" in md
    assert "v0.2.2" in md
    assert "https://github.com/DrewBeFree/golf" in md


def test_render_index_blank_fields_use_dash():
    md = gen_catalog.render_index([_sample_project(version=None, status=None, github=None)])

    assert "| — |" in md  # at least one em-dash cell


def test_render_project_page_includes_fields():
    md = gen_catalog.render_project_page(_sample_project())

    assert md.startswith("# LINKSY")
    assert "Wager tracker." in md
    assert "v0.2.2" in md
    assert "linksy.drewbefree.com" in md
    assert "`apps/golf`" in md
    assert "https://github.com/DrewBeFree/golf" in md

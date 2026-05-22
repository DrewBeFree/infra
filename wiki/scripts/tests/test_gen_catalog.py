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

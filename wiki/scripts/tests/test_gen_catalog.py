import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gen_catalog  # noqa: E402


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

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import ecosystem_task_sync as sync


class EcosystemTaskSyncTests(unittest.TestCase):
    def test_collect_routes_tasks_to_owning_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "apps" / "poker").mkdir(parents=True)
            (root / "infra").mkdir()
            (root / "apps" / "poker" / "BACKLOG.md").write_text(
                "## Backlog\n\n- [ ] **Fix table stakes**\n",
                encoding="utf-8",
            )
            (root / "infra" / "repos.json").write_text(
                '{"repositories":[{"name":"poker","github":"https://github.com/DrewBeFree/poker.git","targetDirectory":"apps/poker","type":"app"}]}',
                encoding="utf-8",
            )
            (root / "infra" / "ecosystem.json").write_text(
                '{"repositories":[{"name":"poker","displayName":"Poker Night","localPath":"' + str(root / "apps" / "poker").replace("\\", "\\\\") + '","githubUrl":"https://github.com/DrewBeFree/poker"}]}',
                encoding="utf-8",
            )

            tasks = sync.collect_tasks(root, root / "infra" / "repos.json", root / "infra" / "ecosystem.json")

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].project, "Poker Night")
        self.assertEqual(tasks[0].repo_full_name, "DrewBeFree/poker")
        self.assertEqual(tasks[0].area, "apps")

    def test_plan_leantime_updates_existing_broad_bucket_task_to_repo_project(self):
        task = sync.Task(
            stable_id="task-abc123def456",
            title="Fix table stakes",
            project="Poker Night",
            area="apps",
            status="Backlog",
            priority="Normal",
            source_file="apps/poker/BACKLOG.md",
            source_line=3,
            section="Backlog",
            description="",
            repo_name="poker",
            repo_full_name="DrewBeFree/poker",
            repo_path="apps/poker",
            repo_type="app",
        )
        existing = [{
            "id": 99,
            "headline": "Fix table stakes",
            "description": "task-sync-id: task-abc123def456",
            "projectId": 4,
        }]
        actions = sync.plan_leantime([task], {"Poker Night": {"id": 12}}, existing)

        self.assertEqual(actions[0].action, "update")
        self.assertEqual(actions[0].project_id, 12)
        self.assertEqual(actions[0].ticket_id, 99)

    def test_plan_github_issue_create_update_skip(self):
        task = sync.Task(
            stable_id="task-abc123def456",
            title="Fix table stakes",
            project="Poker Night",
            area="apps",
            status="Backlog",
            priority="Normal",
            source_file="apps/poker/BACKLOG.md",
            source_line=3,
            section="Backlog",
            description="",
            repo_name="poker",
            repo_full_name="DrewBeFree/poker",
            repo_path="apps/poker",
            repo_type="app",
        )

        self.assertEqual(sync.plan_issues([task], {"DrewBeFree/poker": []})[0].action, "create")
        drifted = [{"number": 5, "title": "Old", "body": "task-sync-id: task-abc123def456", "state": "open"}]
        self.assertEqual(sync.plan_issues([task], {"DrewBeFree/poker": drifted})[0].action, "update")
        current = [{"number": 5, "title": task.title, "body": sync.render_github_body(task), "state": "open"}]
        self.assertEqual(sync.plan_issues([task], {"DrewBeFree/poker": current})[0].action, "skip")


if __name__ == "__main__":
    unittest.main()

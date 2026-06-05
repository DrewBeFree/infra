import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))

import task_sync


class TaskSyncTests(unittest.TestCase):
    def make_task(self, **overrides):
        values = {
            'stable_id': 'task-abc123def456',
            'title': 'Atlas safety dashboard + Hermes handoff lane',
            'project': 'Atlas / Infra',
            'area': 'infra',
            'status': 'Blocked',
            'priority': 'High',
            'source_file': 'infra/BACKLOG.md',
            'source_line': 105,
            'section': 'Blocked / Ready',
            'description': '- Surface offline `/mnt/data4`',
        }
        values.update(overrides)
        return task_sync.Task(**values)

    def test_parse_backlog_task_with_nested_description(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            backlog = root / 'BACKLOG.md'
            backlog.write_text(
                '# Backlog\n\n'
                '## Blocked / Ready\n\n'
                '- [ ] **Atlas safety dashboard + Hermes handoff lane**\n'
                '  - Surface offline `/mnt/data4`\n'
                '  - Reference: `docs/runbook.md`\n\n'
                '- [x] Done thing\n',
                encoding='utf-8',
            )
            tasks = task_sync.parse_markdown(backlog, root)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].title, 'Atlas safety dashboard + Hermes handoff lane')
        self.assertEqual(tasks[0].project, 'Atlas / Infra')
        self.assertEqual(tasks[0].status, 'Blocked')
        self.assertEqual(tasks[0].priority, 'High')
        self.assertIn('Surface offline', tasks[0].description)

    def test_clean_markdown_strips_inline_bold_markup(self):
        self.assertEqual(
            task_sync.clean_markdown('**Custom System Prompts**: Allow overrides.'),
            'Custom System Prompts: Allow overrides.',
        )

    def test_exports_include_github_and_leantime_shapes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'BACKLOG.md').write_text('## In Progress\n\n- [ ] **Sync GitHub Projects with Leantime**\n', encoding='utf-8')
            out = root / 'out'
            tasks = task_sync.collect(root)
            task_sync.write_exports(tasks, out)
            self.assertTrue((out / 'tasks.json').exists())
            self.assertTrue((out / 'github-issues.json').exists())
            self.assertTrue((out / 'leantime-import.csv').exists())
            self.assertIn('Sync GitHub Projects with Leantime', (out / 'tasks.md').read_text(encoding='utf-8'))
            self.assertIn('task-sync-id:', task_sync.render_leantime_description(tasks[0]))

    def test_plan_creates_when_marker_missing(self):
        task = self.make_task()
        actions = task_sync.plan_leantime_sync([task], {'Atlas / Infra': {'id': 1}}, [])
        self.assertEqual(actions[0].action, 'create')
        self.assertEqual(actions[0].project_id, 1)

    def test_plan_skips_when_existing_ticket_is_current(self):
        task = self.make_task()
        existing = [{
            'id': 74,
            'headline': task.title,
            'description': task_sync.render_leantime_description(task),
            'projectId': 1,
        }]
        actions = task_sync.plan_leantime_sync([task], {'Atlas / Infra': {'id': 1}}, existing)
        self.assertEqual(actions[0].action, 'skip')
        self.assertEqual(actions[0].ticket_id, 74)

    def test_plan_updates_when_existing_ticket_drifted(self):
        task = self.make_task(title='Updated title')
        existing = [{
            'id': 74,
            'headline': 'Old title',
            'description': 'task-sync-id: task-abc123def456',
            'projectId': 1,
        }]
        actions = task_sync.plan_leantime_sync([task], {'Atlas / Infra': {'id': 1}}, existing)
        self.assertEqual(actions[0].action, 'update')
        self.assertEqual(actions[0].ticket_id, 74)

    def test_plan_reports_missing_project_mapping(self):
        task = self.make_task(project='Missing Project')
        actions = task_sync.plan_leantime_sync([task], {'Atlas / Infra': {'id': 1}}, [])
        self.assertEqual(actions[0].action, 'missing-project')
        self.assertIsNone(actions[0].project_id)


if __name__ == '__main__':
    unittest.main()

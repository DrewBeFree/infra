// data.js — GitHub API fetch + markdown parse

async function ghFetch(path) {
  const url = `https://api.github.com/repos/${CONFIG.owner}/${path}`;
  const res = await fetch(url, {
    headers: {
      Authorization: `token ${CONFIG.token}`,
      Accept: 'application/vnd.github.v3+json'
    }
  });
  if (!res.ok) return null;
  const json = await res.json();
  return atob(json.content.replace(/\n/g, ''));
}

async function fetchRepos() {
  const raw = await ghFetch(`${CONFIG.infraRepo}/contents/${CONFIG.reposJsonPath}`);
  if (!raw) return [];
  const data = JSON.parse(raw);
  return data.repositories || [];
}

async function fetchSessionLog() {
  const raw = await ghFetch(`${CONFIG.infraRepo}/contents/SESSION_LOG.md`);
  if (!raw) return null;

  const blocks = raw.split(/^## /m).filter(b => b.trim());
  if (!blocks.length) return null;

  const block = blocks[0];
  const dateMatch = block.match(/^(\d{4}-\d{2}-\d{2}[^\n]*)/);
  const date = dateMatch ? dateMatch[1].trim() : 'Unknown date';

  function extractSection(label) {
    const re = new RegExp(`\\*\\*${label}\\*\\*([\\s\\S]*?)(?=\\*\\*|$)`);
    const m = block.match(re);
    if (!m) return [];
    return m[1].split('\n')
      .map(l => l.replace(/^[-*]\s*/, '').trim())
      .filter(Boolean);
  }

  return {
    date,
    did: extractSection('What we did:'),
    stopped: extractSection('Where we stopped:'),
    next: extractSection('Next up:')
  };
}

function parseBacklog(raw, repoName) {
  const sections = {};
  const blocks = raw.split(/^## /m).filter(b => b.trim());

  for (const block of blocks) {
    const lines = block.split('\n');
    const heading = lines[0].trim();
    const tasks = lines.slice(1)
      .filter(l => /^- \[[ x]\]/i.test(l.trim()))
      .map(l => ({
        done: /^- \[x\]/i.test(l.trim()),
        text: l.replace(/^- \[[ x]\]\s*/i, '').trim(),
        repo: repoName
      }));
    if (tasks.length) sections[heading] = tasks;
  }

  return { repo: repoName, sections };
}

async function fetchAllBacklogs(repos) {
  const results = await Promise.allSettled(
    repos.map(async repo => {
      const raw = await ghFetch(`${repo.name}/contents/BACKLOG.md`);
      if (!raw) return null;
      return parseBacklog(raw, repo.name);
    })
  );

  return results
    .filter(r => r.status === 'fulfilled' && r.value !== null)
    .map(r => r.value);
}

function getUpNext(backlogs) {
  const upNext = [];
  const priority = ['In Progress', 'Blocked', 'Blocked / Ready', 'Ready'];

  for (const backlog of backlogs) {
    let found = false;
    for (const heading of priority) {
      if (found) break;
      const tasks = backlog.sections[heading] || [];
      const incomplete = tasks.filter(t => !t.done);
      if (incomplete.length) {
        upNext.push(incomplete[0]);
        found = true;
      }
    }
    if (!found) {
      for (const tasks of Object.values(backlog.sections)) {
        const incomplete = tasks.filter(t => !t.done);
        if (incomplete.length) {
          upNext.push(incomplete[0]);
          break;
        }
      }
    }
  }

  return upNext;
}

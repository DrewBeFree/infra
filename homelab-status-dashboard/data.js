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
  const bytes = Uint8Array.from(atob(json.content.replace(/\n/g, '')), c => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

async function fetchRepos() {
  const raw = await ghFetch(`${CONFIG.infraRepo}/contents/${CONFIG.reposJsonPath}`);
  if (!raw) return [];
  const data = JSON.parse(raw);
  return data.repositories || [];
}

async function fetchSessionLog() {
  const raw = await ghFetch(`${CONFIG.infraRepo}/contents/SESSION_LOG.md`);
  if (!raw) return { today: [], fallback: null };

  const blocks = raw.split(/^## /m)
    .filter(b => b.trim())
    .filter(b => /^\d{4}-\d{2}-\d{2}/.test(b.trim()));

  function parseBlock(block) {
    const firstLine = block.split('\n')[0].trim();
    const dateMatch = firstLine.match(/^(\d{4}-\d{2}-\d{2})(?:\s+(\d{2}:\d{2}))?/);
    if (!dateMatch) return null;

    function extractSection(label) {
      const re = new RegExp(`\\*\\*${label}\\*\\*([\\s\\S]*?)(?=\\*\\*|$)`);
      const m = block.match(re);
      if (!m) return [];
      return m[1].split('\n')
        .map(l => l.replace(/^[-*]\s*/, '').trim())
        .filter(Boolean);
    }

    const title = firstLine
      .replace(/^\d{4}-\d{2}-\d{2}(?:\s+\d{2}:\d{2})?\s*[—–-]\s*/, '')
      .trim();

    return {
      date: dateMatch[1],
      time: dateMatch[2] || null,
      title:   title || null,
      did:     extractSection('What we did:'),
      stopped: extractSection('Where we stopped:'),
      next:    extractSection('Next up:')
    };
  }

  const sessions = blocks.map(parseBlock).filter(Boolean);
  const todayStr = new Date().toISOString().slice(0, 10);

  return {
    today:    sessions.filter(s => s.date === todayStr),
    previous: sessions.filter(s => s.date !== todayStr)
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
      const backlog = parseBacklog(raw, repo.name);
      backlog.type = repo.type || 'app';
      return backlog;
    })
  );

  return results
    .filter(r => r.status === 'fulfilled' && r.value !== null)
    .map(r => r.value);
}

function getUpNext(backlogs) {
  const TYPE_ORDER = ['infrastructure', 'app', 'site', 'agent'];
  const priority = ['In Progress', 'Blocked', 'Blocked / Ready', 'Ready'];

  const sorted = [...backlogs].sort((a, b) => {
    const ai = TYPE_ORDER.indexOf(a.type || 'app');
    const bi = TYPE_ORDER.indexOf(b.type || 'app');
    return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi);
  });

  return sorted.map(backlog => {
    const allOpen = Object.values(backlog.sections).flat().filter(t => !t.done);
    let top = null;

    for (const heading of priority) {
      const incomplete = (backlog.sections[heading] || []).filter(t => !t.done);
      if (incomplete.length) { top = incomplete[0]; break; }
    }
    if (!top) {
      for (const tasks of Object.values(backlog.sections)) {
        const incomplete = tasks.filter(t => !t.done);
        if (incomplete.length) { top = incomplete[0]; break; }
      }
    }

    if (!top) return null;
    return { ...top, repo: backlog.repo, type: backlog.type, remaining: allOpen.length - 1 };
  }).filter(Boolean);
}

// render.js — DOM construction + init()

function esc(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function setLiveState(state) {
  const el = document.getElementById('live-indicator');
  if (!el) return;
  const cfg = {
    fetching: { color: '#f59e0b', label: 'FETCHING', pulse: true,  glow: false },
    live:     { color: '#4ade80', label: 'LIVE',     pulse: true,  glow: true  },
    error:    { color: '#f87171', label: 'ERROR',    pulse: false, glow: false }
  }[state] || { color: '#4ade80', label: 'LIVE', pulse: true, glow: true };

  const glowStyle = cfg.glow ? `box-shadow:0 0 8px ${cfg.color}` : '';
  el.innerHTML = `
    <span class="live-dot ${cfg.pulse ? 'pulse' : ''}" style="background:${cfg.color};${glowStyle}"></span>
    <span style="color:${cfg.color};font-size:0.65rem;font-weight:700;letter-spacing:2px">${cfg.label}</span>
  `;
}

function renderHeader(lastFetched) {
  document.getElementById('last-fetched').textContent =
    lastFetched.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function renderLastSession({ today, previous }) {
  const el = document.getElementById('last-session');
  const sessions = [...(today || []), ...(previous || [])];

  if (!sessions.length) {
    el.innerHTML = '<p class="empty">No session log found.</p>';
    return;
  }

  const listItems = arr => arr.map(t => `<li>${esc(t)}</li>`).join('');

  function sessionBody(s) {
    return `
      <div class="session-block">
        <div class="session-block-label">What we did</div>
        <ul>${listItems(s.did)}</ul>
      </div>
      <div class="session-block">
        <div class="session-block-label">Where we stopped</div>
        <ul>${listItems(s.stopped)}</ul>
      </div>
      <div class="session-block">
        <div class="session-block-label">Next up</div>
        <ul>${listItems(s.next)}</ul>
      </div>
    `;
  }

  // 3-4 word highlight for a date, from that day's latest titled entry.
  function dayHighlight(daySessions) {
    const titled = daySessions.find(s => s.title);
    if (!titled) return '';
    const words = titled.title.split(/\s+/);
    let h = words.slice(0, 4).join(' ').replace(/[\s+·,;:–—-]+$/, '');
    if (words.length > 4) h += '…';
    return h;
  }

  // Group sessions by date, newest first.
  const byDate = {};
  sessions.forEach(s => { (byDate[s.date] = byDate[s.date] || []).push(s); });
  const dates = Object.keys(byDate).sort().reverse();

  // One accordion per date; inside, one sub-accordion per session time.
  // Latest date and its latest time open by default so the newest is visible at a glance.
  const html = dates.map((date, di) => {
    const daySessions = byDate[date]
      .slice()
      .sort((a, b) => (b.time || '').localeCompare(a.time || ''));
    const dateOpen = di === 0 ? ' open' : '';
    const highlight = dayHighlight(daySessions);

    const times = daySessions.map((s, si) => {
      const timeOpen = (di === 0 && si === 0) ? ' open' : '';
      const label = s.time ? esc(s.time) : 'Session';
      const title = s.title ? `<span class="session-time-title">${esc(s.title)}</span>` : '';
      return `
        <details class="session-time"${timeOpen}>
          <summary>${label}${title}</summary>
          ${sessionBody(s)}
        </details>`;
    }).join('');

    return `
      <details class="session-date-group"${dateOpen}>
        <summary class="session-date-summary">
          <span class="session-date-text">${esc(date)}</span>
          ${highlight ? `<span class="session-date-highlight">${esc(highlight)}</span>` : '<span class="session-date-highlight"></span>'}
          <span class="session-count">${daySessions.length}</span>
        </summary>
        <div class="session-date-body">${times}</div>
      </details>`;
  }).join('');

  el.innerHTML = html;
}

function renderUpNext(upNext) {
  const el = document.getElementById('up-next');
  if (!upNext.length) {
    el.innerHTML = '<p class="empty">No pending tasks found.</p>';
    return;
  }

  el.innerHTML = upNext.map(task => `
    <div class="up-next-item">
      <span class="up-next-repo">${esc(task.repo)}</span>
      <span class="up-next-text">${esc(task.text)}</span>
      ${task.remaining > 0 ? `<span class="up-next-more">+${task.remaining}</span>` : ''}
    </div>
  `).join('');
}

function renderBacklogAccordion(backlogs) {
  const el = document.getElementById('backlog');
  const TYPE_ORDER  = ['infrastructure', 'app', 'site', 'agent'];
  const TYPE_LABELS = { infrastructure: 'Infrastructure', app: 'Apps', site: 'Sites', agent: 'Agents' };
  const SECTION_ORDER = ['In Progress', 'Blocked', 'Blocked / Ready', 'Ready', 'Completed'];

  function renderRepo(backlog) {
    const openCount = Object.values(backlog.sections).flat().filter(t => !t.done).length;
    const allHeadings = Object.keys(backlog.sections);
    const ordered = [
      ...SECTION_ORDER.filter(h => backlog.sections[h]),
      ...allHeadings.filter(h => !SECTION_ORDER.includes(h))
    ];
    const sectionsHtml = ordered.map(h => `
      <div class="bl-section">
        <div class="bl-section-label">${esc(h)}</div>
        <ul>
          ${backlog.sections[h].map(t => `<li class="${t.done ? 'done' : ''}">${esc(t.text)}</li>`).join('')}
        </ul>
      </div>
    `).join('');

    return `
      <details class="bl-repo">
        <summary class="bl-summary">
          <span class="bl-repo-name">${esc(backlog.repo)}</span>
          <span class="bl-open-count">${openCount} open</span>
        </summary>
        <div class="bl-body">${sectionsHtml}</div>
      </details>
    `;
  }

  const grouped = {};
  for (const backlog of backlogs) {
    const type = backlog.type || 'app';
    if (!grouped[type]) grouped[type] = [];
    grouped[type].push(backlog);
  }

  const html = TYPE_ORDER
    .filter(t => grouped[t])
    .map(t => `
      <div class="bl-type-group">
        <div class="section-label">${TYPE_LABELS[t]}</div>
        ${grouped[t].map(renderRepo).join('')}
      </div>
    `)
    .join('');

  el.innerHTML = html || '<p class="empty">No backlogs found.</p>';
}

function renderLoading() {
  ['last-session', 'up-next', 'backlog'].forEach(id => {
    document.getElementById(id).innerHTML = '<p class="loading">Loading</p>';
  });
}

function renderError(msg) {
  ['last-session', 'up-next', 'backlog'].forEach(id => {
    document.getElementById(id).innerHTML = `<p class="error">${esc(msg)}</p>`;
  });
}

async function init() {
  renderLoading();
  setLiveState('fetching');
  try {
    const repos = await fetchRepos();
    const [sessionData, backlogs] = await Promise.all([
      fetchSessionLog(),
      fetchAllBacklogs(repos)
    ]);
    const upNext = getUpNext(backlogs);

    renderHeader(new Date());
    setLiveState('live');
    renderLastSession(sessionData);
    renderUpNext(upNext);
    renderBacklogAccordion(backlogs);
  } catch (err) {
    setLiveState('error');
    renderError(`Failed to load data: ${err.message}`);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  init();
  document.getElementById('refresh-btn').addEventListener('click', init);
});

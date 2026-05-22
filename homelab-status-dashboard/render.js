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

  // Group sessions by date
  const byDate = {};
  sessions.forEach(s => {
    if (!byDate[s.date]) byDate[s.date] = [];
    byDate[s.date].push(s);
  });

  const dates = Object.keys(byDate).sort().reverse();
  const [latestDate, ...olderDates] = dates;
  const latestSessions = byDate[latestDate];

  // Render latest date (expanded)
  let html = `<div class="session-date">${esc(latestDate)}</div>`;

  // If multiple sessions on latest date, show latest first, others collapsible
  if (latestSessions.length === 1) {
    html += sessionBody(latestSessions[0]);
  } else {
    const [latest, ...sameDayRest] = latestSessions;
    html += sessionBody(latest);

    for (const s of sameDayRest) {
      const timeLabel = s.time ? `${esc(s.time)}` : 'Earlier';
      html += `
        <details class="session-older">
          <summary>${timeLabel}</summary>
          ${sessionBody(s)}
        </details>
      `;
    }
  }

  // Render older dates (collapsed)
  for (const date of olderDates) {
    const dateSessions = byDate[date];
    html += `
      <details class="session-older">
        <summary>${esc(date)}</summary>
    `;

    if (dateSessions.length === 1) {
      html += sessionBody(dateSessions[0]);
    } else {
      // Multiple sessions on this date - show each with time label
      for (const s of dateSessions) {
        const timeLabel = s.time ? `${esc(s.time)}` : 'No time';
        html += `
          <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border);">
            <div style="font-size: 0.7rem; font-weight: 600; color: var(--text-mid); margin-bottom: 8px;">${timeLabel}</div>
            ${sessionBody(s)}
          </div>
        `;
      }
    }

    html += '</details>';
  }

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

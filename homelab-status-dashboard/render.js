// render.js — DOM construction + init()

function renderHeader(lastFetched) {
  document.getElementById('last-fetched').textContent =
    `Fetched ${lastFetched.toLocaleTimeString()}`;
}

function renderLastSession(session) {
  const el = document.getElementById('last-session');
  if (!session) {
    el.innerHTML = '<p class="empty">No session log found.</p>';
    return;
  }

  const listItems = arr => arr.map(t => `<li>${t}</li>`).join('');

  el.innerHTML = `
    <div class="session-date">${session.date}</div>
    <div class="session-section">
      <div class="section-label">What we did</div>
      <ul>${listItems(session.did)}</ul>
    </div>
    <div class="session-section">
      <div class="section-label">Where we stopped</div>
      <ul>${listItems(session.stopped)}</ul>
    </div>
    <div class="session-section">
      <div class="section-label">Next up</div>
      <ul>${listItems(session.next)}</ul>
    </div>
  `;
}

function renderUpNext(upNext) {
  const el = document.getElementById('up-next');
  if (!upNext.length) {
    el.innerHTML = '<p class="empty">No pending tasks found.</p>';
    return;
  }

  el.innerHTML = upNext.map(task => `
    <div class="up-next-item">
      <span class="up-next-repo">${task.repo}</span>
      <span class="up-next-text">${task.text}</span>
    </div>
  `).join('');
}

function renderBacklogAccordion(backlogs) {
  const el = document.getElementById('backlog');
  const ORDER = ['In Progress', 'Blocked', 'Blocked / Ready', 'Ready', 'Completed'];

  el.innerHTML = backlogs.map(backlog => {
    const openCount = Object.values(backlog.sections)
      .flat()
      .filter(t => !t.done).length;

    const allHeadings = Object.keys(backlog.sections);
    const ordered = [
      ...ORDER.filter(h => backlog.sections[h]),
      ...allHeadings.filter(h => !ORDER.includes(h))
    ];
    const sectionsHtml = ordered.map(h => {
      const tasks = backlog.sections[h];
      return `
        <div class="bl-section">
          <div class="bl-section-label">${h}</div>
          <ul>
            ${tasks.map(t => `<li class="${t.done ? 'done' : ''}">${t.text}</li>`).join('')}
          </ul>
        </div>
      `;
    }).join('');

    return `
      <details class="bl-repo">
        <summary class="bl-summary">
          <span class="bl-repo-name">${backlog.repo}</span>
          <span class="bl-open-count">${openCount} open</span>
        </summary>
        <div class="bl-body">${sectionsHtml}</div>
      </details>
    `;
  }).join('');
}

function renderLoading() {
  ['last-session', 'up-next', 'backlog'].forEach(id => {
    document.getElementById(id).innerHTML = '<p class="loading">Loading…</p>';
  });
}

function renderError(msg) {
  ['last-session', 'up-next', 'backlog'].forEach(id => {
    document.getElementById(id).innerHTML = `<p class="error">${msg}</p>`;
  });
}

async function init() {
  renderLoading();
  try {
    const repos = await fetchRepos();
    const [session, backlogs] = await Promise.all([
      fetchSessionLog(),
      fetchAllBacklogs(repos)
    ]);
    const upNext = getUpNext(backlogs);

    renderHeader(new Date());
    renderLastSession(session);
    renderUpNext(upNext);
    renderBacklogAccordion(backlogs);
  } catch (err) {
    renderError(`Failed to load data: ${err.message}`);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  init();
  document.getElementById('refresh-btn').addEventListener('click', init);
});

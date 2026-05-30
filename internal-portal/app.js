const state = {
  registry: null,
  visibility: "all",
  category: "all",
  query: "",
  selected: null
};

const registryCandidates = [
  "../ecosystem.json",
  "./ecosystem.json",
  "/ecosystem.json"
];

const $ = (selector) => document.querySelector(selector);

function escapeText(value) {
  return String(value ?? "");
}

function isLocalPreview() {
  return ["127.0.0.1", "localhost", "::1"].includes(window.location.hostname);
}

async function loadRegistry() {
  let lastError;

  for (const path of registryCandidates) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (response.ok) {
        return response.json();
      }
      lastError = new Error(`${path}: ${response.status}`);
    } catch (error) {
      lastError = error;
    }
  }

  throw lastError;
}

function firstUrl(item) {
  return item.liveUrls?.[0] || item.githubUrl || item.url || "#";
}

function isWebUrl(url) {
  return /^https?:\/\//i.test(url || "");
}

function atlasWikiToLocal(url) {
  if (!isLocalPreview()) {
    return url;
  }

  const mappings = [
    [/^http:\/\/atlas\/wiki\/projects\/([^/#]+)\/?(#.*)?$/, "/wiki/docs/projects/$1.md$2"],
    [/^http:\/\/atlas\/wiki\/infrastructure\/([^/#]+)\/?(#.*)?$/, "/wiki/docs/infrastructure/$1.md$2"],
    [/^http:\/\/atlas\/wiki\/agents-and-skills\/([^/#]+)\/?(#.*)?$/, "/wiki/docs/agents-and-skills/$1.md$2"],
    [/^http:\/\/atlas\/wiki\/workflows\/([^/#]+)\/?(#.*)?$/, "/wiki/docs/workflows/$1.md$2"],
    [/^http:\/\/atlas\/wiki\/?$/, "/wiki/docs/index.md"],
    [/^http:\/\/atlas\/ecosystem\/?$/, "/internal-portal/"]
  ];

  for (const [pattern, replacement] of mappings) {
    if (pattern.test(url)) {
      return url.replace(pattern, replacement);
    }
  }

  return url;
}

function resolvedUrl(url) {
  if (!url) {
    return "#";
  }

  if (url.startsWith("http://atlas/")) {
    return atlasWikiToLocal(url);
  }

  return url;
}

function preferredOpenUrl(item) {
  const webUrl = [...(item.liveUrls || []), item.url, item.githubUrl]
    .filter(Boolean)
    .find(isWebUrl);
  return resolvedUrl(webUrl || item.githubUrl || "#");
}

function visibleRepos() {
  const query = state.query.trim().toLowerCase();

  return state.registry.repositories.filter((repo) => {
    const matchesVisibility = state.visibility === "all" || repo.visibility === state.visibility;
    const matchesCategory = state.category === "all" || repo.category === state.category;
    const haystack = [
      repo.name,
      repo.displayName,
      repo.category,
      repo.visibility,
      repo.summary,
      repo.githubUrl,
      repo.localPath,
      ...(repo.liveUrls || [])
    ].join(" ").toLowerCase();

    return matchesVisibility && matchesCategory && (!query || haystack.includes(query));
  });
}

function createLink(label, href, variant = "primary") {
  const link = document.createElement("a");
  const url = resolvedUrl(href);
  link.className = `action-link ${variant}`;
  link.href = url;
  link.target = "_blank";
  link.rel = "noreferrer";
  link.textContent = label;
  return link;
}

function createControl(item, action) {
  const button = document.createElement("button");
  button.className = "control-button";
  button.type = "button";
  button.textContent = action;
  button.dataset.action = action;
  button.title = `${action} for ${item.displayName || item.name}`;
  button.addEventListener("click", () => handleAction(item, action));
  return button;
}

function commandFor(item, action) {
  const serviceTarget = item.deployTargets?.find((target) => target.service);

  if (action === "status" && serviceTarget?.service) {
    return `ssh atlas "systemctl --user status ${serviceTarget.service}"`;
  }
  if (action === "restart" && serviceTarget?.service) {
    return `ssh atlas "systemctl --user restart ${serviceTarget.service}"`;
  }
  if (action === "logs" && serviceTarget?.service) {
    return `ssh atlas "journalctl --user -u ${serviceTarget.service} -f"`;
  }
  if (action === "deploy") {
    if (item.name === "infra" || item.id === "internal-ecosystem-portal") {
      return "ssh atlas \"cd ~/infra && git pull && ./internal-portal/deploy.sh\"";
    }
    return item.deployTargets?.map((target) => target.notes || `${target.type} on ${target.host}`).join("\n") || "Deploy hook not wired yet.";
  }
  if (action === "restrict") {
    return "Add edge/IP allowlist before restoring public launcher exposure.";
  }
  if (action === "run") {
    return "Run hook is reserved for a future Atlas/local automation.";
  }
  if (action === "clone") {
    return `git clone ${item.githubUrl} "${item.localPath}"`;
  }
  if (action === "sync") {
    return "Pull/sync hook is reserved for this target.";
  }

  return `${action} hook ready; no command is bound yet.`;
}

function openDrawer(item, action) {
  const drawer = $("#detailDrawer");
  const content = $("#drawerContent");
  const deployTargets = item.deployTargets || [];
  const docs = item.docs || [];
  const urls = item.liveUrls || [];

  content.replaceChildren();

  const title = document.createElement("h2");
  title.textContent = item.displayName || item.name;
  const summary = document.createElement("p");
  summary.className = "drawer-summary";
  summary.textContent = item.summary || "";

  const command = document.createElement("pre");
  command.textContent = commandFor(item, action);

  const lists = document.createElement("div");
  lists.className = "drawer-grid";
  lists.innerHTML = `
    <section>
      <h3>Links</h3>
      ${urls.length ? urls.map((url) => `<a href="${resolvedUrl(url)}" target="_blank" rel="noreferrer">${escapeText(url)}</a>`).join("") : "<span>No live URL recorded</span>"}
    </section>
    <section>
      <h3>Deploy Targets</h3>
      ${deployTargets.length ? deployTargets.map((target) => `<span>${escapeText(target.type)} · ${escapeText(target.host || "n/a")} ${target.service ? "· " + escapeText(target.service) : ""}</span>`).join("") : "<span>No deploy target recorded</span>"}
    </section>
    <section>
      <h3>Docs</h3>
      ${docs.length ? docs.map((doc) => `<a href="${resolvedUrl(doc.url)}" target="_blank" rel="noreferrer">${escapeText(doc.label)}</a>`).join("") : "<span>No docs recorded</span>"}
    </section>
  `;

  content.append(title, summary, command, lists);
  drawer.classList.add("is-open");
  drawer.setAttribute("aria-hidden", "false");
}

function closeDrawer() {
  $("#detailDrawer").classList.remove("is-open");
  $("#detailDrawer").setAttribute("aria-hidden", "true");
}

function handleAction(item, action) {
  if (action === "open") {
    const url = preferredOpenUrl(item);
    if (url !== "#") {
      window.open(url, "_blank", "noopener,noreferrer");
      return;
    }
  }

  openDrawer(item, action);
}

function renderMeta(item) {
  const meta = document.createElement("dl");
  meta.className = "meta-list";

  const pairs = [
    ["Path", item.localPath],
    ["State", item.statusControl?.state],
    ["Deploy", item.deployTargets?.map((target) => target.host || target.type).join(", ")]
  ].filter(([, value]) => value);

  for (const [term, value] of pairs) {
    const dt = document.createElement("dt");
    const dd = document.createElement("dd");
    dt.textContent = term;
    dd.textContent = value;
    meta.append(dt, dd);
  }

  return meta;
}

function renderResource(item) {
  const template = $("#resourceTemplate");
  const card = template.content.firstElementChild.cloneNode(true);

  card.dataset.visibility = item.visibility;
  card.dataset.category = item.category || item.type || "resource";
  card.querySelector("h3").textContent = item.displayName || item.name;
  card.querySelector(".summary").textContent = item.summary || "";
  card.querySelector(".visibility").textContent = item.visibility;
  card.querySelector(".category").textContent = item.category || item.type || "resource";

  const oldMeta = card.querySelector(".meta-list");
  oldMeta.replaceWith(renderMeta(item));

  const links = card.querySelector(".link-row");
  if (preferredOpenUrl(item) !== "#") {
    links.append(createLink("Open", preferredOpenUrl(item)));
  }
  if (item.githubUrl) {
    links.append(createLink("GitHub", item.githubUrl, "secondary"));
  }
  for (const doc of item.docs?.slice(0, 2) || []) {
    links.append(createLink(doc.label.replace("Wiki project page", "Docs"), doc.url, "secondary"));
  }

  const controls = card.querySelector(".control-row");
  for (const action of item.statusControl?.actions || []) {
    controls.append(createControl(item, action));
  }

  return card;
}

function renderRepos() {
  const repos = visibleRepos();
  const grid = $("#repoGrid");
  grid.replaceChildren(...repos.map(renderResource));
  $("#resultCount").textContent = `${repos.length} visible`;
}

function renderOps() {
  const items = [
    ...state.registry.services,
    ...state.registry.dashboards
  ];
  $("#opsGrid").replaceChildren(...items.map(renderResource));
}

function renderDocs() {
  const docs = state.registry.docs.map((doc) => {
    const row = document.createElement("a");
    const name = document.createElement("span");
    const detail = document.createElement("small");

    row.className = "doc-row";
    row.href = resolvedUrl(doc.url);
    row.target = "_blank";
    row.rel = "noreferrer";
    name.textContent = doc.name;
    detail.textContent = `${doc.visibility} · ${doc.localPath || doc.url}`;
    row.append(name, detail);

    return row;
  });

  $("#docsList").replaceChildren(...docs);
}

function renderStats() {
  const repos = state.registry.repositories;
  $("#repoCount").textContent = repos.length;
  $("#serviceCount").textContent = state.registry.services.length;
  $("#dashboardCount").textContent = state.registry.dashboards.length;
  $("#sensitiveCount").textContent = repos.filter((repo) => repo.visibility === "sensitive").length;
  $("#runtimeMode").textContent = isLocalPreview() ? "Local preview with repo-aware links" : "Atlas private network";
}

function bindControls() {
  $("#searchInput").addEventListener("input", (event) => {
    state.query = event.target.value;
    renderRepos();
  });

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.visibility = button.dataset.filter;
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.toggle("is-active", item === button));
      renderRepos();
    });
  });

  document.querySelectorAll("[data-category]").forEach((button) => {
    button.addEventListener("click", () => {
      state.category = button.dataset.category;
      document.querySelectorAll("[data-category]").forEach((item) => item.classList.toggle("is-active", item === button));
      renderRepos();
    });
  });

  $("#closeDrawer").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeDrawer();
    }
  });
}

function renderError(error) {
  $("#repoGrid").innerHTML = `
    <article class="resource-card error-card">
      <h3>Registry unavailable</h3>
      <p class="summary">${escapeText(error.message)}</p>
    </article>
  `;
}

async function init() {
  bindControls();

  try {
    state.registry = await loadRegistry();
    renderStats();
    renderRepos();
    renderOps();
    renderDocs();
  } catch (error) {
    renderError(error);
  }
}

init();

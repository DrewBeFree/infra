const state = {
  registry: null,
  visibility: "all",
  category: "all",
  query: "",
  selected: null,
  openMapColumns: new Set(["public"])
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

function normalizeDoc(doc) {
  return {
    ...doc,
    id: doc.id,
    name: doc.id,
    displayName: doc.name,
    category: "docs",
    summary: doc.localPath || doc.url,
    liveUrls: [doc.url],
    docs: [],
    deployTargets: doc.deployTarget ? [{ type: "docs", host: doc.deployTarget }] : [],
    statusControl: { state: "reference", actions: ["open"] }
  };
}

function allMapItems() {
  return [
    ...state.registry.repositories.map((item) => ({ ...item, mapKind: "repo" })),
    ...state.registry.services.map((item) => ({ ...item, mapKind: "service", displayName: item.name, category: item.type })),
    ...state.registry.dashboards.map((item) => ({ ...item, mapKind: "dashboard", displayName: item.name, category: "dashboard" })),
    ...state.registry.docs.map((item) => ({ ...normalizeDoc(item), mapKind: "doc" }))
  ];
}

function matchesSearch(item) {
  const query = state.query.trim().toLowerCase();
  if (!query) {
    return true;
  }

  const haystack = [
    item.name,
    item.displayName,
    item.category,
    item.type,
    item.visibility,
    item.summary,
    item.githubUrl,
    item.localPath,
    item.url,
    ...(item.liveUrls || [])
  ].join(" ").toLowerCase();

  return haystack.includes(query);
}

function matchesVisibility(item) {
  return state.visibility === "all" || item.visibility === state.visibility;
}

function matchesCategory(item) {
  if (state.category === "all") {
    return true;
  }
  if (item.mapKind && item.mapKind !== "repo") {
    return state.category === item.mapKind || item.category === state.category;
  }
  return item.category === state.category;
}

function filteredMapItems() {
  return allMapItems().filter((item) => matchesSearch(item) && matchesVisibility(item) && matchesCategory(item));
}

function createMapNode(item) {
  const template = $("#mapNodeTemplate");
  const node = template.content.firstElementChild.cloneNode(true);
  node.dataset.visibility = item.visibility;
  node.dataset.kind = item.mapKind || item.category || "item";
  node.querySelector(".node-name").textContent = item.displayName || item.name;
  node.querySelector(".node-meta").textContent = `${item.visibility} / ${item.category || item.type || item.mapKind}`;
  node.addEventListener("click", () => openDrawer(item, "open"));
  return node;
}

function renderSitemap() {
  const items = filteredMapItems();
  const isFocusedView = state.query.trim() || state.visibility !== "all" || state.category !== "all";
  const columns = [
    {
      id: "public",
      title: "Public Surface",
      subtitle: "Sites, apps, public launchers",
      items: items.filter((item) => item.visibility === "public" && item.mapKind !== "doc")
    },
    {
      id: "private",
      title: "Private Workbench",
      subtitle: "Internal repos and planning systems",
      items: items.filter((item) => item.visibility === "private" && item.mapKind === "repo")
    },
    {
      id: "sensitive",
      title: "Sensitive / Controlled",
      subtitle: "IP-filtered or data-bearing surfaces",
      items: items.filter((item) => item.visibility === "sensitive")
    },
    {
      id: "ops",
      title: "Atlas Operations",
      subtitle: "Services, dashboards, deploy surfaces",
      items: items.filter((item) => ["service", "dashboard"].includes(item.mapKind) && item.visibility !== "sensitive")
    },
    {
      id: "docs",
      title: "Docs & Planning",
      subtitle: "Wiki, catalogs, workflow references",
      items: items.filter((item) => item.mapKind === "doc")
    }
  ];

  const rendered = columns.map((column) => {
    const section = document.createElement("details");
    section.className = "sitemap-column";
    section.dataset.column = column.id;
    section.open = isFocusedView ? column.items.length > 0 : state.openMapColumns.has(column.id);

    const header = document.createElement("summary");
    header.className = "column-head";
    const label = document.createElement("div");
    const title = document.createElement("h3");
    title.textContent = column.title;
    const subtitle = document.createElement("p");
    subtitle.textContent = column.subtitle;
    label.append(title, subtitle);
    const count = document.createElement("span");
    count.textContent = String(column.items.length);
    header.append(label, count);

    const list = document.createElement("div");
    list.className = "node-stack";
    if (column.items.length) {
      list.replaceChildren(...column.items.map(createMapNode));
    } else {
      const empty = document.createElement("p");
      empty.className = "empty-branch";
      empty.textContent = "No matching nodes";
      list.append(empty);
    }

    section.addEventListener("toggle", () => {
      if (section.open) {
        state.openMapColumns.add(column.id);
      } else {
        state.openMapColumns.delete(column.id);
      }
    });

    section.append(header, list);
    return section;
  });

  $("#sitemapColumns").replaceChildren(...rendered);
  $("#mapSummary").textContent = `${items.length} visible nodes / ${allMapItems().length} total`;
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
    renderSitemap();
    renderRepos();
  });

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.visibility = button.dataset.filter;
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.toggle("is-active", item === button));
      renderSitemap();
      renderRepos();
    });
  });

  document.querySelectorAll("[data-category]").forEach((button) => {
    button.addEventListener("click", () => {
      state.category = button.dataset.category;
      document.querySelectorAll("[data-category]").forEach((item) => item.classList.toggle("is-active", item === button));
      renderSitemap();
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
    renderSitemap();
    renderRepos();
    renderOps();
    renderDocs();
  } catch (error) {
    renderError(error);
  }
}

init();

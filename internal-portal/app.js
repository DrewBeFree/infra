const state = {
  registry: null,
  visibility: "all",
  category: "all",
  query: "",
  selected: null,
  mapExpanded: false,
  openSidebarGroups: new Set(["apps"])
};

const registryCandidates = [
  "../ecosystem.json",
  "./ecosystem.json",
  "/ecosystem.json"
];

const $ = (selector) => document.querySelector(selector);

const visibilityLabels = {
  all: "All",
  public: "Public",
  private: "Private",
  sensitive: "Sensitive"
};

const categoryLabels = {
  all: "All",
  app: "Apps",
  site: "Sites",
  agent: "Agents",
  infrastructure: "Infra"
};

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

function isWebUrl(url) {
  return /^https?:\/\//i.test(url || "");
}

function atlasWikiToLocal(url) {
  if (!isLocalPreview()) {
    return url;
  }

  const mappings = [
    [/^http:\/\/atlas\/wiki\/projects\/?(#.*)?$/, "/wiki/site/projects/$1"],
    [/^http:\/\/atlas\/wiki\/infrastructure\/?(#.*)?$/, "/wiki/site/infrastructure/$1"],
    [/^http:\/\/atlas\/wiki\/agents-and-skills\/?(#.*)?$/, "/wiki/site/agents-and-skills/$1"],
    [/^http:\/\/atlas\/wiki\/workflows\/?(#.*)?$/, "/wiki/site/workflows/$1"],
    [/^http:\/\/atlas\/wiki\/projects\/([^/#]+)\/?(#.*)?$/, "/wiki/site/projects/$1/$2"],
    [/^http:\/\/atlas\/wiki\/infrastructure\/([^/#]+)\/?(#.*)?$/, "/wiki/site/infrastructure/$1/$2"],
    [/^http:\/\/atlas\/wiki\/agents-and-skills\/([^/#]+)\/?(#.*)?$/, "/wiki/site/agents-and-skills/$1/$2"],
    [/^http:\/\/atlas\/wiki\/workflows\/([^/#]+)\/?(#.*)?$/, "/wiki/site/workflows/$1/$2"],
    [/^http:\/\/atlas\/wiki\/?$/, "/wiki/site/"],
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

const appIconAssets = {
  "adhd-snap": "assets/app-icons/adhd-snap.svg",
  "ai-dog-trainer": "assets/app-icons/ai-dog-trainer.svg",
  "daily-planner": "assets/app-icons/daily-planner.png",
  DrewBeFree: "assets/pixelated-drew.png",
  "drewbefree-command-center": "assets/app-icons/drewbefree-command-center.png",
  golf: "assets/app-icons/golf.png",
  "llm-debate-union": "assets/app-icons/llm-debate-union.png",
  poker: "assets/app-icons/poker.png",
  "public-command-center": "assets/app-icons/drewbefree-command-center.png",
  "recap-viewer": "assets/app-icons/recap-viewer.png",
  recipes: "assets/app-icons/recipes.png",
  "rv-maintenance": "assets/app-icons/rv-maintenance.png",
  "soccer-pickup": "assets/app-icons/soccer-pickup.png",
  "uhaul-load-planner": "assets/app-icons/uhaul-load-planner.png"
};

function appIconUrl(item) {
  if (workspaceBucket(item) !== "apps") {
    return null;
  }

  return appIconAssets[item.name] || appIconAssets[item.id] || null;
}

function initialsFor(item) {
  return itemLabel(item)
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
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

function itemLabel(item) {
  return item.displayName || item.name || item.id;
}

function uniqueItems(items) {
  const seen = new Set();
  return items.filter((item) => {
    const key = itemLabel(item).toLowerCase().replace(/\s+dashboard$/, "");

    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function normalizedPath(item) {
  return String(item.localPath || item.deployTargets?.[0]?.path || item.url || "").replace(/\//g, "\\").toLowerCase();
}

function workspaceBucket(item) {
  const path = normalizedPath(item);
  const name = String(item.name || item.id || item.displayName || "").toLowerCase();

  if (path.includes("\\documents\\github\\apps\\") || name.includes("command-center")) {
    return "apps";
  }
  if (path.includes("\\documents\\github\\sites\\")) {
    return "sites";
  }
  if (path.includes("\\documents\\github\\agents\\") || name.includes("answering-agent") || name.includes("recap-agents")) {
    return "agents";
  }
  if (path.includes("\\documents\\github\\homelab") || ["portainer", "idrac7", "ollama", "open-webui", "openclaw", "homelab-status-dashboard", "atlas-status-dashboard"].some((token) => name.includes(token))) {
    return "homelab";
  }
  if (path.includes("\\documents\\github\\infra") || ["atlas", "leantime", "internal-ecosystem-portal"].some((token) => name.includes(token))) {
    return "infra";
  }
  return "notes";
}

function ecosystemBranches(items) {
  const branchMeta = [
    ["agents", "Agents", "Automation, assistants, workers"],
    ["apps", "Apps", "Product and utility apps"],
    ["homelab", "Homelab", "Atlas services and machine surfaces"],
    ["infra", "Infra", "Portal, wiki, planning, operations"],
    ["notes", "Notes", "Loose docs, config, reference"],
    ["sites", "Sites", "Public web properties"]
  ];

  return [
    ...branchMeta.map(([id, title, subtitle]) => ({
      id,
      title,
      subtitle,
      items: uniqueItems(items.filter((item) => workspaceBucket(item) === id))
    }))
  ];
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

function createSideNavItem(item) {
  const href = preferredOpenUrl(item);
  const label = document.createElement(href === "#" ? "button" : "a");
  const iconUrl = appIconUrl(item);
  label.className = "side-nav-item";
  label.dataset.visibility = item.visibility;
  label.dataset.kind = item.mapKind || item.category || "item";
  label.dataset.hasIcon = workspaceBucket(item) === "apps" ? "true" : "false";

  if (href === "#") {
    label.type = "button";
    label.addEventListener("click", () => openDrawer(item, "open"));
  } else {
    label.href = href;
    label.target = "_blank";
    label.rel = "noreferrer";
  }

  const row = document.createElement("span");
  row.className = "side-nav-label";

  if (workspaceBucket(item) === "apps") {
    const icon = document.createElement("span");
    icon.className = "side-nav-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = initialsFor(item);

    if (iconUrl) {
      const image = document.createElement("img");
      image.src = iconUrl;
      image.alt = "";
      image.loading = "lazy";
      image.addEventListener("error", () => image.remove());
      icon.append(image);
    }

    row.append(icon);
  }

  const name = document.createElement("span");
  name.className = "side-nav-name";
  name.textContent = itemLabel(item);
  row.append(name);
  label.append(row);
  return label;
}

function renderSidebar() {
  const branches = ecosystemBranches(filteredMapItems());
  const groups = branches.map((branch) => {
    const group = document.createElement("section");
    const isOpen = state.openSidebarGroups.has(branch.id);
    group.className = "side-nav-group";
    group.classList.toggle("is-open", isOpen);
    group.dataset.group = branch.id;

    const trigger = document.createElement("button");
    trigger.className = "side-nav-trigger";
    trigger.type = "button";
    trigger.setAttribute("aria-expanded", String(isOpen));

    const label = document.createElement("span");
    label.textContent = branch.title;
    const count = document.createElement("strong");
    count.textContent = String(branch.items.length);
    trigger.append(label, count);
    trigger.addEventListener("click", () => {
      if (state.openSidebarGroups.has(branch.id)) {
        state.openSidebarGroups.delete(branch.id);
      } else {
        state.openSidebarGroups.add(branch.id);
      }
      renderSidebar();
    });

    const panel = document.createElement("div");
    panel.className = "side-nav-panel";
    const list = document.createElement("div");
    list.className = "side-nav-list";
    list.replaceChildren(...branch.items.map(createSideNavItem));
    panel.append(list);

    group.append(trigger, panel);
    return group;
  });

  $("#sideNavGroups").replaceChildren(...groups);
}

function renderSitemap() {
  const items = filteredMapItems();
  const isFocusedView = state.query.trim() || state.visibility !== "all" || state.category !== "all";
  const expandAll = Boolean(state.mapExpanded || isFocusedView);
  const columns = ecosystemBranches(items);

  const rendered = columns.map((column) => {
    const isOpen = expandAll;
    const section = document.createElement("section");
    section.className = "sitemap-column";
    section.classList.toggle("is-open", isOpen);
    section.dataset.column = column.id;

    const header = document.createElement("button");
    header.className = "column-head";
    header.type = "button";
    header.setAttribute("aria-expanded", String(isOpen));
    const label = document.createElement("div");
    const title = document.createElement("h3");
    title.textContent = column.title;
    const subtitle = document.createElement("p");
    subtitle.textContent = column.subtitle;
    label.append(title, subtitle);
    const count = document.createElement("span");
    count.textContent = String(column.items.length);
    header.append(label, count);
    header.addEventListener("click", () => {
      state.mapExpanded = !state.mapExpanded;
      renderSitemap();
    });

    const panel = document.createElement("div");
    panel.className = "branch-panel";
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
    panel.append(list);

    section.append(header, panel);
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

function createBadge(text, extraClass = "") {
  const badge = document.createElement("span");
  badge.className = `badge ${extraClass}`.trim();
  badge.textContent = text;
  return badge;
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

function renderOpsRow(item) {
  const row = document.createElement("article");
  row.className = "ops-row";
  row.dataset.visibility = item.visibility;
  row.dataset.category = item.category || item.type || "resource";

  const main = document.createElement("div");
  main.className = "ops-row-main";
  const dot = document.createElement("span");
  dot.className = "status-dot compact-dot";
  const text = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = itemLabel(item);
  const summary = document.createElement("p");
  summary.textContent = item.summary || item.url || "";
  text.append(title, summary);
  main.append(dot, text);

  const badges = document.createElement("div");
  badges.className = "ops-row-badges";
  badges.append(
    createBadge(item.visibility, "visibility"),
    createBadge(item.type || item.category || "resource", "category"),
    createBadge(item.statusControl?.state || "tracked", "state")
  );

  const target = document.createElement("div");
  target.className = "ops-row-target";
  target.textContent = item.deployTargets?.map((deployTarget) => deployTarget.host || deployTarget.type).filter(Boolean).join(", ") || item.access?.network || "no target";

  const actions = document.createElement("div");
  actions.className = "ops-row-actions";
  if (preferredOpenUrl(item) !== "#") {
    actions.append(createLink("Open", preferredOpenUrl(item)));
  }
  for (const action of item.statusControl?.actions || []) {
    if (action !== "open") {
      actions.append(createControl(item, action));
    }
  }

  row.append(main, badges, target, actions);
  return row;
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
  $("#opsGrid").replaceChildren(...items.map(renderOpsRow));
}

function renderAttention() {
  const banner = $("#uhaulBanner");
  const uhaulVisible = visibleRepos().some((repo) => repo.name === "uhaul-load-planner");
  banner.hidden = !uhaulVisible;
}

function updateFilterSummary() {
  $("#filterSummary").textContent = `${visibilityLabels[state.visibility]} / ${categoryLabels[state.category]}`;
}

function openFilterModal() {
  $("#filterModal").hidden = false;
  $("#filterButton").setAttribute("aria-expanded", "true");
}

function closeFilterModal() {
  $("#filterModal").hidden = true;
  $("#filterButton").setAttribute("aria-expanded", "false");
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

function formatTimestamp(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value || "unknown";
  }

  const pad = (part) => String(part).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function renderStats() {
  const repos = state.registry.repositories;
  const updatedAt = formatTimestamp(document.lastModified || state.registry.updatedAt);
  $("#repoCount").textContent = repos.length;
  $("#serviceCount").textContent = state.registry.services.length;
  $("#dashboardCount").textContent = state.registry.dashboards.length;
  $("#sensitiveCount").textContent = repos.filter((repo) => repo.visibility === "sensitive").length;
  $("#lastUpdated").textContent = `Updated ${updatedAt}`;
  $("#runtimeMode").textContent = isLocalPreview() ? "Local preview with repo-aware links" : "Atlas private network";
}

function bindControls() {
  $("#searchInput").addEventListener("input", (event) => {
    state.query = event.target.value;
    renderSidebar();
    renderSitemap();
    renderRepos();
    renderAttention();
  });

  $("#filterButton").addEventListener("click", openFilterModal);
  $("#closeFilters").addEventListener("click", closeFilterModal);
  $("#filterBackdrop").addEventListener("click", closeFilterModal);

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      state.visibility = button.dataset.filter;
      document.querySelectorAll("[data-filter]").forEach((item) => item.classList.toggle("is-active", item === button));
      updateFilterSummary();
      renderSidebar();
      renderSitemap();
      renderRepos();
      renderAttention();
    });
  });

  document.querySelectorAll("[data-category]").forEach((button) => {
    button.addEventListener("click", () => {
      state.category = button.dataset.category;
      document.querySelectorAll("[data-category]").forEach((item) => item.classList.toggle("is-active", item === button));
      updateFilterSummary();
      renderSidebar();
      renderSitemap();
      renderRepos();
      renderAttention();
    });
  });

  $("#closeDrawer").addEventListener("click", closeDrawer);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeFilterModal();
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
    updateFilterSummary();
    renderSidebar();
    renderSitemap();
    renderRepos();
    renderOps();
    renderAttention();
    renderDocs();
  } catch (error) {
    renderError(error);
  }
}

init();

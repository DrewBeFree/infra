const state = {
  registry: null,
  syncLinks: null,
  visibility: "all",
  category: "all",
  query: "",
  selected: null,
  openSidebarGroups: new Set(),
  openMainSections: new Set()
};

const registryCandidates = [
  "../ecosystem.json",
  "./ecosystem.json",
  "/ecosystem.json"
];

const syncLinksCandidates = [
  "./sync-links.json",
  "../sync-links.json",
  "/ecosystem/sync-links.json"
];

const leadDeskDashboardUrl = "http://127.0.0.1:8017/api/dashboard";

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

function escapeAttr(value) {
  return escapeText(value).replace(/"/g, "&quot;");
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

async function loadSyncLinks() {
  for (const path of syncLinksCandidates) {
    try {
      const response = await fetch(path, { cache: "no-store" });
      if (response.ok) {
        return response.json();
      }
    } catch {
      // Optional data file; the portal remains useful without it.
    }
  }

  return { repos: {} };
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
    [/^http:\/\/atlas\/?$/, "/internal-portal/"],
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
  return state.registry.repositories.filter(matchesItemFilters);
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

function slugFor(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/https?:\/\//g, "")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "doc";
}

function docsForResource(item, sourceKind) {
  return (item.docs || []).map((doc) => {
    const sourceId = item.id || item.name || item.displayName || sourceKind;
    return normalizeDoc({
      id: `${slugFor(sourceId)}-${slugFor(doc.label || doc.url)}`,
      name: doc.label || itemLabel(item),
      visibility: doc.visibility || item.visibility || "private",
      url: doc.url,
      localPath: doc.localPath || item.localPath,
      deployTarget: item.deployTargets?.[0]?.host,
      sourceName: itemLabel(item),
      sourceKind
    });
  });
}

function isWikiDoc(doc) {
  return String(doc.url || "").toLowerCase().includes("/wiki/");
}

function allDocumentItems() {
  const docs = [
    normalizeDoc({
      id: "atlas-wiki",
      name: "Atlas Wiki",
      visibility: "private",
      url: "http://atlas/wiki/",
      localPath: "infra/wiki",
      deployTarget: "atlas",
      sourceName: "Reference"
    })
  ];

  const nonWikiDocs = [
    ...state.registry.docs.map(normalizeDoc),
    ...state.registry.repositories.flatMap((item) => docsForResource(item, "repo")),
    ...state.registry.services.flatMap((item) => docsForResource(item, "service")),
    ...state.registry.dashboards.flatMap((item) => docsForResource(item, "dashboard"))
  ].filter((doc) => !isWikiDoc(doc));

  const seen = new Set();
  return [...docs, ...nonWikiDocs].filter((doc) => {
    const key = resolvedUrl(doc.url).toLowerCase();
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function allMapItems() {
  return [
    ...state.registry.repositories.map((item) => ({ ...item, mapKind: "repo" })),
    ...state.registry.services.map((item) => ({ ...item, mapKind: "service", displayName: item.name, category: item.type })),
    ...state.registry.dashboards.map((item) => ({ ...item, mapKind: "dashboard", displayName: item.name, category: "dashboard" })),
    ...allDocumentItems().map((item) => ({ ...item, mapKind: "doc" }))
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

  const bucket = workspaceBucket(item);
  const category = item.category || item.type || item.mapKind;

  if (state.category === "app") {
    return category === "app" || bucket === "apps";
  }
  if (state.category === "site") {
    return category === "site" || bucket === "sites";
  }
  if (state.category === "agent") {
    return category === "agent" || bucket === "agents";
  }
  if (state.category === "infrastructure") {
    return category === "infrastructure" || bucket === "infra" || bucket === "homelab";
  }

  return category === state.category || bucket === state.category;
}

function matchesItemFilters(item) {
  return matchesSearch(item) && matchesVisibility(item) && matchesCategory(item);
}

function filteredMapItems() {
  return allMapItems().filter(matchesItemFilters);
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
  const category = String(item.category || "").toLowerCase();

  if (category === "site") {
    return "sites";
  }
  if (category === "app") {
    return "apps";
  }
  if (category === "agent") {
    return "agents";
  }
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

function itemHosts(item) {
  const hosts = new Set();
  const name = String(item.name || item.id || item.displayName || "").toLowerCase();
  const path = normalizedPath(item);
  const urls = [...(item.liveUrls || []), item.url, item.githubUrl].filter(Boolean).map(String);

  if (item.host) {
    hosts.add(String(item.host).toLowerCase());
  }

  (item.deployTargets || []).forEach((target) => {
    if (target.host) {
      hosts.add(String(target.host).toLowerCase());
    }
  });

  urls.forEach((url) => {
    const lower = url.toLowerCase();
    if (lower.includes("atlas") || lower.includes("100.71.165.80")) {
      hosts.add("atlas");
    }
    if (lower.includes("localhost") || lower.includes("127.0.0.1")) {
      hosts.add("alienware");
    }
    if (lower.startsWith("https://") && !lower.includes("github.com") && !lower.includes("atlas") && !lower.includes("localhost") && !lower.includes("127.0.0.1")) {
      hosts.add("public-edge");
    }
    if (lower.includes("github.com") || lower.includes("github.io")) {
      hosts.add("github");
    }
  });

  if (path.includes("\\documents\\github\\infra") || ["infra", "internal-ecosystem-portal", "atlas-wiki", "homelab-status-dashboard", "leantime", "portainer", "idrac7", "bob"].some((token) => name.includes(token))) {
    hosts.add("atlas");
  }
  if (["alienware", "ollama", "open-webui", "openclaw", "lead-gen-agent", "llm-debate-union"].some((token) => name.includes(token))) {
    hosts.add("alienware");
  }

  return [...hosts];
}

function primaryHost(item) {
  const hosts = itemHosts(item);
  if (hosts.includes("atlas")) {
    return "atlas";
  }
  if (hosts.includes("alienware")) {
    return "alienware";
  }
  if (hosts.includes("public-edge")) {
    return "public edge";
  }
  if (hosts.includes("github")) {
    return "github";
  }
  return workspaceBucket(item);
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

function systemMapZones(items) {
  const isRepo = (item) => item.mapKind === "repo";
  const isAtlas = (item) => itemHosts(item).includes("atlas");
  const isAlienware = (item) => itemHosts(item).includes("alienware");
  const isPublic = (item) => item.visibility === "public" || itemHosts(item).includes("public-edge");
  const isDoc = (item) => item.mapKind === "doc" || item.category === "docs" || item.type === "docs" || item.type === "planning-cockpit";
  const isSensitive = (item) => item.visibility === "sensitive" || item.accessControl?.ipFilter;

  const atlasItems = items.filter((item) => isAtlas(item) && !isSensitive(item));
  const alienwareItems = items.filter(isAlienware);
  const publicItems = items.filter((item) => isPublic(item) && !isSensitive(item));
  const docItems = items.filter(isDoc);
  const sensitiveItems = items.filter(isSensitive);

  return [
    {
      id: "source",
      title: "Source + Repos",
      subtitle: "GitHub and local workspace inventory",
      primary: items.find((item) => item.name === "infra") || items.find(isRepo),
      items: uniqueItems(items.filter(isRepo))
    },
    {
      id: "atlas",
      title: "Atlas Core",
      subtitle: "Private runtime, portal, wiki, planning",
      primary: atlasItems.find((item) => item.id === "internal-ecosystem-portal") || atlasItems.find((item) => item.name === "infra") || atlasItems[0],
      items: uniqueItems(atlasItems)
    },
    {
      id: "alienware",
      title: "Alienware Local Compute",
      subtitle: "AI workstation, local services, phase-1 agents",
      primary: alienwareItems.find((item) => item.id === "ollama") || alienwareItems[0],
      items: uniqueItems(alienwareItems)
    },
    {
      id: "public",
      title: "Public Edge",
      subtitle: "External launch surfaces and Pages apps",
      primary: publicItems.find((item) => item.name === "drewbefree-command-center") || publicItems[0],
      items: uniqueItems(publicItems)
    },
    {
      id: "docs",
      title: "Docs + Planning",
      subtitle: "Wiki, project catalog, Leantime, runbooks",
      primary: docItems.find((item) => item.id === "atlas-wiki") || docItems[0],
      items: uniqueItems(docItems)
    },
    {
      id: "sensitive",
      title: "Sensitive Controls",
      subtitle: "IP-gated, admin, approval, and restricted surfaces",
      primary: sensitiveItems.find((item) => item.name === "uhaul-load-planner") || sensitiveItems[0],
      items: uniqueItems(sensitiveItems)
    }
  ];
}

function createMapNode(item) {
  const template = $("#mapNodeTemplate");
  const node = template.content.firstElementChild.cloneNode(true);
  node.dataset.visibility = item.visibility;
  node.dataset.kind = item.mapKind || item.category || "item";
  node.querySelector(".node-name").textContent = item.displayName || item.name;
  node.querySelector(".node-meta").textContent = `${item.visibility} / ${item.category || item.type || item.mapKind}`;
  node.querySelector(".node-host").textContent = primaryHost(item);
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
  const zones = systemMapZones(items);

  const rendered = zones.map((zone) => {
    const section = document.createElement("section");
    section.className = "map-zone";
    section.dataset.zone = zone.id;

    const header = document.createElement("button");
    header.className = "zone-head";
    header.type = "button";
    header.disabled = !zone.primary;
    const label = document.createElement("div");
    const title = document.createElement("h3");
    title.textContent = zone.title;
    const subtitle = document.createElement("p");
    subtitle.textContent = zone.subtitle;
    label.append(title, subtitle);
    const count = document.createElement("span");
    count.textContent = String(zone.items.length);
    header.append(label, count);
    header.addEventListener("click", () => zone.primary && openDrawer(zone.primary, "open"));

    const rail = document.createElement("div");
    rail.className = "map-rail";
    rail.setAttribute("aria-hidden", "true");

    const body = document.createElement("div");
    body.className = "zone-body";

    if (zone.primary) {
      const primary = createMapNode(zone.primary);
      primary.classList.add("zone-primary");
      body.append(primary);
    }

    const list = document.createElement("div");
    list.className = "zone-node-list";
    const children = zone.items.filter((item) => item !== zone.primary);
    if (children.length) {
      list.replaceChildren(...children.slice(0, 18).map(createMapNode));
    } else {
      const empty = document.createElement("p");
      empty.className = "empty-zone";
      empty.textContent = "No matching nodes in this view";
      list.append(empty);
    }
    body.append(list);

    section.append(header, rail, body);
    return section;
  });

  $("#systemMap").replaceChildren(...rendered);
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

function actionLabelForUrl(url) {
  const lower = String(url || "").toLowerCase();

  if (lower.includes(":3001") || lower.includes("/d/") || lower.includes("grafana")) {
    return "Grafana";
  }
  if (lower.includes(":9090")) {
    return "Prometheus";
  }
  if (lower.includes(":9443")) {
    return "Portainer";
  }
  if (lower.includes(":8095")) {
    return "Leantime";
  }
  if (lower.includes(":9119")) {
    return "Hermes";
  }
  if (lower.includes(":3027")) {
    return "Lead Desk";
  }
  if (lower.includes("/wiki/")) {
    return "Docs";
  }
  return "Open";
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

function createDetailsButton(item) {
  const button = document.createElement("button");
  button.className = "control-button";
  button.type = "button";
  button.textContent = "Details";
  button.title = `Details for ${item.displayName || item.name}`;
  button.addEventListener("click", () => openDrawer(item, "open"));
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
  const accessCommands = item.accessCommands || [];

  if (accessCommands.length) {
    return accessCommands.map((entry) => `${entry.label}\n${entry.command}`).join("\n\n");
  }

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

function syncRecordFor(item) {
  const repos = state.syncLinks?.repos || {};
  const name = item.name || item.id;
  if (name && repos[name]) {
    return repos[name];
  }

  const githubUrl = String(item.githubUrl || "").replace(/\.git$/, "").toLowerCase();
  return Object.values(repos).find((record) => {
    return record.repoFullName && githubUrl.endsWith(record.repoFullName.toLowerCase());
  }) || null;
}

function syncSectionHtml(item) {
  const record = syncRecordFor(item);
  if (!record) {
    return `
      <section>
        <h3>Sync</h3>
        <span>No synced backlog items</span>
      </section>
    `;
  }

  const links = [
    record.githubProjectUrl ? `<a href="${escapeAttr(record.githubProjectUrl)}" target="_blank" rel="noreferrer">GitHub Project</a>` : "",
    record.leantimeProjectUrl ? `<a href="${escapeAttr(record.leantimeProjectUrl)}" target="_blank" rel="noreferrer">Leantime Project</a>` : "",
    record.githubRepoUrl ? `<a href="${escapeAttr(record.githubRepoUrl)}" target="_blank" rel="noreferrer">GitHub Repo</a>` : ""
  ].filter(Boolean).join("");

  const tasks = (record.tasks || []).slice(0, 8).map((task) => {
    const issue = task.githubIssueUrl
      ? `<a href="${escapeAttr(task.githubIssueUrl)}" target="_blank" rel="noreferrer">#${escapeText(task.githubIssueNumber)} ${escapeText(task.title)}</a>`
      : `<span>${escapeText(task.title)}</span>`;
    return `<li>${issue}<small>${escapeText(task.sourceFile)}:${escapeText(task.sourceLine)}</small></li>`;
  }).join("");

  const remaining = record.taskCount > 8 ? `<span>${record.taskCount - 8} more synced tasks</span>` : "";

  return `
    <section class="sync-section">
      <h3>Sync</h3>
      ${links || "<span>No sync links recorded</span>"}
      <span>${escapeText(record.taskCount || 0)} synced backlog items</span>
      ${tasks ? `<ul class="sync-task-list">${tasks}</ul>` : ""}
      ${remaining}
    </section>
  `;
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
    ${syncSectionHtml(item)}
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

function itemTargetText(item) {
  return item.deployTargets?.map((deployTarget) => deployTarget.host || deployTarget.type).filter(Boolean).join(", ")
    || item.localPath
    || item.url
    || item.access?.network
    || "no target";
}

function renderCatalogRow(item, variant = "resource") {
  const row = document.createElement("article");
  row.className = "catalog-row";
  row.dataset.visibility = item.visibility;
  row.dataset.category = item.category || item.type || "resource";
  row.dataset.variant = variant;

  const main = document.createElement("div");
  main.className = "catalog-row-main";
  const dot = document.createElement("span");
  dot.className = "status-dot compact-dot";
  const text = document.createElement("div");
  const title = document.createElement("h3");
  title.textContent = itemLabel(item);
  const summary = document.createElement("p");
  summary.textContent = item.summary || item.url || "";
  text.append(title, summary);
  main.append(dot, text);
  main.setAttribute("role", "button");
  main.tabIndex = 0;
  main.addEventListener("click", () => openDrawer(item, "open"));
  main.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      openDrawer(item, "open");
    }
  });

  const badges = document.createElement("div");
  badges.className = "catalog-row-badges";
  badges.append(
    createBadge(item.visibility, "visibility"),
    createBadge(item.type || item.category || "resource", "category"),
    createBadge(item.statusControl?.state || "tracked", "state")
  );

  const target = document.createElement("div");
  target.className = "catalog-row-target";
  target.textContent = itemTargetText(item);

  const actions = document.createElement("div");
  actions.className = "catalog-row-actions";
  const primaryUrl = preferredOpenUrl(item);
  if (primaryUrl !== "#") {
    actions.append(createLink(actionLabelForUrl(primaryUrl), primaryUrl));

    const seenActionLabels = new Set([actionLabelForUrl(primaryUrl)]);
    const secondaryLinks = [];
    for (const url of (item.liveUrls || []).map(resolvedUrl)) {
      const label = actionLabelForUrl(url);
      if (!url || url === primaryUrl || label === "Open" || seenActionLabels.has(label)) {
        continue;
      }
      seenActionLabels.add(label);
      secondaryLinks.push(url);
      if (secondaryLinks.length === 2) {
        break;
      }
    }

    secondaryLinks.forEach((url) => {
      actions.append(createLink(actionLabelForUrl(url), url, "secondary"));
    });
  }
  actions.append(createDetailsButton(item));

  row.append(main, badges, target, actions);
  return row;
}

function renderRepos() {
  const repos = visibleRepos();
  const grid = $("#repoGrid");
  grid.replaceChildren(...repos.map((item) => renderCatalogRow(item, "repo")));
  $("#resultCount").textContent = `${repos.length} visible`;
}

function renderOps() {
  const items = [
    ...state.registry.services,
    ...state.registry.dashboards
  ].filter(matchesItemFilters);
  $("#opsGrid").replaceChildren(...items.map((item) => renderCatalogRow(item, "ops")));
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
  const docs = allDocumentItems().filter(matchesItemFilters).map((doc) => {
    const row = document.createElement("a");
    const name = document.createElement("span");
    const detail = document.createElement("small");

    row.className = "doc-row";
    row.href = resolvedUrl(doc.url);
    row.target = "_blank";
    row.rel = "noreferrer";
    row.dataset.visibility = doc.visibility;
    row.dataset.category = doc.category || "docs";
    name.textContent = doc.displayName || doc.name;
    detail.textContent = `${doc.visibility} · ${doc.sourceName ? `${doc.sourceName} · ` : ""}${doc.localPath || doc.url}`;
    row.append(name, detail);

    return row;
  });

  $("#docsList").replaceChildren(...docs);
}

function updateMainSection(section) {
  const id = section.dataset.mainSection;
  const isOpen = state.openMainSections.has(id);
  const trigger = section.querySelector(".section-toggle");

  section.classList.toggle("is-open", isOpen);
  trigger?.setAttribute("aria-expanded", String(isOpen));
}

function openMainSection(section) {
  const id = section?.dataset.mainSection;
  if (!id) {
    return;
  }

  state.openMainSections.add(id);
  updateMainSection(section);
}

function bindMainSectionToggles() {
  document.querySelectorAll("[data-main-section]").forEach((section) => {
    const id = section.dataset.mainSection;
    const trigger = section.querySelector(".section-toggle");
    if (!id || !trigger) {
      return;
    }

    trigger.addEventListener("click", () => {
      if (state.openMainSections.has(id)) {
        state.openMainSections.delete(id);
      } else {
        state.openMainSections.add(id);
      }
      updateMainSection(section);
    });
    updateMainSection(section);
  });

  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener("click", () => {
      const target = document.querySelector(link.getAttribute("href"));
      openMainSection(target?.closest("[data-main-section]"));
    });
  });

  if (window.location.hash) {
    const target = document.querySelector(window.location.hash);
    openMainSection(target?.closest("[data-main-section]"));
  }
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

async function updateLeadDeskStats() {
  const count = $("#likelyLeadCount");
  const card = $("#leadDeskCard");

  if (!count || !card) {
    return;
  }

  try {
    const response = await fetch(leadDeskDashboardUrl, { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Lead Desk API returned ${response.status}`);
    }

    const dashboard = await response.json();
    const likelyLeads = dashboard?.metrics?.high_fit ?? dashboard?.metrics?.total_leads ?? "--";
    const totalLeads = dashboard?.metrics?.total_leads ?? "unknown";
    count.textContent = String(likelyLeads);
    card.title = `${likelyLeads} likely leads / ${totalLeads} total in Lead Desk`;
    card.dataset.state = "live";
  } catch {
    if (!count.textContent || count.textContent === "--") {
      count.textContent = "--";
    }
    card.title = `${count.textContent} likely leads in Lead Desk; local dashboard API is not reachable from this browser.`;
    card.dataset.state = "offline";
  }
}

function bindControls() {
  bindMainSectionToggles();

  $("#searchInput").addEventListener("input", (event) => {
    state.query = event.target.value;
    renderSidebar();
    renderSitemap();
    renderRepos();
    renderOps();
    renderDocs();
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
      renderOps();
      renderDocs();
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
      renderOps();
      renderDocs();
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
    <article class="catalog-row error-card">
      <div class="catalog-row-main">
        <span class="status-dot compact-dot"></span>
        <div>
          <h3>Registry unavailable</h3>
          <p>${escapeText(error.message)}</p>
        </div>
      </div>
    </article>
  `;
}

async function init() {
  bindControls();

  try {
    const [registry, syncLinks] = await Promise.all([
      loadRegistry(),
      loadSyncLinks()
    ]);
    state.registry = registry;
    state.syncLinks = syncLinks;
    renderStats();
    updateFilterSummary();
    renderSidebar();
    renderSitemap();
    renderRepos();
    renderOps();
    renderDocs();
    updateLeadDeskStats();
  } catch (error) {
    renderError(error);
  }
}

init();

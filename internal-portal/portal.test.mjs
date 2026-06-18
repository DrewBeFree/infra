import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import vm from "node:vm";
import test from "node:test";

const registryPath = new URL("../ecosystem.json", import.meta.url);
const indexPath = new URL("./index.html", import.meta.url);
const appPath = new URL("./app.js", import.meta.url);
const stylePath = new URL("./style.css", import.meta.url);
const syncLinksPath = new URL("./sync-links.json", import.meta.url);
const deployPath = new URL("./deploy.sh", import.meta.url);
const avatarPath = new URL("./assets/pixelated-drew.png", import.meta.url);
const appIconPath = new URL("./assets/app-icons/daily-planner.png", import.meta.url);
const dogTrainerIconPath = new URL("./assets/app-icons/ai-dog-trainer.svg", import.meta.url);
const commandCenterPath = new URL("../../apps/drewbefree-command-center/index.html", import.meta.url);

const requiredRepos = [
  "adhd-snap",
  "ai-dog-trainer",
  "answering-agent",
  "bob",
  "claude-config",
  "daily-planner",
  "DrewBeFree",
  "drewbefree-command-center",
  "dwebbsolutions",
  "golf",
  "homelab",
  "infra",
  "interactive-setup",
  "kybernet-tech",
  "lead-gen-agent",
  "llm-debate-union",
  "photography",
  "poker",
  "recap-agents",
  "recap-viewer",
  "recipes",
  "rv-maintenance",
  "soccer-pickup",
  "surfthewebb",
  "uhaul-load-planner"
];

const visibilityLevels = new Set(["public", "private", "sensitive"]);

async function loadRegistry() {
  const raw = await readFile(registryPath, "utf8");
  return JSON.parse(raw);
}

async function loadAppSandbox() {
  const source = await readFile(appPath, "utf8");
  const sandbox = {
    URL,
    console,
    fetch: async () => ({ ok: false }),
    document: {
      querySelector: () => null,
      querySelectorAll: () => []
    },
    window: {
      location: {
        protocol: "https:",
        hostname: "portal.drewbefree.com"
      }
    }
  };

  sandbox.window.window = sandbox.window;
  vm.runInNewContext(
    `${source.replace(/\ninit\(\);\s*$/, "\n")}\n;globalThis.__portal = { state, protectedUrlFor, upgradeProtectedLinks, document, window };`,
    sandbox,
    {
      filename: "internal-portal/app.js"
    }
  );

  return sandbox.__portal;
}

test("ecosystem registry is the canonical Atlas/Tailscale source of truth", async () => {
  const registry = await loadRegistry();

  assert.equal(registry.schema, "drewbefree.ecosystem.v1");
  assert.equal(registry.access.network, "atlas-tailscale-only");
  assert.equal(registry.access.publicInternet, false);
  assert.deepEqual(registry.visibilityLevels, ["public", "private", "sensitive"]);
  assert.ok(registry.generatedFrom.includes("infra/repos.json"));
});

test("registry includes every known repo with launch and deployment metadata", async () => {
  const registry = await loadRegistry();
  const repos = new Map(registry.repositories.map((repo) => [repo.name, repo]));

  for (const name of requiredRepos) {
    assert.ok(repos.has(name), `missing repo: ${name}`);
  }

  for (const repo of registry.repositories) {
    assert.ok(visibilityLevels.has(repo.visibility), `${repo.name} has invalid visibility`);
    if (repo.sourceControl === "external-managed") {
      assert.ok(repo.managedBy, `${repo.name} needs external manager`);
      assert.ok(repo.deployTargets.some((target) => target.host === repo.managedBy || target.type === repo.managedBy), `${repo.name} needs external deploy target`);
    } else {
      assert.ok(repo.githubUrl?.startsWith("https://github.com/DrewBeFree/"), `${repo.name} needs GitHub link`);
      assert.ok(repo.localPath?.startsWith("C:\\Users\\drewb\\Documents\\GitHub\\"), `${repo.name} needs local path`);
    }
    assert.ok(Array.isArray(repo.liveUrls), `${repo.name} liveUrls must be an array`);
    assert.ok(Array.isArray(repo.docs), `${repo.name} docs must be an array`);
    assert.ok(Array.isArray(repo.deployTargets), `${repo.name} deployTargets must be an array`);
    assert.ok(repo.statusControl?.state, `${repo.name} needs a status/control state`);
  }
});

test("trading scanner remains active while the experimental repo stays archived", async () => {
  const registry = await loadRegistry();
  const syncLinks = JSON.parse(await readFile(syncLinksPath, "utf8"));
  const repos = new Map(registry.repositories.map((repo) => [repo.name, repo]));
  const linkedRepos = Object.values(syncLinks.repos);

  const tradingScanner = repos.get("trading-scanner");
  const tradingScannerLinks = syncLinks.repos["trading-scanner"];

  assert.ok(tradingScanner, "missing active repo: trading-scanner");
  assert.equal(tradingScanner.visibility, "private");
  assert.ok(
    tradingScanner.localPath?.endsWith("apps\\trading-scanner"),
    "trading-scanner should keep its active workspace path"
  );
  assert.equal(repos.has("trading-scanner-experimental"), false);
  assert.ok(tradingScannerLinks, "missing sync-links entry for trading-scanner");
  assert.equal(tradingScannerLinks.project, "Trading Scanner");
  assert.equal(tradingScannerLinks.taskCount, 0);
  assert.equal(linkedRepos.length, registry.repositories.length);
});

test("Surf The Webb is tracked as an external Framer-managed site", async () => {
  const registry = await loadRegistry();
  const surf = registry.repositories.find((repo) => repo.name === "surfthewebb");

  assert.ok(surf);
  assert.equal(surf.category, "site");
  assert.equal(surf.visibility, "public");
  assert.equal(surf.sourceControl, "external-managed");
  assert.equal(surf.managedBy, "framer");
  assert.ok(surf.liveUrls.includes("https://surfthewebb.com"));
  assert.ok(surf.deployTargets.some((target) => target.type === "framer" && target.host === "framer"));
  assert.equal(surf.publicCommandCenter, true);
});

test("Lead Gen Agent exposes the Lead Desk Hub as a live ecosystem link", async () => {
  const registry = await loadRegistry();
  const leadGen = registry.repositories.find((repo) => repo.name === "lead-gen-agent");

  assert.ok(leadGen);
  assert.equal(leadGen.category, "agent");
  assert.ok(leadGen.liveUrls.includes("http://100.117.87.57:3027"));
  assert.ok(leadGen.liveUrls.includes("http://127.0.0.1:3027"));
  assert.ok(leadGen.deployTargets.some((target) => target.type === "fastapi-local" && target.url === "http://100.117.87.57:8017"));
  assert.ok(leadGen.deployTargets.some((target) => target.type === "nextjs-local" && target.url === "http://100.117.87.57:3027"));
});

test("UHaul Planner is sensitive and removed from the public Command Center", async () => {
  const registry = await loadRegistry();
  const uhaul = registry.repositories.find((repo) => repo.name === "uhaul-load-planner");

  assert.equal(uhaul.visibility, "sensitive");
  assert.equal(uhaul.publicCommandCenter, false);
  assert.equal(uhaul.accessControl.ipFilter, true);
  assert.match(uhaul.accessControl.reason, /Sensitive \/ IP filter/);
  assert.ok(uhaul.liveUrls.includes("https://uhaul.drewbefree.com"));
});

test("portal is status and control ready", async () => {
  const registry = await loadRegistry();
  const portal = registry.dashboards.find((dashboard) => dashboard.id === "internal-ecosystem-portal");

  assert.ok(portal);
  assert.equal(portal.visibility, "private");
  assert.equal(portal.access.network, "atlas-tailscale-only");
  assert.ok(portal.liveUrls.includes("http://atlas/"));
  assert.ok(portal.liveUrls.includes("http://atlas/ecosystem/"));
  assert.ok(portal.deployTargets.some((target) => target.url === "http://atlas/" && target.type === "atlas-home-redirect"));
  assert.ok(portal.deployTargets.some((target) => target.host === "atlas" && target.type === "nginx-static"));
  assert.deepEqual(portal.statusControl.actions, ["open", "status", "restart", "logs", "deploy"]);
});

test("protected Access routes cover the local operator surfaces", async () => {
  const registry = await loadRegistry();
  const routes = new Map(registry.protectedAccess.routes.map((route) => [route.id, route]));

  assert.equal(registry.protectedAccess.provider, "cloudflare-access");
  assert.equal(registry.protectedAccess.defaultPolicy, "drew-only");

  const expectedRoutes = [
    ["portal", "https://portal.drewbefree.com/ecosystem/", "http://127.0.0.1/ecosystem/", "http://atlas/ecosystem/"],
    ["wiki", "https://wiki.drewbefree.com/wiki/", "http://127.0.0.1/wiki/", "http://atlas/wiki/"],
    ["lead-desk", "https://leads.drewbefree.com/", "http://127.0.0.1:3027", "http://atlas:3027/"],
    ["grafana", "https://grafana.drewbefree.com/", "http://127.0.0.1:3001", "http://atlas:3001/"],
    ["ai-token-dashboard", "https://tokens.drewbefree.com/", "http://127.0.0.1:7474", "http://atlas:7474/"],
    ["leantime", "https://planning.drewbefree.com/", "http://127.0.0.1:8095", "http://atlas:8095/"],
    ["hermes", "https://hermes.drewbefree.com/", "http://127.0.0.1:9119", "http://100.71.165.80:9119/"]
  ];

  for (const [id, publicUrl, origin, fallbackUrl] of expectedRoutes) {
    const route = routes.get(id);
    assert.ok(route, `missing protected route: ${id}`);
    assert.equal(route.publicUrl, publicUrl);
    assert.equal(route.origin, origin);
    assert.equal(route.fallbackUrl, fallbackUrl);
    assert.equal(route.access, "cloudflare-access");
  }
});

test("Hermes Agent is tracked as an Atlas install with access commands", async () => {
  const registry = await loadRegistry();
  const hermes = registry.services.find((service) => service.id === "hermes-agent");

  assert.ok(hermes);
  assert.equal(hermes.name, "Hermes Agent");
  assert.equal(hermes.type, "agent-runtime");
  assert.equal(hermes.host, "atlas");
  assert.equal(hermes.visibility, "private");
  assert.equal(hermes.githubUrl, "https://github.com/NousResearch/hermes-agent");
  assert.equal(hermes.localPath, "/home/drew/.hermes/hermes-agent");
  assert.ok(hermes.liveUrls.includes("http://localhost:9119"));
  assert.ok(hermes.liveUrls.includes("http://100.71.165.80:9119"));
  assert.ok(hermes.ports.includes(9119));
  assert.ok(hermes.accessCommands.some((entry) => entry.command === "/home/drew/.local/bin/hermes status"));
  assert.ok(hermes.accessCommands.some((entry) => entry.command.includes("ssh -L 9119:127.0.0.1:9119 atlas")));
  assert.ok(hermes.deployTargets.some((target) => target.type === "git-install" && target.host === "atlas"));
  assert.ok(hermes.deployTargets.some((target) => target.type === "tailscale-auth-proxy" && target.url === "http://100.71.165.80:9119"));
  assert.ok(hermes.docs.some((doc) => doc.url === "https://github.com/NousResearch/hermes-agent/blob/main/README.md"));
  assert.equal(hermes.statusControl.state, "installed");
});

test("Atlas / PowerEdge Monitoring links to Grafana and exposes docs", async () => {
  const registry = await loadRegistry();
  const dashboard = registry.dashboards.find((item) => item.id === "atlas-poweredge-monitoring");
  const docs = new Map(registry.docs.map((doc) => [doc.id, doc]));

  assert.ok(dashboard);
  assert.equal(dashboard.name, "Atlas / PowerEdge Monitoring");
  assert.equal(dashboard.liveUrls[0], "http://atlas:3001/d/atlas-overview/poweredge-dashboard");
  assert.ok(dashboard.liveUrls.includes("http://atlas.tail401605.ts.net:3001/d/atlas-overview/poweredge-dashboard"));
  assert.ok(dashboard.liveUrls.includes("http://atlas:9090"));
  assert.ok(dashboard.docs.some((doc) => doc.label === "Ollama exporter README"));
  assert.ok(dashboard.docs.some((doc) => doc.label === "Atlas monitoring deployment guide"));
  assert.ok(dashboard.docs.some((doc) => doc.url.endsWith("/docs/528/atlas-overview.json")));
  assert.ok(dashboard.deployTargets.some((target) => target.type === "docker-compose" && target.host === "atlas"));
  assert.equal(dashboard.statusControl.state, "live");
  assert.equal(docs.has("atlas-poweredge-monitoring-ollama-exporter-readme"), false);
  assert.equal(docs.has("atlas-poweredge-monitoring-atlas-monitoring-deployment-guide"), false);
});

test("portal deploy installs Atlas home redirect while preserving the old status dashboard", async () => {
  const deploy = await readFile(deployPath, "utf8");
  const registry = await loadRegistry();
  const statusDashboard = registry.dashboards.find((dashboard) => dashboard.id === "atlas-status-dashboard");

  assert.match(deploy, /INTERNAL_PORTAL_INSTALL_HOME_REDIRECT/);
  assert.match(deploy, /url=\/ecosystem\//);
  assert.match(deploy, /STATUS_TARGET/);
  assert.ok(statusDashboard.liveUrls.includes("http://atlas/status/"));
});

test("portal static files are present and load the canonical registry", async () => {
  assert.ok(existsSync(indexPath), "index.html missing");
  assert.ok(existsSync(appPath), "app.js missing");
  assert.ok(existsSync(stylePath), "style.css missing");
  assert.ok(existsSync(avatarPath), "pixelated Drew avatar missing");
  assert.ok(existsSync(appIconPath), "app icon asset missing");
  assert.ok(existsSync(dogTrainerIconPath), "AI Dog Trainer icon asset missing");

  const index = await readFile(indexPath, "utf8");
  const app = await readFile(appPath, "utf8");
  const style = await readFile(stylePath, "utf8");

  assert.match(index, /Atlas\/Tailscale/);
  assert.match(index, /@DrewBeFree Ecosystem/);
  assert.match(index, /lastUpdated/);
  assert.match(index, /filterButton/);
  assert.match(index, /filterModal/);
  assert.match(index, /mobileNavigator/);
  assert.match(index, /leadDeskCard/);
  assert.match(index, /likelyLeadCount/);
  assert.match(index, /Likely Leads/);
  assert.match(index, /data-protected-route="lead-desk"/);
  assert.match(index, /data-protected-route="grafana"/);
  assert.match(index, /data-protected-route="ai-token-dashboard"/);
  assert.match(index, /data-protected-route="leantime"/);
  assert.match(index, /data-protected-route="hermes"/);
  assert.match(index, /networkStatusLabel/);
  assert.match(index, /href="http:\/\/atlas:3027\/"/);
  assert.match(index, /AI Dashboard/);
  assert.match(index, /Hermes/);
  assert.match(index, /http:\/\/100\.71\.165\.80:9119/);
  assert.match(index, /Leantime/);
  assert.doesNotMatch(index, /uhaulBanner/);
  assert.match(index, /pixelated-drew\.png/);
  assert.match(index, /sideNavGroups/);
  assert.match(index, /ecosystemMap/);
  assert.match(index, /data-main-section="map"/);
  assert.match(index, /data-main-section="directory"/);
  assert.match(index, /data-main-section="operate"/);
  assert.match(index, /data-main-section="docs"/);
  assert.match(index, /section-toggle/);
  assert.match(index, /section-body-inner/);
  assert.match(index, /systemMap/);
  assert.match(index, /mapNodeTemplate/);
  assert.match(index, /node-host/);
  assert.match(index, /app\.js/);
  assert.match(app, /\.\.\/ecosystem\.json/);
  assert.match(app, /renderSidebar/);
  assert.match(app, /openSidebarGroups: new Set\(\)/);
  assert.match(app, /openMainSections: new Set\(\)/);
  assert.match(app, /bindMainSectionToggles/);
  assert.match(app, /openMainSection/);
  assert.match(app, /function isProtectedHostedMode/);
  assert.match(app, /function protectedRoutes/);
  assert.match(app, /function protectedUrlFor/);
  assert.match(app, /upgradeProtectedLinks/);
  assert.match(app, /Cloudflare Access protected/);
  assert.doesNotMatch(app, /openSidebarGroups: new Set\(\["apps"\]\)/);
  assert.match(app, /renderSitemap/);
  assert.match(app, /workspaceBucket/);
  assert.match(app, /itemHosts/);
  assert.match(app, /primaryHost/);
  assert.match(app, /systemMapZones/);
  assert.match(app, /allDocumentItems/);
  assert.match(app, /atlas-wiki/);
  assert.match(app, /Atlas Wiki/);
  assert.match(app, /isWikiDoc/);
  assert.match(app, /nonWikiDocs/);
  assert.match(app, /docsForResource/);
  assert.match(app, /Alienware Local Compute/);
  assert.match(app, /!lower\.includes\("github\.com"\)/);
  assert.match(app, /appIconAssets/);
  assert.match(app, /appIconUrl/);
  assert.match(app, /actionLabelForUrl/);
  assert.match(app, /Grafana/);
  assert.match(app, /Prometheus/);
  assert.match(app, /Hermes/);
  assert.match(app, /Lead Desk/);
  assert.match(app, /bindPriorityLinks/);
  assert.match(app, /127\.0\.0\.1:8017\/api\/dashboard/);
  assert.match(app, /high_fit/);
  assert.match(app, /matchesItemFilters/);
  assert.match(app, /renderCatalogRow/);
  assert.match(app, /updateFilterSummary/);
  assert.match(app, /openFilterModal/);
  assert.match(style, /\.side-nav/);
  assert.match(style, /\.mobile-nav-button/);
  assert.match(style, /\.priority-links/);
  assert.match(style, /translateX\(-105%\)/);
  assert.match(style, /--ease-smooth/);
  assert.match(style, /panel-in/);
  assert.match(style, /\.collapsible-section/);
  assert.match(style, /\.section-body/);
  assert.match(style, /grid-template-rows/);
  assert.match(style, /\.side-nav-icon/);
  assert.match(style, /\.catalog-row/);
  assert.match(style, /\.ops-link-card/);
  assert.match(style, /\.filter-panel/);
  assert.match(style, /\.system-map/);
  assert.match(style, /\.map-zone/);
  assert.match(style, /\.zone-head/);
  assert.match(style, /fade-in-up/);
});

test("protected hosted links preserve route suffixes and normalize slash variants", async () => {
  const registry = await loadRegistry();
  const app = await loadAppSandbox();

  app.state.registry = { protectedAccess: registry.protectedAccess };

  assert.equal(
    app.protectedUrlFor("http://atlas/wiki/projects/adhd-snap/"),
    "https://wiki.drewbefree.com/wiki/projects/adhd-snap/"
  );
  assert.equal(
    app.protectedUrlFor("http://atlas/wiki/projects/adhd-snap/?ref=1#intro"),
    "https://wiki.drewbefree.com/wiki/projects/adhd-snap/?ref=1#intro"
  );
  assert.equal(
    app.protectedUrlFor("http://atlas:8095"),
    "https://planning.drewbefree.com/"
  );
  assert.equal(
    app.protectedUrlFor("http://atlas:8095/projects/board?x=1#y"),
    "https://planning.drewbefree.com/projects/board?x=1#y"
  );
  assert.equal(
    app.protectedUrlFor("http://100.71.165.80:9119/metrics?format=text#top"),
    "https://hermes.drewbefree.com/metrics?format=text#top"
  );
});

test("protected link upgrades keep local fallback hrefs outside hosted mode", async () => {
  const registry = await loadRegistry();
  const app = await loadAppSandbox();
  const leadDeskLink = {
    dataset: { protectedRoute: "lead-desk" },
    getAttribute: (name) => (name === "href" ? "http://atlas:3027/" : null),
    href: "http://atlas:3027/"
  };
  const networkLabel = { innerHTML: "" };

  app.state.registry = { protectedAccess: registry.protectedAccess };
  app.document.querySelectorAll = (selector) => (selector === "[data-protected-route]" ? [leadDeskLink] : []);
  app.document.querySelector = (selector) => (selector === "#networkStatusLabel" ? networkLabel : null);
  app.window.location.protocol = "http:";
  app.window.location.hostname = "localhost";

  app.upgradeProtectedLinks();

  assert.equal(leadDeskLink.dataset.internalHref, "http://atlas:3027/");
  assert.equal(leadDeskLink.dataset.protectedHref, "https://leads.drewbefree.com/");
  assert.equal(leadDeskLink.href, "http://atlas:3027/");
  assert.match(networkLabel.innerHTML, /Atlas\/Tailscale only/);

  app.window.location.protocol = "https:";
  app.window.location.hostname = "portal.drewbefree.com";
  app.upgradeProtectedLinks();

  assert.equal(leadDeskLink.href, "https://leads.drewbefree.com/");
  assert.match(networkLabel.innerHTML, /Cloudflare Access protected/);
});

test("portal sync links include every ecosystem project, not only repos with tasks", async () => {
  const registry = await loadRegistry();
  const syncLinks = JSON.parse(await readFile(syncLinksPath, "utf8"));
  const linkedRepos = Object.values(syncLinks.repos);
  const missingProjectLinks = linkedRepos.filter((repo) => !repo.githubProjectUrl || !repo.leantimeProjectUrl);

  assert.equal(linkedRepos.length, registry.repositories.length);
  assert.deepEqual(missingProjectLinks.map((repo) => repo.project), ["Trading Scanner"]);
  assert.equal(linkedRepos.filter((repo) => repo.project !== "Trading Scanner" && repo.leantimeProjectUrl).length, registry.repositories.length - 1);
  assert.equal(linkedRepos.filter((repo) => repo.project !== "Trading Scanner" && repo.githubProjectUrl).length, registry.repositories.length - 1);
  assert.equal(linkedRepos.filter((repo) => repo.taskCount > 0).length, 9);
});

test("local preview serves rendered wiki site pages instead of raw markdown", async () => {
  const server = await readFile(new URL("./dev-server.mjs", import.meta.url), "utf8");

  assert.match(server, /wikiDocPath/);
  assert.match(server, /wiki", "site"/);
});

test("public Command Center no longer exposes UHaul Planner", async () => {
  const commandCenter = await readFile(commandCenterPath, "utf8");

  assert.doesNotMatch(commandCenter, /uhaul\.drewbefree\.com/i);
  assert.doesNotMatch(commandCenter, /UHAUL PLANNER/i);
  assert.match(commandCenter, /7 apps deployed/);
});

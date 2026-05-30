import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import test from "node:test";

const registryPath = new URL("../ecosystem.json", import.meta.url);
const indexPath = new URL("./index.html", import.meta.url);
const appPath = new URL("./app.js", import.meta.url);
const stylePath = new URL("./style.css", import.meta.url);
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
  "llm-debate-union",
  "photography",
  "poker",
  "recap-agents",
  "recap-viewer",
  "recipes",
  "rv-maintenance",
  "soccer-pickup",
  "uhaul-load-planner"
];

const visibilityLevels = new Set(["public", "private", "sensitive"]);

async function loadRegistry() {
  const raw = await readFile(registryPath, "utf8");
  return JSON.parse(raw);
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
    assert.ok(repo.githubUrl?.startsWith("https://github.com/DrewBeFree/"), `${repo.name} needs GitHub link`);
    assert.ok(repo.localPath?.startsWith("C:\\Users\\drewb\\Documents\\GitHub\\"), `${repo.name} needs local path`);
    assert.ok(Array.isArray(repo.liveUrls), `${repo.name} liveUrls must be an array`);
    assert.ok(Array.isArray(repo.docs), `${repo.name} docs must be an array`);
    assert.ok(Array.isArray(repo.deployTargets), `${repo.name} deployTargets must be an array`);
    assert.ok(repo.statusControl?.state, `${repo.name} needs a status/control state`);
  }
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
  assert.ok(portal.liveUrls.includes("http://atlas/ecosystem/"));
  assert.ok(portal.deployTargets.some((target) => target.host === "atlas" && target.type === "nginx-static"));
  assert.deepEqual(portal.statusControl.actions, ["open", "status", "restart", "logs", "deploy"]);
});

test("portal static files are present and load the canonical registry", async () => {
  assert.ok(existsSync(indexPath), "index.html missing");
  assert.ok(existsSync(appPath), "app.js missing");
  assert.ok(existsSync(stylePath), "style.css missing");

  const index = await readFile(indexPath, "utf8");
  const app = await readFile(appPath, "utf8");

  assert.match(index, /Atlas\/Tailscale/);
  assert.match(index, /app\.js/);
  assert.match(app, /\.\.\/ecosystem\.json/);
});

test("public Command Center no longer exposes UHaul Planner", async () => {
  const commandCenter = await readFile(commandCenterPath, "utf8");

  assert.doesNotMatch(commandCenter, /uhaul\.drewbefree\.com/i);
  assert.doesNotMatch(commandCenter, /UHAUL PLANNER/i);
  assert.match(commandCenter, /7 apps deployed/);
});

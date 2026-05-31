import { createReadStream, existsSync, statSync } from "node:fs";
import { createServer } from "node:http";
import { extname, join, normalize, resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname.slice(1));
const port = Number(process.env.PORT || 8765);
const host = process.env.HOST || "127.0.0.1";

const mimeTypes = {
  ".css": "text/css; charset=utf-8",
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".md": "text/markdown; charset=utf-8",
  ".svg": "image/svg+xml"
};

function fileForUrl(url) {
  const parsed = new URL(url, `http://${host}:${port}`);
  const rawPath = decodeURIComponent(parsed.pathname);
  const wikiDocPath = rawPath.match(/^\/wiki\/docs\/(.+)\.md$/);

  if (wikiDocPath) {
    const pagePath = wikiDocPath[1] === "index" ? "index.html" : join(wikiDocPath[1], "index.html");
    const renderedPage = normalize(join(root, "wiki", "site", pagePath));
    return renderedPage.startsWith(root) ? renderedPage : null;
  }

  const candidate = normalize(join(root, rawPath));

  if (!candidate.startsWith(root)) {
    return null;
  }

  if (existsSync(candidate) && statSync(candidate).isDirectory()) {
    return join(candidate, "index.html");
  }

  return candidate;
}

createServer((request, response) => {
  const file = fileForUrl(request.url || "/");

  if (!file || !existsSync(file) || !statSync(file).isFile()) {
    response.writeHead(404, { "content-type": "text/plain; charset=utf-8" });
    response.end("Not found");
    return;
  }

  response.writeHead(200, {
    "cache-control": "no-store",
    "content-type": mimeTypes[extname(file)] || "application/octet-stream"
  });
  createReadStream(file).pipe(response);
}).listen(port, host, () => {
  console.log(`Internal portal preview: http://${host}:${port}/internal-portal/`);
});

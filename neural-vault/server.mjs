import http from "node:http";
import path from "node:path";
import { promises as fs } from "node:fs";
import { fileURLToPath } from "node:url";

const APP = path.dirname(fileURLToPath(import.meta.url));
const NOTES = path.resolve(
  process.argv[2] || process.env.NOTES_DIR || path.join(APP, "notes")
);
const PORT = Number(process.env.PORT || 3000);
const PUBLIC = path.join(APP, "public");
const THREE = path.join(APP, "node_modules", "three");

const mime = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".json": "application/json; charset=utf-8"
};

const slash = (value) => value.split(path.sep).join("/");
const withoutExtension = (value) => value.replace(/\.md$/i, "");
const key = (value) =>
  withoutExtension(value).normalize("NFC").toLowerCase();

function send(res, status, data, type = "application/json; charset=utf-8") {
  res.writeHead(status, {
    "Content-Type": type,
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff"
  });
  res.end(typeof data === "string" ? data : JSON.stringify(data));
}

async function walk(directory) {
  const entries = await fs.readdir(directory, { withFileTypes: true });
  entries.sort((a, b) => a.name.localeCompare(b.name));

  const files = [];
  for (const entry of entries) {
    // Skip symbolic links, hidden directories, and dependency folders.
    if (entry.isSymbolicLink() || entry.name.startsWith(".")) continue;
    if (entry.name === "node_modules") continue;

    const filename = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(filename));
    else if (entry.isFile() && /\.md$/i.test(entry.name)) files.push(filename);
  }
  return files;
}

function extractLinks(markdown) {
  const text = markdown
    .replace(/^(`{3,}|~{3,})[^\n]*\n[\s\S]*?^\1[ \t]*$/gm, "")
    .replace(/`+[^`\n]*`+/g, "");

  const links = [];
  for (const match of text.matchAll(/!?\[\[([^\]]+)\]\]/g)) {
    links.push({ target: match[1].split("|")[0].trim(), wiki: true });
  }

  // Supports inline Markdown links, optional titles, and one nested
  // parenthesis pair in destinations. Images are not graph edges.
  const inline =
    /(?<!!)\[[^\]\n]*\]\(\s*(<[^>]+>|(?:[^\s()]|\([^()]*\))+)(?:\s+["'][^]*?["'])?\s*\)/g;

  for (const match of text.matchAll(inline)) {
    links.push({
      target: match[1].replace(/^<|>$/g, ""),
      wiki: false
    });
  }

  const definitions = new Map();
  for (const match of text.matchAll(
    /^\s{0,3}\[([^\]]+)\]:\s*(<[^>]+>|\S+)/gm
  )) {
    definitions.set(
      match[1].trim().toLowerCase(),
      match[2].replace(/^<|>$/g, "")
    );
  }

  for (const match of text.matchAll(
    /(?<!!)\[([^\]\n]+)\]\[([^\]\n]*)\]/g
  )) {
    const reference = (match[2] || match[1]).trim().toLowerCase();
    if (definitions.has(reference)) {
      links.push({ target: definitions.get(reference), wiki: false });
    }
  }

  return links;
}

async function buildGraph() {
  const filenames = await walk(NOTES);
  const nodes = [];

  for (const filename of filenames) {
    const content = await fs.readFile(filename, "utf8");
    const stat = await fs.stat(filename);
    const id = slash(path.relative(NOTES, filename));
    const heading = content.match(/^#\s+(.+)$/m)?.[1]?.trim();
    const folder = path.posix.dirname(id);

    nodes.push({
      id,
      title: heading || withoutExtension(path.posix.basename(id)),
      folder: folder === "." ? "Root" : folder,
      content,
      words: content.trim() ? content.trim().split(/\s+/u).length : 0,
      modified: stat.mtimeMs,
      outgoing: [],
      incoming: [],
      unresolved: []
    });
  }

  const paths = new Map();
  const names = new Map();

  function index(map, name, node) {
    const normalized = key(name);
    if (!map.has(normalized)) map.set(normalized, []);
    if (!map.get(normalized).includes(node)) map.get(normalized).push(node);
  }

  for (const node of nodes) {
    index(paths, node.id, node);
    index(names, path.posix.basename(node.id), node);
    index(names, node.title, node);
  }

  function resolve(source, raw, wiki) {
    let target = raw.trim().replace(/\\/g, "/");
    if (/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(target)) return { skip: true };

    target = target.split(/[?#]/)[0];
    try {
      target = decodeURIComponent(target);
    } catch {
      return { missing: raw };
    }

    if (!target) return { skip: true };
    if (!wiki && !/\.md$/i.test(target)) return { skip: true };

    const relative = path.posix.normalize(
      path.posix.join(path.posix.dirname(source.id), target)
    );
    const root = path.posix.normalize(target.replace(/^\/+/, ""));

    const candidates = target.startsWith("/")
      ? [root]
      : wiki
        ? [root, relative]
        : [relative, root];

    for (const candidate of candidates) {
      const matches = paths.get(key(candidate));
      if (matches?.length === 1) return { node: matches[0] };
    }

    if (wiki) {
      const matches = names.get(key(target));
      if (matches?.length === 1) return { node: matches[0] };
    }

    return { missing: raw };
  }

  const links = [];
  const seen = new Set();

  for (const source of nodes) {
    for (const reference of extractLinks(source.content)) {
      const result = resolve(source, reference.target, reference.wiki);

      if (result.missing) {
        source.unresolved.push(result.missing);
        continue;
      }
      if (!result.node || result.node.id === source.id) continue;

      const target = result.node;
      const edge = JSON.stringify([source.id, target.id]);
      if (seen.has(edge)) continue;
      seen.add(edge);

      links.push({ source: source.id, target: target.id });
      source.outgoing.push(target.id);
      target.incoming.push(source.id);
    }

    source.unresolved = [...new Set(source.unresolved)];
  }

  return {
    nodes,
    links,
    generatedAt: Date.now(),
    signature: JSON.stringify(
      nodes.map((node) => [node.id, node.modified, node.content.length])
    )
  };
}

async function serveFile(res, root, relative) {
  const filename = path.resolve(root, relative);
  if (!filename.startsWith(root + path.sep)) {
    send(res, 403, { error: "Forbidden" });
    return;
  }

  try {
    const data = await fs.readFile(filename);
    res.writeHead(200, {
      "Content-Type": mime[path.extname(filename)] || "application/octet-stream",
      "X-Content-Type-Options": "nosniff"
    });
    res.end(data);
  } catch (error) {
    send(res, error.code === "ENOENT" ? 404 : 500, {
      error: error.code === "ENOENT" ? "Not found" : "Unable to read file"
    });
  }
}

await fs.mkdir(NOTES, { recursive: true });

const server = http.createServer(async (req, res) => {
  try {
    if (req.method !== "GET") {
      send(res, 405, { error: "Only GET is supported" });
      return;
    }

    const url = new URL(req.url, "http://localhost");
    const pathname = decodeURIComponent(url.pathname);

    if (pathname === "/api/graph") {
      send(res, 200, await buildGraph());
    } else if (pathname.startsWith("/vendor/")) {
      await serveFile(res, THREE, pathname.slice("/vendor/".length));
    } else {
      await serveFile(
        res,
        PUBLIC,
        pathname === "/" ? "index.html" : pathname.slice(1)
      );
    }
  } catch (error) {
    console.error(error);
    send(res, 500, { error: "Unable to load graph. Check the server terminal." });
  }
});

server.on("error", (error) => {
  console.error(`Cannot start server: ${error.message}`);
  process.exitCode = 1;
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`\nNEURAL VAULT → http://localhost:${PORT}`);
  console.log(`Markdown folder → ${NOTES}\n`);
});

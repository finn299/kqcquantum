/* ==========================================================================
   Password-protected preview server for the KQC site (Render web service).

   - No dependencies; Node 18+.
   - One shared password, no username. A signed cookie keeps the visitor
     logged in for 30 days. The default password is stored as a SHA-256 hash
     below but the gate is OFF unless PREVIEW_GATE=1 is set (JP, Oct 7 2026:
     no password on the front page). With the gate on, override the password
     with env PREVIEW_PASSWORD (plaintext) or PREVIEW_PASSWORD_SHA256.
   - Serves the static site from this directory with clean URLs
     (/investors -> investors.html), noindex headers and a robots.txt that
     disallows everything, so the preview never gets indexed.

   Run locally:  node server.js  ->  http://localhost:10000
   ========================================================================== */
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = __dirname;
const PORT = process.env.PORT || 10000;
const DEFAULT_HASH = 'e93288bcc58de1633702d3e10be2a04ae1223abef356ad49b04e214fb9f9b280';   // sha256 of the shared preview password
const sha256hex = (s) => crypto.createHash('sha256').update(String(s)).digest('hex');
const GATE_ON = process.env.PREVIEW_GATE === '1' || process.env.PREVIEW_GATE === 'true';
const PASSWORD_HASH = !GATE_ON ? ''
  : process.env.PREVIEW_PASSWORD !== undefined
    ? (process.env.PREVIEW_PASSWORD ? sha256hex(process.env.PREVIEW_PASSWORD) : '')
    : (process.env.PREVIEW_PASSWORD_SHA256 || DEFAULT_HASH);
const GATE = !!PASSWORD_HASH;
// With the gate off, crawling is governed by the built robots.txt and the pages' own meta tags (PUBLIC_INDEXING).
const NOINDEX = GATE;
const SECRET = process.env.PREVIEW_SECRET || sha256hex('kqc-preview::' + PASSWORD_HASH);
const COOKIE = 'kqc_preview';
const MAX_AGE = 60 * 60 * 24 * 30;
const BLOCKED = new Set(['server.js', 'package.json', 'package-lock.json', 'render.yaml', 'README.md', '.gitignore', '.git', 'tools', 'node_modules']);

const MIME = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.xml': 'application/xml; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.ico': 'image/x-icon',
  '.woff2': 'font/woff2', '.woff': 'font/woff', '.pdf': 'application/pdf', '.webmanifest': 'application/manifest+json', '.mp4': 'video/mp4',
};

const token = () => crypto.createHmac('sha256', SECRET).update('access-granted').digest('hex');
const sha = (s) => crypto.createHash('sha256').update(String(s)).digest();
const safeEqual = (a, b) => { try { return crypto.timingSafeEqual(sha(a), sha(b)); } catch (e) { return false; } };

function cookies(req) {
  const out = {};
  (req.headers.cookie || '').split(';').forEach((c) => { const i = c.indexOf('='); if (i > 0) out[c.slice(0, i).trim()] = decodeURIComponent(c.slice(i + 1).trim()); });
  return out;
}
const isHttps = (req) => (req.headers['x-forwarded-proto'] || '').split(',')[0] === 'https';
const hasAccess = (req) => !GATE || safeEqual(cookies(req)[COOKIE] || '', token());
const passwordOk = (input) => GATE && safeEqual(sha256hex(input || ''), PASSWORD_HASH);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

function loginPage(next, error) {
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>KQC · Preview access</title>
<link rel="icon" type="image/svg+xml" href="/assets/images/favicon.svg">
<style>
:root{color-scheme:dark}*{box-sizing:border-box}
body{margin:0;min-height:100svh;display:grid;place-items:center;background:radial-gradient(900px 500px at 80% -10%,rgba(1,33,105,.55),transparent 60%),#02040b;color:#eef3ff;font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;padding:24px}
.card{width:100%;max-width:400px;padding:36px 32px;border:1px solid rgba(153,184,255,.14);border-radius:18px;background:linear-gradient(180deg,rgba(16,26,54,.6),rgba(5,10,23,.7));backdrop-filter:blur(12px)}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:26px}.brand svg{width:30px;height:30px;color:#99b8ff}.brand b{font-size:1.15rem;letter-spacing:.14em}
.brand span{font-size:.62rem;letter-spacing:.22em;text-transform:uppercase;color:#8593bb;border-left:1px solid rgba(153,184,255,.26);padding-left:12px;margin-left:2px;line-height:1.2}
h1{font-size:1.25rem;margin:0 0 6px;letter-spacing:-.02em;font-weight:500}p{margin:0 0 20px;color:#8593bb;font-size:.9rem}
label{display:block;font-size:.66rem;letter-spacing:.16em;text-transform:uppercase;color:#8593bb;margin-bottom:6px}
input{width:100%;height:46px;padding:0 14px;border-radius:8px;border:1px solid rgba(153,184,255,.26);background:rgba(5,10,23,.7);color:#fff;font:inherit}
input:focus{outline:none;border-color:#5e8aed;box-shadow:0 0 0 3px rgba(59,116,255,.2)}
button{margin-top:14px;width:100%;height:46px;border-radius:8px;border:1px solid rgba(153,184,255,.28);background:#265dd9;color:#fff;font:inherit;font-weight:500;cursor:pointer}
button:hover{background:#3b74ff}.err{color:#ffb4a2;font-size:.85rem;margin:10px 0 0}.foot{margin-top:22px;font-size:.7rem;color:#56638c;letter-spacing:.08em;text-transform:uppercase}
</style></head><body><form class="card" method="post" action="/__login" autocomplete="off">
<div class="brand"><svg viewBox="0 0 100 100" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round"><path d="M18 50 L50 18"/><path d="M82 18 L82 50"/><path d="M50 50 L82 82"/><path d="M18 82 L50 82"/></g><g fill="currentColor"><circle cx="18" cy="18" r="9.5"/><circle cx="50" cy="18" r="9.5"/><circle cx="82" cy="18" r="9.5"/><circle cx="18" cy="50" r="9.5"/><circle cx="50" cy="50" r="9.5"/><circle cx="82" cy="50" r="9.5"/><circle cx="18" cy="82" r="9.5"/><circle cx="50" cy="82" r="9.5"/><circle cx="82" cy="82" r="9.5"/></g></svg><b>KQC</b><span>Preview<br>access</span></div>
<h1>This preview is private.</h1><p>Enter the password to continue.</p>
<label for="pw">Password</label><input id="pw" name="password" type="password" required autofocus>
<input type="hidden" name="next" value="${esc(next)}">
${error ? '<div class="err">That password is not right. Try again.</div>' : ''}
<button type="submit">Enter</button>
<div class="foot">kqcquantum.com · preview build · not an offer of securities</div>
</form></body></html>`;
}

function send(res, status, body, headers) {
  res.writeHead(status, Object.assign({ 'X-Robots-Tag': 'noindex, nofollow', 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'strict-origin-when-cross-origin' }, headers || {}));
  res.end(body);
}

function readBody(req) {
  return new Promise((resolve) => { let d = ''; req.on('data', (c) => { d += c; if (d.length > 1e4) req.destroy(); }); req.on('end', () => resolve(d)); });
}

function safeNext(n) { return typeof n === 'string' && n.startsWith('/') && !n.startsWith('//') && !n.startsWith('/__') ? n : '/'; }

function serveStatic(req, res, urlPath) {
  let p = decodeURIComponent(urlPath.split('?')[0]);
  if (p.endsWith('/')) p += 'index.html';
  const rel = path.normalize(p).replace(/^(\.\.[\/\\])+/, '');
  const first = rel.split(/[\/\\]/).filter(Boolean)[0];
  if (first && BLOCKED.has(first)) return notFound(res);
  let file = path.join(ROOT, rel);
  if (!file.startsWith(ROOT)) return notFound(res);
  if (!path.extname(file) && fs.existsSync(file + '.html')) file += '.html';
  else if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) return notFound(res);
  const ext = path.extname(file).toLowerCase();
  const type = MIME[ext] || 'application/octet-stream';
  const stat = fs.statSync(file);
  const etag = 'W/"' + stat.size.toString(16) + '-' + Math.floor(stat.mtimeMs).toString(16) + '"';
  // HTML: never cached. CSS/JS: revalidate on every load (ETag) so design changes show up immediately.
  // Fonts/images: cached for a day (their names never change).
  const cache = ext === '.html' ? 'no-store' : (ext === '.css' || ext === '.js') ? 'no-cache' : 'public, max-age=86400';
  if (req.headers['if-none-match'] === etag) { res.writeHead(304, { ETag: etag, 'Cache-Control': cache }); return res.end(); }
  const headers = { 'Content-Type': type, 'Content-Length': stat.size, 'Cache-Control': cache, ETag: etag, 'X-Content-Type-Options': 'nosniff' };
  if (NOINDEX) headers['X-Robots-Tag'] = 'noindex, nofollow';
  res.writeHead(200, headers);
  if (req.method === 'HEAD') return res.end();
  fs.createReadStream(file).pipe(res);
}

function notFound(res) {
  const f = path.join(ROOT, '404.html');
  const body = fs.existsSync(f) ? fs.readFileSync(f) : 'Not found';
  send(res, 404, body, { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
}

const server = http.createServer(async (req, res) => {
  const url = req.url || '/';
  const pathname = url.split('?')[0];

  if (pathname === '/__health') return send(res, 200, 'ok', { 'Content-Type': 'text/plain' });
  // robots.txt is answered before the gate so crawlers get an explicit disallow instead of the login page
  if (NOINDEX && pathname === '/robots.txt') return send(res, 200, 'User-agent: *\nDisallow: /\n', { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });

  if (pathname === '/__logout') {
    return send(res, 303, '', { 'Set-Cookie': `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax`, Location: '/' });
  }

  if (pathname === '/__login' && req.method === 'POST') {
    const params = new URLSearchParams(await readBody(req));
    const next = safeNext(params.get('next') || '/');
    if (passwordOk(params.get('password'))) {
      const secure = isHttps(req) ? '; Secure' : '';
      return send(res, 303, '', { 'Set-Cookie': `${COOKIE}=${token()}; Path=/; Max-Age=${MAX_AGE}; HttpOnly; SameSite=Lax${secure}`, Location: next });
    }
    await new Promise((r) => setTimeout(r, 700));
    return send(res, 401, loginPage(next, true), { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
  }

  if (!hasAccess(req)) {
    // let the login page load its favicon
    if (pathname === '/assets/images/favicon.svg') return serveStatic(req, res, pathname);
    return send(res, 401, loginPage(safeNext(pathname === '/__login' ? '/' : url), false), { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store' });
  }

  if (req.method !== 'GET' && req.method !== 'HEAD') return send(res, 405, 'Method not allowed', { 'Content-Type': 'text/plain' });
  return serveStatic(req, res, url);
});

server.listen(PORT, () => {
  console.log(`KQC preview on :${PORT} (${GATE ? 'password gate ON' : 'password gate OFF'})`);
});

/* Kengūros treniruoklis — service worker.
   Shell (html/js/json): network-first, cache fallback → updates land on
   the next load, offline still opens the app. Figures (png): cache-first,
   filled on demand → a paper the kid has opened once works offline. */
const SHELL = "kengura-shell-v2";
const FIGS = "kengura-figs-v16";   // bump whenever a figure PNG is replaced (cache-first!)
const SHELL_URLS = ["./", "kengura.html", "kengura-archive.js", "manifest.webmanifest", "icon.svg"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(SHELL_URLS).catch(() => {})).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== SHELL && k !== FIGS).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if(req.method !== "GET") return;
  const url = new URL(req.url);
  if(url.origin !== self.location.origin) return;
  if(/\/figures\//.test(url.pathname)){
    e.respondWith(caches.open(FIGS).then(c => c.match(req).then(hit => hit || fetch(req).then(res => { if(res.ok) c.put(req, res.clone()); return res; }))));
    return;
  }
  // no-cache: revalidate with the server, so a fixed archive is never hidden by the HTTP cache
  e.respondWith(fetch(req, {cache: "no-cache"}).then(res => {
    if(res.ok){ const copy = res.clone(); caches.open(SHELL).then(c => c.put(req, copy)); }
    return res;
  }).catch(() => caches.match(req).then(hit => hit || (req.mode === "navigate" ? caches.match("kengura.html") : undefined))));
});

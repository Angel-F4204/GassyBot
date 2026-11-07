// Lets GassyBot install as an app and open instantly, even while the free server wakes up.
// The app itself loads from the cache first and updates in the background for next time.
// Prices (/api/) always come from the network and are never cached here.
const CACHE = 'gassybot-v2';
const SHELL = ['/', '/manifest.webmanifest', '/static/icons/icon-192.png', '/static/icons/icon-512.png', '/static/icons/apple-touch-icon.png'];

self.addEventListener('install', e => {
    e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
    e.waitUntil(caches.keys()
        .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
        .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
    const url = new URL(e.request.url);
    if (e.request.method !== 'GET' || url.origin !== location.origin || url.pathname.startsWith('/api/')) return;
    e.respondWith(caches.open(CACHE).then(async cache => {
        const cached = await cache.match(e.request);
        const fresh = fetch(e.request).then(rsp => {
            if (rsp.ok) cache.put(e.request, rsp.clone());
            return rsp;
        });
        if (cached) {
            // Show the saved copy now, keep the download going to update it
            e.waitUntil(fresh.catch(() => {}));
            return cached;
        }
        return fresh;
    }));
});

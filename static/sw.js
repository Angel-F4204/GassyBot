// Lets GassyBot install as an app and open even with a bad connection.
// Pages load fresh from the network when possible; prices are never cached here.
const CACHE = 'gassybot-v1';
const SHELL = ['/', '/manifest.webmanifest', '/static/icons/icon-192.png', '/static/icons/icon-512.png'];

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
    e.respondWith(
        fetch(e.request)
            .then(rsp => {
                const copy = rsp.clone();
                caches.open(CACHE).then(c => c.put(e.request, copy));
                return rsp;
            })
            .catch(() => caches.match(e.request))
    );
});

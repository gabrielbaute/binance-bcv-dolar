const CACHE_NAME = "exchange-rate-v3";
const APP_SHELL = [
    "/",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css",
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)),
    );
    self.skipWaiting();
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) =>
            Promise.all(
                cacheNames
                    .filter((cacheName) => cacheName !== CACHE_NAME)
                    .map((cacheName) => caches.delete(cacheName)),
            ),
        ),
    );
    self.clients.claim();
});

async function networkFirst(request) {
    const cache = await caches.open(CACHE_NAME);
    try {
        const response = await fetch(request, { cache: "no-store" });
        if (response && response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    } catch {
        const cached = await cache.match(request);
        if (cached) {
            return cached;
        }
        throw new Error("Network unavailable and no cache entry found");
    }
}

self.addEventListener("fetch", (event) => {
    const { request } = event;
    if (request.method !== "GET") {
        return;
    }

    const url = new URL(request.url);
    const isSameOrigin = url.origin === self.location.origin;
    const isStaticAsset =
        url.pathname.startsWith("/static/css/") ||
        url.pathname.startsWith("/static/js/");

    if (isSameOrigin && isStaticAsset) {
        event.respondWith(networkFirst(request));
        return;
    }

    event.respondWith(
        caches.match(request).then((cached) => {
            if (cached) {
                return cached;
            }
            return fetch(request);
        }),
    );
});
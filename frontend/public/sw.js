/* NewsRadar Service Worker — Push + Offline Cache */
const CACHE = "newsradar-v1";
const OFFLINE_URLS = ["/", "/sources", "/bookmarks", "/settings"];

self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(OFFLINE_URLS)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  if (e.request.url.includes("/api/")) return; // never cache API calls
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request))
  );
});

self.addEventListener("push", (e) => {
  if (!e.data) return;
  const data = e.data.json();
  e.waitUntil(
    self.registration.showNotification(data.title || "NewsRadar", {
      body: data.body || "",
      icon: data.icon || "/icons/icon-192.png",
      badge: "/icons/icon-192.png",
      data: { url: data.url || "/" },
      vibrate: [100, 50, 100],
      tag: "newsradar-news",
      renotify: true,
    })
  );
});

self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  const url = e.notification.data?.url || "/";
  e.waitUntil(clients.openWindow(url));
});

// static/sw.js
const CACHE_NAME = 'blogend-v3'; // versiyon numarasını artırarak cache kırarsın
const PRECACHE_URLS = [
  '/',                      // ana sayfa
  '/static/css/blog.css',   // ana css
  '/static/images/ejderha_logo.png' // logo
  // ihtiyaca göre ekleyebilirsin
];

// Kurulum: önyükleme cache
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting(); // yeni SW hemen aktif olsun
});

// Aktivasyon: eski cache'leri temizle
self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((key) => {
      if (key !== CACHE_NAME) return caches.delete(key);
    }));
    await self.clients.claim();
  })());
});

// İstekler: same-origin isteklerde "cache first, network fallback"
// HTML sayfaları için network-first'e yakın davran (eski HTML birikmesin)
self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Sadece aynı origin
  if (url.origin !== self.location.origin) return;

  // HTML ise: önce ağ, olmazsa cache
  if (req.mode === 'navigate' || (req.headers.get('accept') || '').includes('text/html')) {
    event.respondWith(
      (async () => {
        try {
          const fresh = await fetch(req);
          // İsteğe bağlı: bir kopyasını cache'e koymak istersen:
          const cache = await caches.open(CACHE_NAME);
          cache.put(req, fresh.clone());
          return fresh;
        } catch (err) {
          const cached = await caches.match(req);
          return cached || caches.match('/');
        }
      })()
    );
    return;
  }

  // Diğerleri (CSS/JS/IMG): cache-first
  event.respondWith(
    (async () => {
      const cached = await caches.match(req);
      if (cached) return cached;
      try {
        const fresh = await fetch(req);
        // Sadece GET ve başarılı yanıtları cache’le
        if (req.method === 'GET' && fresh && fresh.status === 200) {
          const cache = await caches.open(CACHE_NAME);
          cache.put(req, fresh.clone());
        }
        return fresh;
      } catch (err) {
        return cached; // en azından cache varsa onu döndür
      }
    })()
  );
});

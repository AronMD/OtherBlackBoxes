const staticNoBlackBoxes = "no-black-boxes"
const assets = [
  "/",
  "/index.html",
  "/style.css",
  "/app.js",
  "/images/logo.png",
]

self.addEventListener("install", installEvent => {
    installEvent.waitUntil(
        caches.open(staticDevCoffee).then(cache => {
        cache.addAll(assets)
        })
    )
})

self.addEventListener("fetch", fetchEvent => {
    fetchEvent.respondWith(
    caches.match(fetchEvent.request).then(res => {
    return res || fetch(fetchEvent.request)
    })
    )
})
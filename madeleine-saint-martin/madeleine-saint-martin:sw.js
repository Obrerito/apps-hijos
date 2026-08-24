// Service worker mínimo, sin caché: existe solo para que Android/Chrome
// reconozca la página como "instalable" (ícono propio + pantalla completa,
// en vez de un simple acceso directo con el logo de Chrome).
// A propósito NO guarda nada en caché, para evitar que vuelva a mostrar
// contenido viejo como pasó antes.
self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request));
});

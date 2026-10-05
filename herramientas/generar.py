#!/usr/bin/env python3
"""Genera las tarjetas a partir de su datos.json y reconstruye el panel.

Uso (desde la raíz del repositorio):
    python3 herramientas/generar.py                # todas las tarjetas con datos.json + panel
    python3 herramientas/generar.py luciana-belen  # solo esa tarjeta + panel

Cada tarjeta es una carpeta. Si la carpeta tiene datos.json, este programa
escribe index.html, manifest.json, sw.js y qr.png. Las carpetas sin datos.json
(tarjetas hechas a mano) no se tocan: solo se listan en el panel.

La foto (avatar.jpg) y los íconos (icon-192.png, icon-512.png) se preparan
aparte y se dejan dentro de la carpeta.
"""
import html
import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SITIO = "https://obrerito.github.io/apps-hijos"
REPO = "https://github.com/Obrerito/apps-hijos"
NO_SON_TARJETAS = {"herramientas", "panel"}

FLECHA = ('<svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M4 12L12 4M12 4H6M12 4V10" '
          'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

ICONOS = {
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.77.46 3.45 1.28 4.94L2 22l5.29-1.39a9.9 9.9 0 0 0 4.75 1.21h.01c5.46 0 9.91-4.45 9.91-9.91C21.96 6.45 17.51 2 12.04 2Zm5.8 14.02c-.24.68-1.4 1.33-1.93 1.4-.5.07-1.12.1-1.8-.11-.42-.13-.95-.3-1.64-.6-2.88-1.24-4.76-4.14-4.9-4.33-.14-.19-1.17-1.56-1.17-2.97 0-1.42.74-2.11 1-2.4.26-.29.57-.36.76-.36.19 0 .38 0 .55.01.18.01.42-.07.65.5.24.58.8 2.01.87 2.16.07.15.12.32.02.51-.1.19-.15.31-.3.48-.15.17-.31.38-.44.51-.15.15-.3.31-.13.6.17.29.76 1.26 1.63 2.04 1.12 1 2.06 1.31 2.35 1.46.29.15.46.13.63-.08.17-.21.72-.84.91-1.13.19-.29.38-.24.64-.14.26.1 1.66.78 1.94.92.28.14.47.21.54.33.07.12.07.68-.17 1.36Z"/></svg>',
    "email": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="5" width="18" height="14" rx="2.2"/><path d="M3.5 6.5 12 13l8.5-6.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "web": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.7 3.8 9s-1.3 6.4-3.8 9c-2.5-2.6-3.8-5.7-3.8-9s1.3-6.4 3.8-9Z" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3.5" y="3.5" width="17" height="17" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.2" cy="6.8" r="1" fill="currentColor" stroke="none"/></svg>',
    "youtube": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="6" width="18" height="12" rx="3.2"/><path d="M10.5 9.8v4.4l4-2.2Z" fill="currentColor" stroke="none"/></svg>',
    "telefono": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M5 4h3.5l1.6 4.2-2.2 1.5a12 12 0 0 0 6.4 6.4l1.5-2.2L20 15.5V19a1.5 1.5 0 0 1-1.6 1.5C10.6 20 4 13.400 3.500 5.600A1.500 1.500 0 0 1 5 4Z" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "mapa": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M12 21s-6.500-5.800-6.500-11a6.500 6.500 0 0 1 13 0c0 5.200-6.500 11-6.500 11Z" stroke-linejoin="round"/><circle cx="12" cy="10" r="2.400"/></svg>',
    "enlace": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M10 14a4 4 0 0 0 5.700 0l3-3a4 4 0 0 0-5.700-5.700l-1 1M14 10a4 4 0 0 0-5.700 0l-3 3a4 4 0 0 0 5.700 5.700l1-1" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}

SW = """self.addEventListener('fetch', (event) => {
  event.respondWith(fetch(event.request));
});
"""


def e(texto):
    return html.escape(str(texto), quote=True)


def carpetas_de_tarjetas():
    return sorted(p for p in RAIZ.iterdir()
                  if p.is_dir() and not p.name.startswith(".")
                  and p.name not in NO_SON_TARJETAS and (p / "index.html").exists()
                  or (p.is_dir() and (p / "datos.json").exists()))


def generar_tarjeta(carpeta):
    datos = json.loads((carpeta / "datos.json").read_text(encoding="utf-8"))
    estilo = datos["estilo"]
    colores = estilo["colores"]

    if estilo.get("encabezado") == "retrato":
        foto = f'    <img class="portrait" src="{e(datos["foto"])}" alt="{e(datos["foto_alt"])}">'
    else:
        foto = f'    <img class="avatar" src="{e(datos["foto"])}" alt="{e(datos["foto_alt"])}" width="92" height="92">'
    clase = ' class="caps"' if estilo.get("nombre_en_mayusculas") else ""
    identidad = [foto, f'    <h1{clase}>{e(datos["nombre"])}</h1>']
    if datos.get("profesion"):
        identidad.append(f'    <p class="specialty">{e(datos["profesion"])}</p>')
    if datos.get("frase"):
        identidad.append(f'    <p class="tagline">{e(datos["frase"])}</p>')

    filas = []
    for enlace in datos["enlaces"]:
        url = enlace["url"]
        externo = '' if url.startswith(("mailto:", "tel:")) else ' target="_blank" rel="noopener"'
        clase_fila = "link-row primary" if enlace.get("principal") else "link-row"
        icono = ICONOS.get(enlace.get("tipo"), ICONOS["enlace"])
        filas.append(
            f'    <a class="{clase_fila}" href="{e(url)}"{externo}>\n'
            f'      <span class="link-icon" aria-hidden="true">{icono}</span>\n'
            f'      <span class="link-text">\n'
            f'        <span class="link-label">{e(enlace["titulo"])}</span>\n'
            f'        <span class="link-sub">{e(enlace["detalle"])}</span>\n'
            f'      </span>\n'
            f'      <span class="link-arrow" aria-hidden="true">{FLECHA}</span>\n'
            f'    </a>')

    valores = {
        "nombre": e(datos["nombre"]),
        "nombre_app": e(datos["nombre_app"]),
        "descripcion": e(datos["descripcion"]),
        "pie": e(datos.get("pie", "Tarjeta de contacto digital")),
        "foto_encuadre": datos.get("foto_encuadre", "50% 30%"),
        "google_fonts": estilo["google_fonts"].replace("&", "&amp;"),
        "fuente_titulo": estilo["fuente_titulo"],
        "fuente_texto": estilo["fuente_texto"],
        "bloque_identidad": "\n".join(identidad),
        "bloque_enlaces": "\n\n".join(filas),
        **colores,
    }
    pagina = (RAIZ / "herramientas" / "plantilla.html").read_text(encoding="utf-8")
    pagina = re.sub(r"\{\{(\w+)\}\}", lambda m: valores[m.group(1)], pagina)
    (carpeta / "index.html").write_text(pagina, encoding="utf-8")

    manifest = {
        "start_url": "./index.html",
        "scope": "./",
        "display": "standalone",
        "background_color": colores["fondo"],
        "theme_color": colores["fondo"],
        "orientation": "portrait",
        "name": datos["nombre"],
        "short_name": datos["nombre_app"],
        "description": datos["descripcion"],
        "icons": [
            {"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"},
        ],
    }
    (carpeta / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (carpeta / "sw.js").write_text(SW, encoding="utf-8")

    try:
        import segno
        segno.make(f"{SITIO}/{carpeta.name}/", error="m").save(
            str(carpeta / "qr.png"), scale=16, border=4, dark="#000000", light="#ffffff")
    except ImportError:
        print(f"  (sin la librería 'segno' no se regenera el QR de {carpeta.name}; el existente sigue valiendo)")
    print(f"✓ {carpeta.name}")


def generar_panel():
    fichas = []
    for carpeta in carpetas_de_tarjetas():
        nombre, detalle, generada = carpeta.name, "", (carpeta / "datos.json").exists()
        if generada:
            datos = json.loads((carpeta / "datos.json").read_text(encoding="utf-8"))
            nombre = datos["nombre"]
            detalle = datos.get("profesion") or datos.get("descripcion", "")
        else:
            texto = (carpeta / "index.html").read_text(encoding="utf-8")
            titulo = re.search(r"<title>([^<]*)", texto)
            nombre = html.unescape(titulo.group(1)) if titulo else carpeta.name
        icono = f"../{carpeta.name}/icon-192.png"
        qr = (f'<a href="../{carpeta.name}/qr.png">QR</a>' if (carpeta / "qr.png").exists() else "")
        datos_link = (f'<a href="{REPO}/blob/main/{carpeta.name}/datos.json">Datos</a>' if generada else "")
        tipo = "Con ficha de datos" if generada else "Hecha a mano"
        fichas.append(f"""    <li class="ficha">
      <img src="{icono}" alt="" width="64" height="64">
      <div class="cuerpo">
        <h2>{e(nombre)}</h2>
        <p class="detalle">{e(detalle)}</p>
        <p class="ruta"><code>{carpeta.name}/</code> · {tipo}</p>
        <p class="acciones">
          <a class="ver" href="../{carpeta.name}/">Abrir tarjeta</a>
          <a href="{REPO}/tree/main/{carpeta.name}">Archivos</a>
          {datos_link}
          {qr}
        </p>
        <p class="url">{SITIO}/{carpeta.name}/</p>
      </div>
    </li>""")

    pagina = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Panel de tarjetas</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<style>
  :root {{ --bg:#F6F4EF; --surface:#FFFFFF; --ink:#22211E; --soft:#625E56; --line:#E2DDD2; --accent:#7A5F3E; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#171614; --surface:#211F1C; --ink:#F1EEE7; --soft:#B0AA9D; --line:#35322D; --accent:#D8C4AD; }}
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink);
         font-family:-apple-system,"Segoe UI",Roboto,sans-serif; padding:32px 16px 56px; }}
  main {{ max-width:760px; margin:0 auto; }}
  h1 {{ font-family:Georgia,serif; font-weight:400; font-size:30px; margin:0 0 6px; }}
  .intro {{ color:var(--soft); line-height:1.55; margin:0 0 6px; max-width:62ch; }}
  .intro a {{ color:var(--accent); }}
  ul {{ list-style:none; padding:0; margin:26px 0 0; display:grid; gap:12px; }}
  .ficha {{ display:flex; gap:16px; background:var(--surface); border:1px solid var(--line);
           border-radius:10px; padding:16px; }}
  .ficha img {{ border-radius:14px; flex:none; object-fit:cover; background:var(--line); }}
  .cuerpo {{ min-width:0; flex:1; }}
  h2 {{ margin:0; font-size:18px; font-weight:600; }}
  p {{ margin:4px 0 0; }}
  .detalle, .ruta {{ color:var(--soft); font-size:14px; }}
  .acciones {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:12px; }}
  .acciones a {{ font-size:14px; text-decoration:none; color:var(--ink); border:1px solid var(--line);
                border-radius:6px; padding:6px 12px; }}
  .acciones a.ver {{ background:var(--accent); border-color:var(--accent); color:var(--bg); }}
  .url {{ font-size:12.5px; color:var(--soft); margin-top:10px; overflow-wrap:anywhere; }}
  code {{ font-family:ui-monospace,Menlo,monospace; font-size:13px; }}
</style>
</head>
<body>
<main>
  <h1>Panel de tarjetas</h1>
  <p class="intro">Todas las tarjetas están guardadas en el repositorio
    <a href="{REPO}">Obrerito/apps-hijos</a> de GitHub: una carpeta por tarjeta.
    Lo que se guarda ahí se publica solo en <code>obrerito.github.io/apps-hijos/</code>.</p>
  <p class="intro">Cómo se modifica y cómo se crea una nueva: <a href="{REPO}/blob/main/LEEME.md">LEEME</a>.</p>
  <ul>
{chr(10).join(fichas)}
  </ul>
</main>
</body>
</html>
"""
    (RAIZ / "panel").mkdir(exist_ok=True)
    (RAIZ / "panel" / "index.html").write_text(pagina, encoding="utf-8")
    print(f"✓ panel ({len(fichas)} tarjetas)")


if __name__ == "__main__":
    pedidas = sys.argv[1:]
    for carpeta in carpetas_de_tarjetas():
        if (carpeta / "datos.json").exists() and (not pedidas or carpeta.name in pedidas):
            generar_tarjeta(carpeta)
    generar_panel()

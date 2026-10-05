# Tarjetas de contacto digitales

Este repositorio es el lugar donde viven todas las tarjetas. Es de la cuenta
de GitHub **Obrerito** y todo lo que se guarda aquí se publica solo en:

**https://obrerito.github.io/apps-hijos/**

## Dónde está cada cosa

| Qué | Dónde |
|---|---|
| Una tarjeta | Una carpeta con su nombre, por ejemplo `luciana-belen/` |
| Su dirección pública | `https://obrerito.github.io/apps-hijos/<carpeta>/` |
| Sus datos (textos, enlaces, colores, letras) | `<carpeta>/datos.json` |
| Su foto e íconos | `<carpeta>/avatar.jpg`, `icon-192.png`, `icon-512.png` |
| Su código QR | `<carpeta>/qr.png` |
| El panel con todas las tarjetas | `panel/` → https://obrerito.github.io/apps-hijos/panel/ |
| El molde común y el programa que arma las tarjetas | `herramientas/` |

## Dos tipos de tarjeta

- **Con ficha de datos** (tienen `datos.json`): se arman solas a partir de esa
  ficha. Desde Luciana Belén en adelante.
- **Hechas a mano** (sin `datos.json`): Madeleine Saint Martin y las cinco de
  la familia. Se modifican editando directamente su `index.html`.

## Modificar una tarjeta

1. Cambiar lo que haga falta en `<carpeta>/datos.json`.
2. Ejecutar `python3 herramientas/generar.py` (rehace la tarjeta y el panel).
3. Guardar los cambios en GitHub. En uno o dos minutos la tarjeta publicada
   muestra lo nuevo; quien la tenga instalada lo ve al volver a abrirla.

## Crear una tarjeta nueva

1. Copiar la carpeta de la tarjeta que más se parezca y darle otro nombre
   (minúsculas, sin acentos ni espacios: `nombre-apellido`).
2. Cambiar `datos.json`, la foto y los íconos.
3. Ejecutar `python3 herramientas/generar.py`.

## Lo que no hay que cambiar

El nombre de la cuenta, el del repositorio y el de cada carpeta forman la
dirección de la tarjeta. Si alguno cambia, dejan de funcionar los QR impresos
y las tarjetas ya instaladas en los teléfonos.

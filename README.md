# Tengo Hambre

**A dónde ir cuando tienes hambre** — guía personal de restaurantes extraída de Google Maps, con platos recomendados generados por IA.

## Qué es

Web estática de un solo archivo (`index.html`) que muestra los restaurantes recomendados por Zaswear en Barcelona, Utrecht y Amsterdam. Los datos vienen del Google Takeout personal y los platos recomendados los genera Claude Haiku y se guardan en `platos.json`.

## Stack

- HTML5 + CSS + vanilla JS — sin frameworks
- Claude Haiku (`claude-haiku-4-5-20251001`) — para generar platos por restaurante
- Python 3 — script de generación por batch (`generar_platos.py`)
- Google Fonts (Playfair Display + Plus Jakarta Sans)

## Archivos

```
tengohambre/
├── index.html          ← Toda la web en un solo archivo
├── platos.json         ← Platos recomendados por restaurante (generados por IA)
├── generar_platos.py   ← Script para generar/actualizar platos.json
├── .env                ← API key de Anthropic (NO se sube a git)
└── .gitignore          ← Excluye .env
```

## Datos

312 restaurantes en 3 ciudades:
- **Barcelona** — 238 sitios
- **Utrecht** — 53 sitios
- **Amsterdam** — 9 sitios (aprox.)

Extraídos del Google Takeout (Reseñas.json + Sitios_guardados.json). Solo establecimientos de comida/bebida dentro de la ciudad (filtrando por código postal).

## Generar platos.json

```bash
# 1. Pon tu API key en .env
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# 2. Lanza el script (reanuda automáticamente si se interrumpe)
python3 generar_platos.py

# 3. Para probar solo una ciudad
python3 generar_platos.py --city Barcelona
```

El script guarda progreso en `platos.json` tras cada restaurante, por lo que si se interrumpe continúa donde lo dejó.

## Funcionalidades

- Tabs por ciudad con tema de color propio
- Búsqueda de texto en tiempo real
- Filtro por barrio
- Sección "Qué pedir" por restaurante (desde `platos.json`)
- Botón "Mapa Google" — descarga un KML importable en [Google My Maps](https://www.google.com/mymaps)
- Enlace directo a Google Maps por restaurante

## Añadir un restaurante nuevo

### Opción A — desde la propia web (recomendado)

Abre `index.html` en el navegador y pulsa el botón **+** (abajo a la izquierda). Rellena el formulario:

| Campo | Ejemplo |
|-------|---------|
| Nombre | `Bar del Pla` |
| Dirección | `Carrer de la Montcada 2, Barcelona` |
| Ciudad | Barcelona / Utrecht / Amsterdam |
| Barrio | `Gótic` |
| URL Google Maps | pega la URL del lugar en Google Maps |
| Qué pedir | `Croquetes, Patates braves, Vermut` (separado por comas) |

El restaurante aparece al instante y se guarda en el navegador (localStorage). Si recargas la página sigue ahí.

> **Limitación:** los restaurantes añadidos desde el formulario solo se guardan en ese navegador. Para hacerlos permanentes, sigue la Opción B.

---

### Opción B — editar el HTML directamente (permanente)

1. Abre `index.html` en un editor de texto y busca `const RESTAURANTS = [`.
2. Añade una entrada al principio o al final del array:

```js
{"n":"Bar del Pla","a":"Carrer de la Montcada 2, 08003 Barcelona, España","c":"Barcelona","h":"Gótic","r":5,"u":"https://maps.google.com/?cid=...","s":"review"}
```

Campos:

| Clave | Descripción |
|-------|-------------|
| `n` | Nombre del restaurante |
| `a` | Dirección completa (con código postal y país) |
| `c` | Ciudad: `Barcelona`, `Utrecht` o `Amsterdam` |
| `h` | Barrio (aparece como chip en la tarjeta) |
| `r` | Rating original — usar `5` para cualquier nuevo sitio |
| `u` | URL de Google Maps |
| `s` | Fuente: `"review"` si lo has visitado, `"saved"` si es pendiente |

3. Guarda el archivo.
4. Para añadir los platos "Qué pedir" con IA, ejecuta:

```bash
python3 generar_platos.py --city Barcelona
```

El script detecta los restaurantes sin platos y los procesa solos. Al terminar actualiza el HTML automáticamente.

---

## Despliegue

El archivo `index.html` + `platos.json` son suficientes para cualquier hosting estático (GitHub Pages, Netlify, Vercel, etc.). No hay build step.

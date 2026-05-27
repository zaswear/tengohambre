# Tengo Hambre — Guía personal de restaurantes de Zaswear

## Qué es esto

Web estática interactiva que muestra los restaurantes recomendados por Zaswear, extraídos de su exportación personal de Google Maps (Google Takeout).

El archivo final es `index.html` — un único HTML autocontenido sin dependencias externas salvo Google Fonts.

---

## Origen de los datos

Los datos vienen de dos archivos JSON del Google Takeout de Zaswear:

- **`Reseñas.json`** — Sitios reseñados en Google Maps. Formato GeoJSON (`FeatureCollection`). Cada `Feature` tiene `properties.location.name`, `properties.location.address`, `properties.five_star_rating_published` (0–5), y `properties.google_maps_url`.
- **`Sitios_guardados.json`** — Sitios guardados (favoritos) sin reseña. Mismo formato GeoJSON pero sin campo de rating.

### Criterios de filtrado aplicados

- Solo sitios dentro de la ciudad (no provincia). Barcelona: código postal 08001–08080. Utrecht y Amsterdam: por nombre de ciudad en la dirección postal holandesa.
- Solo establecimientos de comida/bebida — se filtran farmacias, gimnasios, hoteles, cines, tiendas, museos, parques, etc.
- Ratings no se muestran — todos los sitios son recomendados por igual.

### Resultado actual

| Ciudad | Sitios |
|--------|--------|
| Barcelona | 240 |
| Utrecht | 53 |
| Amsterdam | 9 |
| **Total** | **302** |

---

## Estructura de la web

Archivo único: `index.html`

### Secciones

1. **Header** — Título "Tengo Hambre", subtítulo "A dónde ir cuando tienes hambre", tabs de ciudad.
2. **City hero** — Descripción y estadísticas de la ciudad activa.
3. **Barra de controles** (sticky) — Buscador + chips de filtro por barrio + contador + botón "Mapa Google".
4. **Grid "Todos los sitios"** — Una sola sección con todos los restaurantes de la ciudad activa.
5. **Footer** — Créditos.

### Tarjeta de restaurante

Cada tarjeta muestra:
- Nombre (Playfair Display serif)
- Barrio/distrito (chip)
- Dirección (simplificada, sin país)
- **Sección "Qué pedir"** — 4 platos desde `platos.json`
- Enlace a Google Maps

### Sistema de platos

Los platos vienen de `platos.json`, cargado con `fetch('./platos.json')` al arrancar la página.

Formato de `platos.json`:
```json
{"RestaurantName|CityName": ["plato1", "plato2", "plato3", "plato4"], ...}
```

Generado con `generar_platos.py` usando Claude Haiku. No requiere API key en el cliente.

### Botón "Mapa Google"

Genera y descarga un archivo `.kml` con todos los restaurantes de la ciudad activa. El usuario puede importarlo en [Google My Maps](https://www.google.com/mymaps) para ver todos los pins en el mapa.

---

## Diseño visual

- **Paleta**: crema `#F5F0E8`, tinta `#1A1208`, terra cotta `#C4501A` (Barcelona), naranja `#D0621E` (Utrecht), ámbar `#C07028` (Amsterdam)
- **Tipografías**: Playfair Display (títulos, nombres), Plus Jakarta Sans (cuerpo)
- **Estética**: editorial, cálida, mediterránea
- **Responsive**: grid fluido `repeat(auto-fill, minmax(300px, 1fr))`

---

## Datos de restaurante (formato compacto JS)

```js
{n, a, c, h, r, u, s}
// n = nombre, a = dirección, c = ciudad, h = barrio (hood)
// r = rating original (0/4/5) — no se muestra pero está en los datos
// u = google_maps_url, s = fuente (source: "review"/"saved")
```

---

## Generar / actualizar platos.json

```bash
# Poner API key en .env (no se sube a git)
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env

# Generar todos (reanuda si se interrumpe)
python3 generar_platos.py

# Solo una ciudad
python3 generar_platos.py --city Barcelona

# Limpiar entradas vacías del cache
python3 generar_platos.py --limpiar
```

---

## Archivos importantes

| Archivo | Descripción |
|---------|-------------|
| `index.html` | Toda la web |
| `platos.json` | Platos por restaurante (generado, se puede subir a git) |
| `generar_platos.py` | Script batch para generar platos.json |
| `.env` | API key Anthropic — **NO subir a git** |
| `.gitignore` | Excluye `.env` |

---

## Cómo añadir restaurantes

Editar el array `const RESTAURANTS = [...]` en el `<script>` del `index.html`:

```js
{n:"Nombre", a:"Dirección, Ciudad", c:"Barcelona", h:"Eixample", r:5, u:"https://maps.google.com/...", s:"review"}
```

Luego regenerar `platos.json` con `python3 generar_platos.py`.

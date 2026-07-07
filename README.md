# 🌶️ Tengo Hambre — ruleta de restaurantes

**¿No sabes dónde comer?** Pulsa el botón, comparte tu ubicación y te manda al
restaurante de mi lista personal **más cercano que esté abierto ahora**, con su
ficha, las fotos de Google Maps y qué pedir.

**URL pública:** https://zaswear.github.io/tengohambre/

---

## Cómo funciona

1. El usuario pulsa **Tengo hambre** y acepta el permiso de **geolocalización**.
2. Se ordenan los restaurantes de la lista por distancia (haversine) usando las
   coordenadas de `restaurants.json`.
3. Entre los más cercanos se saca **uno aleatorio** (ruleta). Se consulta Google
   Places para saber si está **abierto ahora**; si está cerrado, prueba con otro.
4. Se muestra su **ficha**: fotos de Google Maps, distancia, barrio, estado
   abierto/cerrado, "qué pedir" (`platos.json`) y enlace directo a Google Maps.

Todo es HTML/JS vanilla en un único `index.html`. Sin build step.

---

## Archivos

```
tengohambre/
├── index.html          ← Toda la web (ruleta) en un solo archivo
├── restaurants.json    ← Lista de restaurantes con coordenadas (n,a,c,h,r,u,lat,lon)
├── platos.json         ← "Qué pedir" por restaurante (clave "Nombre|Ciudad")
├── geocode.js          ← Geocodifica direcciones → lat/lon (Nominatim, sin key)
├── generar_platos.py   ← Genera/actualiza platos.json con Claude Haiku
└── .gitignore
```

---

## Configuración necesaria (Google Maps Platform)

El estado **"abierto ahora"** y las **fotos** vienen de la **Places API (New)**.
Hace falta una API key propia con billing:

1. En Google Cloud, activa **Places API (New)** y **Maps JavaScript API**.
2. Crea una **API key** y **restríngela por "HTTP referrer"** a tu dominio
   (p. ej. `https://zaswear.github.io/*`) — así es seguro que viaje en el cliente.
3. Pega la clave en `index.html`, en la constante `GOOGLE_MAPS_API_KEY`.

Sin clave la ruleta sigue funcionando por cercanía, pero sin fotos ni horario.

> **Coste:** cada tirada hace hasta `MAX_LOOKUPS` (12) consultas a Places para
> encontrar uno abierto. Ajusta `MAX_LOOKUPS` / `NEAREST_K` en `index.html`.

---

## Regenerar coordenadas

Si añades restaurantes sin `lat`/`lon`, ejecútalo (reanuda si se corta):

```bash
node geocode.js
```

Usa Nominatim (OpenStreetMap, sin API key, máx 1 req/seg). Los que no resuelva
quedan marcados con `geocode_failed` y no aparecen en la ruleta hasta corregirlos.

---

## Datos

~307 restaurantes en Barcelona, Utrecht, Ámsterdam, Madrid y Rotterdam,
extraídos del Google Takeout personal. Los platos recomendados los genera
Claude Haiku (`generar_platos.py`).

---

## Despliegue

Vive en `apps/sites/tengohambre` del monorepo `zaswear/zaswear-projects` y se
espeja a `zaswear/tengohambre` (GitHub Pages) vía `.github/workflows/pages-mirror.yml`.

## 🛡️ Licencia

MIT.

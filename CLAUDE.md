# CLAUDE.md — tengohambre

## Qué es
Ruleta de restaurantes. Pulsas el botón, compartes ubicación y te manda al restaurante **más
cercano que esté abierto ahora** de una lista personal, con ficha, fotos de Google Maps y qué pedir.

**Stack:** HTML + JS vanilla en un único `index.html`. Sin build, sin framework, sin `package.json`.
Se publica en GitHub Pages vía el workflow `pages-mirror.yml`.

## Estructura
```
index.html        ← toda la app
restaurants.json  ← la lista personal (fuente de verdad)
platos.json       ← qué pedir en cada sitio
geocode.js        ← utilidad local para geocodificar direcciones nuevas
generar_platos.py ← script local, no se despliega
```

## ⚠️ La API key de Google Maps es pública

`index.html` lleva `GOOGLE_MAPS_API_KEY` **escrita en el código**, y el sitio está publicado en
`https://zaswear.github.io/tengohambre/`. Cualquiera puede leerla.

Esto es **inevitable** con la Maps JavaScript API: la clave viaja al navegador por diseño. Lo que
no es opcional es la restricción:

> La clave **tiene que estar restringida por referente HTTP** en Google Cloud Console
> (APIs y servicios → Credenciales → Restricciones de aplicación → Sitios web), permitiendo solo
> `zaswear.github.io/*` y `localhost:*`. Sin esa restricción, cualquiera que copie la clave
> consume tu cuota y te la factura a ti.

Conviene además limitar por API (solo Maps JavaScript y Places) y ponerle un presupuesto con
alerta en Google Cloud.

**No intentes "arreglarlo" moviendo la clave a una variable de entorno**: no hay build ni servidor,
así que acabaría igualmente en el HTML servido. La protección va en la consola de Google, no aquí.

## Añadir un restaurante
1. Entrada nueva en `restaurants.json` con `nombre`, `direccion` y coordenadas
2. `node geocode.js` si no tienes las coordenadas (usa Nominatim, sin API key)
3. Los platos recomendados van en `platos.json`, emparejados por nombre

Validar que ambos JSON siguen siendo válidos antes de push: no hay build que lo detecte, el fallo
sale en producción.

/**
 * Geocodifica las direcciones de restaurants.json con Nominatim (OpenStreetMap,
 * sin API key) y añade lat/lon a cada entrada. Guarda tras cada uno, así que si
 * se interrumpe reanuda donde lo dejó (salta los que ya tienen coords).
 *
 *   node geocode.js
 *
 * ToS Nominatim: máx 1 req/seg y User-Agent identificable. Respetado abajo.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const FILE = path.join(HERE, "restaurants.json");
const UA = "tengohambre-geocoder/1.0 (zaswear@gmail.com)";
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function geocode(query) {
  const url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(query)}`;
  const res = await fetch(url, { headers: { "User-Agent": UA } });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  if (!data.length) return null;
  return { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) };
}

// Simplifica la dirección: quita el país final y colapsa espacios.
function simplify(addr) {
  return addr.replace(/,\s*(Países Bajos|España|Netherlands|Spain)\s*$/i, "").trim();
}

async function main() {
  const list = JSON.parse(fs.readFileSync(FILE, "utf8"));
  let done = 0, failed = 0, skipped = 0;

  for (let i = 0; i < list.length; i++) {
    const r = list[i];
    if (typeof r.lat === "number" && typeof r.lon === "number") { skipped++; continue; }

    let coords = null;
    for (const q of [r.a, `${r.n}, ${simplify(r.a)}`, `${simplify(r.a)}, ${r.c}`]) {
      try {
        coords = await geocode(q);
      } catch (err) {
        console.error(`  ! ${r.n}: ${err.message}`);
      }
      await sleep(1100); // respeta el límite de 1 req/seg
      if (coords) break;
    }

    if (coords) {
      r.lat = coords.lat;
      r.lon = coords.lon;
      done++;
      console.log(`✓ [${i + 1}/${list.length}] ${r.n} → ${coords.lat},${coords.lon}`);
    } else {
      r.geocode_failed = true;
      failed++;
      console.log(`✗ [${i + 1}/${list.length}] ${r.n} — sin coords`);
    }
    fs.writeFileSync(FILE, JSON.stringify(list, null, 0)); // guardado incremental
  }

  console.log(`\nHecho. Nuevos: ${done} · fallos: ${failed} · ya tenían: ${skipped}`);
}

main().catch((e) => { console.error("Error crítico:", e); process.exit(1); });

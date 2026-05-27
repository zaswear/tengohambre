#!/usr/bin/env python3
"""
Genera los platos recomendados para cada restaurante usando Claude Haiku.
Guarda el resultado en platos.json (formato: {"Nombre|Ciudad": ["plato1","plato2",...]}).
Reanuda automáticamente si se interrumpe: los restaurantes sin platos se reintentan.

Uso:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 generar_platos.py

Opcionales:
  python3 generar_platos.py --city Barcelona   # solo una ciudad
  python3 generar_platos.py --delay 0.3        # pausa entre llamadas (default: 0.3s)

Limpieza manual (si necesitas borrar los fallidos del cache):
  python3 generar_platos.py --limpiar
"""

import json
import os
import re
import sys
import time
import argparse
import anthropic

# Carga .env si existe (para no tener que exportar la key manualmente)
_env = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env):
    with open(_env) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ[_k.strip()] = _v.strip()

PLATOS_FILE = "platos.json"
HTML_FILE   = "index.html"
MODEL       = "claude-haiku-4-5-20251001"

MAX_AUTH_ERRORS = 3   # si hay N errores 401 seguidos, para el script


def load_restaurants():
    with open(HTML_FILE, encoding="utf-8") as f:
        html = f.read()
    start = html.index("const RESTAURANTS = [")
    end   = html.index("</script>", start)
    ns = {}
    exec(html[start:end].strip().replace("const RESTAURANTS", "RESTAURANTS"), ns)
    return ns["RESTAURANTS"]


def load_cache():
    if os.path.exists(PLATOS_FILE):
        with open(PLATOS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(PLATOS_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def get_dishes(client, name, address):
    prompt = (
        f'For the restaurant "{name}" located at "{address}", '
        f'list exactly 4 signature or typical dishes this place is known for. '
        f'Return ONLY a JSON array of 4 short dish names in Spanish or the '
        f"restaurant's native language. No explanations, no markdown, just "
        f'the JSON array like ["Dish 1","Dish 2","Dish 3","Dish 4"].'
    )
    resp = client.messages.create(
        model=MODEL,
        max_tokens=150,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.content[0].text.strip()
    m = re.search(r'\[[\s\S]*?\]', raw)
    return json.loads(m.group()) if m else []


def limpiar_vacios():
    """Elimina del cache las entradas con lista vacía (para reintentarlas)."""
    cache = load_cache()
    antes = len(cache)
    cache = {k: v for k, v in cache.items() if v}
    save_cache(cache)
    print(f"Limpieza: {antes} entradas → {len(cache)} (eliminados {antes - len(cache)} vacíos)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city",    default=None,  help="Filtrar por ciudad")
    parser.add_argument("--delay",   type=float, default=0.3, help="Pausa entre llamadas (s)")
    parser.add_argument("--limpiar", action="store_true", help="Elimina entradas vacías del cache y sale")
    args = parser.parse_args()

    if args.limpiar:
        limpiar_vacios()
        return

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: necesitas exportar ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    restaurants = load_restaurants()

    # Cache: solo considera "hecho" si tiene platos reales (lista no vacía)
    cache = load_cache()
    done_keys = {k for k, v in cache.items() if v}

    if args.city:
        restaurants = [r for r in restaurants if r["c"] == args.city]
        print(f"Filtrando: solo {args.city} ({len(restaurants)} restaurantes)")

    pending = [r for r in restaurants if f"{r['n']}|{r['c']}" not in done_keys]
    total   = len(restaurants)
    done    = total - len(pending)

    print(f"Total: {total} | Con platos: {done} | Pendientes: {len(pending)}")
    if not pending:
        print("✓ Nada que hacer. platos.json ya está completo.")
        return

    errors = 0
    auth_errors_consecutive = 0

    for i, r in enumerate(pending, 1):
        key  = f"{r['n']}|{r['c']}"
        pct  = int(100 * (done + i) / total)
        print(f"[{done+i}/{total} {pct}%] {r['n'][:52]}", end=" ", flush=True)

        try:
            dishes = get_dishes(client, r["n"], r["a"])
            if dishes:
                cache[key] = dishes
                save_cache(cache)
                auth_errors_consecutive = 0
                print(f"→ {dishes}")
            else:
                # Respuesta vacía: no guardar, se reintentará
                print("→ (respuesta vacía, se reintentará)")

        except anthropic.RateLimitError:
            print("→ rate limit, espera 15s...")
            time.sleep(15)
            try:
                dishes = get_dishes(client, r["n"], r["a"])
                if dishes:
                    cache[key] = dishes
                    save_cache(cache)
                    print(f"  reintento OK → {dishes}")
                else:
                    print("  reintento vacío")
            except Exception as e2:
                print(f"  fallo en reintento: {e2}")
                errors += 1

        except anthropic.AuthenticationError:
            print("→ ERROR 401 — API key inválida o sin créditos.")
            auth_errors_consecutive += 1
            errors += 1
            if auth_errors_consecutive >= MAX_AUTH_ERRORS:
                print(f"\nDemasiados errores 401 consecutivos. Parando.")
                print(f"Progreso guardado: {len([v for v in cache.values() if v])} restaurantes con platos.")
                print(f"\nSolución: recarga créditos en console.anthropic.com y vuelve a correr el script.")
                print(f"Los restaurantes sin platos se reintentarán automáticamente.")
                break

        except Exception as e:
            print(f"→ ERROR: {str(e)[:80]}")
            errors += 1

        time.sleep(args.delay)

    total_ok = len([v for v in cache.values() if v])
    print(f"\n✓ {total_ok}/{total} restaurantes con platos. Errores: {errors}")
    if errors:
        print("  Vuelve a correr el script cuando tengas créditos — continuará desde donde paró.")
    embed_platos_in_html(cache)


def embed_platos_in_html(cache):
    """Embebe el contenido de platos.json directamente en index.html como variable JS."""
    html_file = os.path.join(os.path.dirname(__file__), HTML_FILE)
    if not os.path.exists(html_file):
        print(f"  (no se encontró {HTML_FILE} para embeber platos)")
        return
    with open(html_file, encoding="utf-8") as f:
        html = f.read()

    platos_json = json.dumps(cache, ensure_ascii=False, separators=(",", ":"))

    # Replace the embedded PLATOS variable
    import re
    new_html = re.sub(
        r'let PLATOS = \{[^;]*\};',
        f'let PLATOS = {platos_json};',
        html,
        count=1,
        flags=re.DOTALL,
    )
    if new_html == html:
        print(f"  (no se pudo actualizar PLATOS en {HTML_FILE} — patrón no encontrado)")
        return
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(new_html)
    print(f"  ✓ PLATOS actualizado en {HTML_FILE}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Importe tout le contenu du site Cargo anthony-vivien.com dans ce dépôt.

- Pages  -> data/cargo.json  (contenu HTML Cargo, CSS, liste des médias)
- Médias -> site/media/<hash>.webp (images, max 2000 px de large, WebP q85)
            site/media/<hash>.gif / .mp4 (copiés tels quels)
- Vidéos YouTube : uniquement référencées dans data/cargo.json (url, url_id, url_thumb)

Prérequis : accès réseau à api.cargo.site et freight.cargo.site
            pip install requests pillow

Usage : python3 scripts/import_cargo.py
Relançable : les médias déjà téléchargés sont sautés.
"""
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import requests
from PIL import Image

SITE_ID = 3183960
API = f"https://api.cargo.site/v1/pages/{SITE_ID}/url/"
FREIGHT = "https://freight.cargo.site"
MAX_W = 2000
WEBP_Q = 85

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
MEDIA = ROOT / "site" / "media"

# Pages de départ : sections du menu + éléments épinglés (menu, header mobile, footer).
# Les pages projets (arcane, maiko…) sont découvertes en suivant les liens.
START = [
    "index", "tv_page", "commercials_page-1", "game_page", "personal_page", "about",
    "left-nav-—-desktop", "header---mobile", "footer",
]
# Liens du gabarit Cargo par défaut, inutilisés sur le site
IGNORE = {
    "Aenean-Facili", "Mauris-Lan", "Quisque-Vita-Est", "Cras-Temp", "Euismod-Faucibus",
    "Quam-Lora", "Curabitur", "Mauris-Facili", "Nam-Facibu-Est", "information", "contact-form",
}

session = requests.Session()
session.headers["User-Agent"] = "anthony-vivien-site-import/1.0"


def get_json(url, tries=3):
    for i in range(tries):
        r = session.get(url, timeout=30)
        if r.status_code == 404:
            return None
        if r.ok:
            return r.json()
        time.sleep(1 + i)
    r.raise_for_status()


def fetch_pages():
    pages, queue, seen = {}, list(START), set(START) | IGNORE
    while queue:
        purl = queue.pop(0)
        j = get_json(API + quote(purl, safe=""))
        if not j:
            print(f"  ! page introuvable : {purl}")
            continue
        p = j.get("data", j)
        pages[purl] = p
        print(f"  page {purl:28s} {len(p.get('content') or ''):6d} car. {len(p.get('media') or []):3d} médias")
        for href in re.findall(r'href="([^"#:]+)"', p.get("content") or ""):
            if href not in seen and not href.startswith(("http", "mailto")):
                seen.add(href)
                queue.append(href)
    return pages


def media_url(m):
    name = quote(m["name"])
    if m.get("is_video") or m.get("file_type") == "gif" or (m.get("width") or 0) <= MAX_W:
        return f"{FREIGHT}/t/original/i/{m['hash']}/{name}"
    return f"{FREIGHT}/w/{MAX_W}/q/{WEBP_Q}/i/{m['hash']}/{name}"


def out_path(m):
    if m.get("is_video"):
        return MEDIA / f"{m['hash']}.mp4"
    if m.get("file_type") == "gif":
        return MEDIA / f"{m['hash']}.gif"
    return MEDIA / f"{m['hash']}.webp"


def download(m):
    dest = out_path(m)
    if dest.exists() and dest.stat().st_size > 0:
        return dest.name, "déjà là"
    r = session.get(media_url(m), timeout=120)
    r.raise_for_status()
    if dest.suffix == ".webp":
        img = Image.open(BytesIO(r.content))
        img = img.convert("RGBA") if img.mode in ("P", "LA", "RGBA") else img.convert("RGB")
        if img.width > MAX_W:
            img = img.resize((MAX_W, round(img.height * MAX_W / img.width)), Image.LANCZOS)
        img.save(dest, "WEBP", quality=WEBP_Q, method=6)
    else:
        dest.write_bytes(r.content)
    return dest.name, f"{dest.stat().st_size // 1024} Ko"


def main():
    DATA.mkdir(exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)

    print("1/3 Pages…")
    pages = fetch_pages()

    print("2/3 Inventaire des médias…")
    by_hash, used = {}, []
    for p in pages.values():
        for m in p.get("media") or []:
            by_hash[m["hash"]] = m
        for h in re.findall(r'hash="([^"]+)"', p.get("content") or ""):
            if h not in used:
                used.append(h)
    media = [by_hash[h] for h in used if h in by_hash]
    files = [m for m in media if not m.get("is_url")]
    print(f"  {len(media)} médias utilisés dont {len(files)} fichiers, {len(media) - len(files)} vidéos en ligne")

    keep = ("id", "title", "purl", "content", "local_css", "pin", "overlay", "thumbnail", "thumb_media_id")
    data = {
        "site_id": SITE_ID,
        "pages": {k: {f: p.get(f) for f in keep} | {"media": [m["hash"] for m in p.get("media") or []]}
                  for k, p in pages.items()},
        "media": {m["hash"]: {
            "name": m.get("name"), "width": m.get("width"), "height": m.get("height"),
            "type": m.get("file_type"), "is_video": m.get("is_video"), "is_url": m.get("is_url"),
            "url": m.get("url"), "url_id": m.get("url_id"), "url_type": m.get("url_type"),
            "url_thumb": m.get("url_thumb"), "display_name": m.get("display_name"),
            "file": None if m.get("is_url") else f"/media/{out_path(m).name}",
        } for m in media},
    }
    (DATA / "cargo.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  -> {DATA / 'cargo.json'}")

    print("3/3 Téléchargement des médias…")
    errors = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(download, m): m for m in files}
        for i, f in enumerate(futs, 1):
            m = futs[f]
            try:
                name, info = f.result()
                print(f"  [{i:3d}/{len(files)}] {name} ({info})")
            except Exception as e:  # noqa: BLE001
                errors.append(f"{m['name']}: {e}")
                print(f"  [{i:3d}/{len(files)}] ERREUR {m['name']}: {e}")

    total = sum(p.stat().st_size for p in MEDIA.iterdir())
    print(f"\nTerminé : {len(pages)} pages, {len(files) - len(errors)}/{len(files)} fichiers, {total / 1e6:.1f} Mo dans site/media/")
    if errors:
        print("Erreurs :", *errors, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main()

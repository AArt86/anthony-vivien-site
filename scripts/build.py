#!/usr/bin/env python3
"""
Génère le site statique (version améliorée) à partir de data/cargo.json.

    python3 scripts/build.py

Entrée  : data/cargo.json (export Cargo) + site/media/ (images WebP, GIF, MP4)
Sortie  : site/*.html, site/sitemap.xml, site/robots.txt
"""
import html
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = json.loads((ROOT / "data" / "cargo.json").read_text(encoding="utf-8"))
PAGES = DATA["pages"]
MEDIA = {m["hash"]: m for m in DATA["media"]}

BASE_URL = "https://www.anthony-vivien.com"
NAME = "Anthony Vivien"
TAGLINE = "Concept Artist · Visual Development · Art Direction"
# Adresse de contact : reprise telle quelle du menu du site Cargo
CONTACT = re.search(r'mailto:([^"]+)"', PAGES["left-nav-—-desktop"]["content"]).group(1)
SOCIAL = {
    "Instagram": "https://www.instagram.com/_ayvn_/",
    "LinkedIn": "https://www.linkedin.com/in/anthonyvivien/",
    "Behance": "https://www.behance.net/anthonyvivien",
}

# Sections : purl Cargo -> (libellé menu, titre de page, description SEO)
SECTIONS = {
    "tv_page": ("TV", "TV & Animation", "TV series and animation work by Anthony Vivien: visual development, colorscripts, key art and art direction for Arcane, 101 Dalmatian Street, Pfffirates and more."),
    "commercials_page-1": ("Commercials", "Commercials", "Concept art and pitch-deck visuals created by Anthony Vivien for advertising campaigns and brands."),
    "game_page": ("Games", "Video Games", "Video game art direction, visual development and level design by Anthony Vivien, co-founder of Brain Up studio: The Travelling Land, Maiko, Soul of Kaeru."),
    "personal_page": ("Personal", "Personal Art", "Personal paintings and illustrations by Anthony Vivien."),
    "about": ("About", "About", "Anthony Vivien is a French concept artist and art director with more than 15 years in animation and video games. Get in touch for visual development and art direction."),
}
NAV = ["tv_page", "commercials_page-1", "game_page", "personal_page", "about"]
SKIP = {"index", "left-nav-—-desktop", "header---mobile", "footer", "nav-—-mobile"}

ICONS = {
    "instagram": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="3" width="18" height="18" rx="5" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.4" cy="6.6" r="1.2" fill="currentColor"/></svg>',
    "linkedin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4.98 3.5A2.5 2.5 0 1 1 5 8.5a2.5 2.5 0 0 1-.02-5zM3 9.75h4V21H3zM9.5 9.75h3.8v1.6h.06c.53-1 1.84-2.06 3.79-2.06 4.05 0 4.8 2.66 4.8 6.12V21h-4v-4.9c0-1.17-.02-2.68-1.63-2.68-1.64 0-1.89 1.28-1.89 2.6V21h-4z"/></svg>',
    "behance": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M8.2 11.3c.9-.4 1.5-1.2 1.5-2.4C9.7 6.6 8 6 6 6H1v12h5.2c2.1 0 4.1-1 4.1-3.4 0-1.5-.7-2.7-2.1-3.3zM3.3 8h2.3c.9 0 1.7.2 1.7 1.2s-.6 1.3-1.5 1.3H3.3zm2.5 8H3.3v-3.3h2.6c1 0 1.8.4 1.8 1.6 0 1.3-.9 1.7-1.9 1.7zM17.8 8.8c-2.9 0-4.8 2.1-4.8 4.8 0 2.8 1.8 4.8 4.8 4.8 2.3 0 3.8-1 4.5-3.2h-2.3c-.3.8-1.2 1.2-2.1 1.2-1.6 0-2.4-.9-2.4-2.4h6.9c.1-3-1.5-5.2-4.6-5.2zm-2.3 3.9c.1-1.2.9-2 2.2-2s2 .8 2.1 2zM15.3 6.5h5.3v1.3h-5.3z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2" fill="none" stroke="currentColor" stroke-width="1.8"/><path d="m4 7 8 6 8-6" fill="none" stroke="currentColor" stroke-width="1.8"/></svg>',
    "arrow-left": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m6-6-6 6 6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "arrow-right": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14m-6-6 6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "north-east-arrow": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 17 17 7M8 7h9v9" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "palette": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M12 3a9 9 0 1 0 0 18c1.1 0 1.6-.8 1.6-1.6 0-.9-.7-1.3-.7-2.1 0-.9.7-1.5 1.6-1.5H17a4 4 0 0 0 4-4C21 6.9 17 3 12 3z"/><circle cx="7.5" cy="11" r="1.2" fill="currentColor"/><circle cx="10" cy="7.3" r="1.2" fill="currentColor"/><circle cx="14.5" cy="7.3" r="1.2" fill="currentColor"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.8" d="M12 21s-6.5-6.1-6.5-11a6.5 6.5 0 0 1 13 0c0 4.9-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.3" fill="currentColor"/></svg>',
    "play": '<svg viewBox="0 0 68 48" aria-hidden="true"><path d="M66.5 7.7a8.5 8.5 0 0 0-6-6C55.3.3 34 .3 34 .3s-21.3 0-26.5 1.4a8.5 8.5 0 0 0-6 6C.1 13 .1 24 .1 24s0 11 1.4 16.3a8.5 8.5 0 0 0 6 6C12.7 47.7 34 47.7 34 47.7s21.3 0 26.5-1.4a8.5 8.5 0 0 0 6-6C67.9 35 67.9 24 67.9 24s0-11-1.4-16.3z" fill="#900086"/><path d="M27 34V14l18 10z" fill="#fff"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>',
}
ICON_ALIAS = {"mail-2": "mail", "leftwards-arrow-5": "arrow-left", "menu-5": "menu"}


def esc(s):
    return html.escape(s or "", quote=True)


def text_of(node):
    return re.sub(r"\s+", " ", node.get_text(" ") if hasattr(node, "get_text") else str(node)).strip()


# ------------------------------------------------------------ médias
def img_tag(m, alt, eager=False, sizes="(min-width: 900px) 60vw, 100vw"):
    h = m["hash"]
    load = "eager" if eager else "lazy"
    if m.get("ext") == "gif":
        return (f'<img src="/media/{h}.gif" alt="{esc(alt)}" width="{m.get("width") or ""}" '
                f'height="{m.get("height") or ""}" loading="{load}" decoding="async">')
    w, hgt = m.get("w") or m.get("width"), m.get("h") or m.get("height")
    big = (w or 0) > 800
    src = f"/media/t/{h}.webp" if big else f"/media/{h}.webp"
    srcset = f' srcset="/media/t/{h}.webp 800w, /media/{h}.webp {w}w" sizes="{sizes}"' if big else ""
    return f'<img src="{src}"{srcset} alt="{esc(alt)}" width="{w}" height="{hgt}" loading="{load}" decoding="async">'


def media_html(m, alt, zoom, link=None, scale=None, caption_html=""):
    style = ""
    if scale and scale.endswith("%"):
        try:
            v = float(scale[:-1])
            if v < 98:
                style = f' style="--w:{v:.0f}%"'
        except ValueError:
            pass
    if m.get("is_url") and m.get("url_type") == "youtube":
        vid = m.get("url_id")
        inner = (f'<button class="yt" data-id="{esc(vid)}" aria-label="Play video: {esc(m.get("display_name"))}">'
                 f'<img src="https://i.ytimg.com/vi/{esc(vid)}/hqdefault.jpg" alt="" loading="lazy" decoding="async" width="480" height="360">'
                 f'<span class="yt-play">{ICONS["play"]}</span></button>')
        cap = caption_html or f'<figcaption class="caption">{esc(m.get("display_name"))}</figcaption>'
        return f'<figure class="media video-embed"{style}>{inner}{cap}</figure>'
    if m.get("is_url"):
        return f'<p><a href="{esc(m.get("url"))}" target="_blank" rel="noopener">{esc(m.get("display_name"))}</a></p>'
    if m.get("is_video"):
        inner = (f'<video src="/media/{m["hash"]}.mp4" autoplay muted loop playsinline preload="metadata" '
                 f'width="{m.get("width")}" height="{m.get("height")}" aria-label="{esc(alt)}"></video>')
    else:
        inner = img_tag(m, alt)
        if link:
            inner = f'<a href="{esc(link)}" class="card-link">{inner}</a>'
        elif zoom:
            full = f'/media/{m["hash"]}.{m.get("ext") or "webp"}'
            inner = f'<a href="{full}" class="lb" data-caption="{esc(alt)}">{inner}</a>'
    return f'<figure class="media"{style}>{inner}{caption_html}</figure>'


# -------------------------------------------------- traduction Cargo -> HTML
def internal(href):
    if not href or href.startswith(("http", "mailto:", "#", "/")):
        return href
    return "/" if href == "index" else "/" + href


def translate(content, page_title):
    soup = BeautifulSoup(content or "", "html.parser")

    # blocs « retour / home » de Cargo : remplacés par notre propre navigation
    for a in soup.select("a.icon-link"):
        icon = a.find("text-icon")
        if icon and icon.get("icon") == "leftwards-arrow-5":
            box = a.find_parent("div") or a
            box.decompose()
    for a in soup.find_all("a"):
        if text_of(a).lower() in {"home", "return", "index"} and a.get("href") in {"index", "tv_page", "game_page"}:
            a.decompose()

    for t in soup.find_all(True):
        for attr in ["data-bcup-haslogintext", "rel", "uses"]:
            t.attrs.pop(attr, None)
        st = t.attrs.pop("style", "")
        if "text-align: center" in st:
            t["class"] = (t.get("class") or []) + ["center"]
        elif "text-align: right" in st:
            t["class"] = (t.get("class") or []) + ["right"]
        if t.name == "a" and t.get("href"):
            t["href"] = internal(t["href"])
            if t["href"].startswith("http"):
                t["target"] = "_blank"
                t["rel"] = "noopener"

    for icon in soup.find_all("text-icon"):
        key = ICON_ALIAS.get(icon.get("icon"), icon.get("icon"))
        icon.replace_with(BeautifulSoup(f'<span class="ico">{ICONS.get(key, "")}</span>', "html.parser"))

    for mi in soup.find_all("media-item"):
        m = MEDIA.get(mi.get("hash"))
        if not m:
            mi.decompose()
            continue
        cap = mi.find("figcaption")
        cap_html, alt = "", page_title
        if cap:
            alt = text_of(cap) or page_title
            cap_html = f'<figcaption class="caption">{cap.decode_contents()}</figcaption>'
        zoom = "zoomable" in (mi.get("class") or []) and mi.get("disable-zoom") != "true"
        link = internal(mi.get("href")) if mi.get("href") else None
        mi.replace_with(BeautifulSoup(media_html(m, alt, zoom, link, mi.get("scale"), cap_html), "html.parser"))

    for g in soup.find_all("gallery-grid"):
        cols, mcols = g.attrs.get("columns", "3"), g.attrs.get("mobile-columns", "1")
        g.name = "div"
        g.attrs = {"class": ["g-grid"], "style": f"--cols:{cols};--mcols:{mcols}"}
    for g in soup.find_all("gallery-columnized"):
        g.name = "div"
        g.attrs = {"class": ["g-masonry"]}
    for g in soup.find_all("gallery-freeform"):
        g.name = "div"
        g.attrs = {"class": ["g-grid"], "style": "--cols:3;--mcols:1"}

    for cs in soup.find_all("column-set"):
        units = cs.find_all("column-unit", recursive=False)
        default = 12 // max(1, len(units))
        stack = cs.get("mobile-stack") != "false"
        cs.name = "div"
        cs.attrs = {"class": ["cols"] + ([] if stack else ["no-stack"])}
        for u in units:
            span = u.get("span") or default
            u.name = "div"
            empty = not text_of(u) and not u.find(["img", "video", "button", "figure"])
            u.attrs = {"class": ["col"] + (["empty"] if empty else []), "style": f"--span:{span}"}

    for b in soup.find_all(["b", "u", "i", "span"]):
        if b.parent is None:
            continue
        if not text_of(b) and not b.find(["img", "svg", "figure"]):
            if b.find("br"):
                b.unwrap()
            else:
                b.decompose()
    for b in soup.find_all("b"):
        if b.find(["h1", "h2", "div", "figure"]):
            b.unwrap()
    for h in soup.find_all(["h1", "h2"]):
        for br in h.find_all("br"):
            br.decompose()
        if not text_of(h) and not h.find("svg"):
            h.decompose()

    out = str(soup)
    out = re.sub(r"(?:\s*<br\s*/?>\s*){3,}", "<br><br>", out)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out


# --------------------------------------------------------------- données
def first_h1(content):
    h = BeautifulSoup(content or "", "html.parser").find("h1")
    return text_of(h) if h and text_of(h) else None


def first_image(content):
    for h in re.findall(r'hash="([^"]+)"', content or ""):
        m = MEDIA.get(h)
        if m and m.get("ext") == "webp":
            return m
    return None


def describe(content, fallback):
    soup = BeautifulSoup(content or "", "html.parser")
    for t in soup.find_all(["h1", "h2", "figcaption", "span"]):
        if t.parent is not None and (t.name != "span" or "caption" in (t.get("class") or [])):
            t.decompose()
    txt = re.sub(r"\s+([,.;:!?])", r"\1", text_of(soup))
    if len(txt) < 60:
        return fallback
    return (txt[:157].rsplit(" ", 1)[0] + "…") if len(txt) > 157 else txt


def grid_items(purl):
    """Projets d'une page catégorie, dans l'ordre : [(href, titre, rôle, hash)]"""
    soup = BeautifulSoup(PAGES[purl]["content"], "html.parser")
    items = []
    for mi in soup.select("gallery-grid media-item"):
        cap = mi.find("figcaption")
        title_el = cap.find(class_="menu-text") if cap else None
        title = text_of(title_el) if title_el else ""
        if title_el:
            title_el.extract()
        meta = text_of(cap) if cap else ""
        items.append((mi.get("href"), title, meta, mi.get("hash")))
    return items


CATEGORY_OF = {}
for _cat in ("tv_page", "game_page"):
    for _href, *_ in grid_items(_cat):
        if _href and _href in PAGES:
            CATEGORY_OF[_href] = _cat

AVATAR = re.search(r'hash="([^"]+)"', PAGES["left-nav-—-desktop"]["content"]).group(1)
OG_DEFAULT = re.search(r'hash="([^"]+)"', PAGES["index"]["content"]).group(1)
VERSION = "3"

PERSON_LD = {
    "@context": "https://schema.org", "@type": "Person", "name": NAME,
    "jobTitle": "Concept Artist & Art Director", "url": BASE_URL + "/",
    "sameAs": list(SOCIAL.values()) + ["https://x.com/_ayvn_"],
    "knowsAbout": ["Concept art", "Visual development", "Art direction", "Colorscript", "Level design", "Animation", "Video games"],
}


# --------------------------------------------------------------- gabarit
def nav_html(active):
    items = []
    for p in NAV:
        cur = ' aria-current="page"' if (p == active or CATEGORY_OF.get(active) == p) else ""
        items.append(f'<li><a href="/{p}"{cur}>{SECTIONS[p][0]}</a></li>')
    socials = "".join(
        f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}" class="ico">{ICONS[n.lower()]}</a>'
        for n, u in SOCIAL.items()
    )
    return f"""<header class="site-header">
  <a class="brand" href="/" aria-label="{NAME}, home">
    <img src="/media/{AVATAR}.webp" alt="" width="48" height="29">
    <span>Anthony <br>Vivien</span>
  </a>
  <button class="menu-toggle" aria-expanded="false" aria-controls="site-nav" aria-label="Menu">{ICONS["menu"]}</button>
  <nav id="site-nav" class="site-nav" aria-label="Main">
    <ul>{''.join(items)}</ul>
    <div class="nav-foot">
      <a class="mail" href="mailto:{CONTACT}">{ICONS["mail"]}<span>{CONTACT}</span></a>
      <div class="socials">{socials}</div>
      <p class="copy">© 2026 {NAME}</p>
    </div>
  </nav>
</header>"""


def page(path, title, desc, body, active=None, og_image=None, ld=None, extra_class=""):
    url = BASE_URL + ("/" if path == "index" else f"/{path}")
    full_title = title if path == "index" else f"{title} — {NAME}"
    og = f"{BASE_URL}/media/{(og_image or MEDIA[OG_DEFAULT])['hash']}.webp"
    ld_html = f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/media/{AVATAR}.webp">
<link rel="preload" href="/assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/style.css?v={VERSION}">
{ld_html}
</head>
<body class="{extra_class}">
<a class="skip" href="#main">Skip to content</a>
{nav_html(active)}
<main id="main">
{body}
</main>
<script src="/assets/site.js?v={VERSION}" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------- pages
def build_home():
    idx = PAGES["index"]["content"]
    labels = {"tv_page": "TV & Animation", "commercials_page-1": "Commercials", "game_page": "Video Games"}
    cards = []
    first = None
    # Les vignettes Cargo ont le texte incrusté (« TV », « GAMES »…) : on prend des visuels propres
    grid = {h: mh for c in ("tv_page", "game_page") for h, _, _, mh in grid_items(c) if h}
    com_imgs = [h for h in re.findall(r'class="zoomable" hash="([^"]+)"', PAGES["commercials_page-1"]["content"])]
    pick = {"tv_page": grid.get("pfffirates"), "game_page": grid.get("the-travelling-land"),
            "commercials_page-1": com_imgs[0] if com_imgs else None}
    for mi in BeautifulSoup(idx, "html.parser").find_all("media-item"):
        href = mi.get("href")
        m = MEDIA.get(pick.get(href)) or MEDIA[mi["hash"]]
        first = first or m
        cards.append(f'<a class="cat-card" href="/{href}">{img_tag(m, labels.get(href, ""), eager=True, sizes="(min-width: 900px) 33vw, 100vw")}'
                     f'<span class="cat-label">{labels.get(href, "")}<span class="ico">{ICONS["arrow-right"]}</span></span></a>')
    feat_ids = ["arcane", "the-travelling-land", "maiko", "101-dalmatian-street", "soul-of-kaeru", "pfffirates", "orphan-age", "once-your-land"]
    allitems = {h: (t, meta, mh) for c in ("tv_page", "game_page") for h, t, meta, mh in grid_items(c) if h}
    feats = []
    for pid in feat_ids:
        if pid in allitems:
            t, meta, mh = allitems[pid]
            feats.append(f'<a class="proj-card" href="/{pid}">{img_tag(MEDIA[mh], t, sizes="(min-width: 900px) 25vw, 50vw")}'
                         f'<span class="proj-title">{esc(t)}</span><span class="proj-meta">{esc(meta)}</span></a>')
    body = f"""<section class="hero">
  <p class="eyebrow">{TAGLINE}</p>
  <h1>Colourful worlds for <em>animation</em>, <em>advertising</em> &amp; <em>games</em>.</h1>
  <p class="lead">I'm Anthony Vivien, a French concept artist and art director with more than 15 years in the animation industry, from visual development and colorscripts to art direction. Co-founder of the game studio Brain Up, now freelance and open to new creative challenges.</p>
  <p class="cta"><a class="btn" href="mailto:{CONTACT}">Get in touch</a> <a class="btn ghost" href="/about">About me</a></p>
</section>
<section class="cats" aria-label="Work">{''.join(cards)}</section>
<section class="featured">
  <h2 class="section-title">Selected projects</h2>
  <div class="proj-grid">{''.join(feats)}</div>
</section>"""
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": BASE_URL + "/", "author": PERSON_LD}
    return page("index", f"{NAME} — Concept Artist & Art Director",
                "Anthony Vivien, French concept artist and art director: visual development, colorscripts and art direction for animated series (Arcane, 101 Dalmatian Street), commercials and video games.",
                body, og_image=first, ld=ld, extra_class="home")


def build_category(purl):
    label, title, desc = SECTIONS[purl]
    content = re.sub(r'^\s*(?:<br\s*/?>)?\s*<span class="caption">[^<]*</span>', "", PAGES[purl]["content"], count=1)
    inner = translate(content, "Anthony Vivien" if purl == "about" else title)
    if purl == "about":
        inner = re.sub(r'<span class="email">\s*([^<]+?)\s*</span>', r'<a class="email" href="mailto:\1">\1</a>', inner)
    body = f'<header class="page-head"><h1>{esc(title)}</h1></header>\n<div class="cargo sec-{label.lower()}">{inner}</div>'
    return page(purl, title, desc, body, active=purl, og_image=first_image(content),
                ld=PERSON_LD if purl == "about" else None, extra_class=f"section-{label.lower()}")


def build_project(purl, order):
    p = PAGES[purl]
    title = first_h1(p["content"]) or p["title"]
    cat = CATEGORY_OF.get(purl)
    crumbs, prev_next = "", ""
    if cat:
        crumbs = f'<p class="crumbs"><a href="/{cat}">{ICONS["arrow-left"]}{SECTIONS[cat][1]}</a></p>'
        seq = order[cat]
        i = seq.index(purl)
        prv, nxt = seq[i - 1], seq[(i + 1) % len(seq)]

        def label(h):
            return first_h1(PAGES[h]["content"]) or PAGES[h]["title"]
        prev_next = f"""<nav class="prev-next" aria-label="More projects">
  <a href="/{prv}" class="prev">{ICONS["arrow-left"]}<span><small>Previous</small>{esc(label(prv))}</span></a>
  <a href="/{cat}" class="all">All {SECTIONS[cat][0]} projects</a>
  <a href="/{nxt}" class="next"><span><small>Next</small>{esc(label(nxt))}</span>{ICONS["arrow-right"]}</a>
</nav>"""
    body = f'{crumbs}\n<article class="cargo project">{translate(p["content"], title)}</article>\n{prev_next}'
    desc = describe(p["content"], f"{title}: concept art and visual development by Anthony Vivien.")
    ld = {"@context": "https://schema.org", "@type": "CreativeWork", "name": title,
          "creator": {"@type": "Person", "name": NAME}, "url": f"{BASE_URL}/{purl}"}
    return page(purl, title, desc, body, active=purl, og_image=first_image(p["content"]), ld=ld, extra_class="project-page")


def main():
    order = {c: [h for h, *_ in grid_items(c) if h and h in PAGES] for c in ("tv_page", "game_page")}
    out = {"index": build_home()}
    for purl in NAV:
        out[purl] = build_category(purl)
    for purl in PAGES:
        if purl not in SKIP and purl not in SECTIONS:
            out[purl] = build_project(purl, order)
    for name, doc in out.items():
        (SITE / f"{name}.html").write_text(doc, encoding="utf-8")
    urls = "".join(f"<url><loc>{BASE_URL}{'/' if n == 'index' else '/' + n}</loc></url>" for n in out)
    (SITE / "sitemap.xml").write_text(
        f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n', encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    print(f"{len(out)} pages générées")


if __name__ == "__main__":
    main()

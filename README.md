# anthony-vivien.com — site statique

Portfolio d'Anthony Vivien, sorti de Cargo et hébergé **gratuitement** sur **Cloudflare Pages**, avec le code sur **GitHub**.
Seul coût : le nom de domaine (≈ 10 € par an chez Cloudflare Registrar).

## Comment ça marche

```
GitHub (ce dépôt)  ──push──▶  Cloudflare Pages  ──▶  https://www.anthony-vivien.com
```

Chaque `git push` sur `main` met le site en ligne en moins d'une minute.
Chaque autre branche reçoit sa propre adresse d'aperçu, par exemple `https://ameliore.anthony-vivien-site.pages.dev`.

| Réglage Cloudflare Pages | Valeur |
|---|---|
| Framework preset | None |
| Build command | *(vide)* |
| Build output directory | `site` |
| Production branch | `main` |

## Arborescence

```
site/              ← tout ce qui est publié
  index.html       ← accueil (page d'attente pour l'instant)
  404.html
  _headers         ← cache et sécurité (Cloudflare Pages)
  _redirects       ← anciennes URL Cargo → nouvelles
  media/           ← images WebP / GIF / MP4 (rempli par le script d'import)
scripts/
  import_cargo.py  ← récupère pages et médias depuis Cargo
data/
  cargo.json       ← contenu brut des pages Cargo (généré par le script)
GUIDE.md           ← étapes GitHub, Cloudflare et transfert du domaine
```

## Les deux versions

| Branche | Version | Aperçu |
|---|---|---|
| `main` | **Copie fidèle** du site Cargo (devient la production) | `anthony-vivien-site.pages.dev` |
| `ameliore` | **Version améliorée** (SEO, performance, finitions) | `ameliore.anthony-vivien-site.pages.dev` |

On compare les deux aperçus, puis on fusionne celle qu'on garde dans `main`.

## Importer le contenu Cargo

À lancer dans une session qui a accès à `api.cargo.site` et `freight.cargo.site` :

```bash
pip install requests pillow
python3 scripts/import_cargo.py
```

Résultat attendu (inventaire fait le 27/11/2026) : **environ 33 pages**, **292 fichiers** (287 images, 3 GIF, 2 MP4) et **12 vidéos YouTube**.
Tout cela fait **environ 55 Mo** une fois les images converties en WebP, contre 1,4 Go d'originaux sur Cargo.

## Inventaire du site Cargo (référence pour la reconstruction)

- **Site Cargo** : `anthonyvivien`, ID `3183960`
- **Accueil** (`index`) : trois grandes vignettes cliquables à bords arrondis (1.2rem) en disposition libre (TV, COMMERCIALS, GAMES).
- **Menu gauche** (page épinglée, 22 % de la largeur) : logo `IconAv.jpg` + « ANTHONY VIVIEN », puis TV / COMMERCIALS / GAMES / PERSONAL, ABOUT, une icône mail, Instagram, LinkedIn, Behance et « © 2025 ANTHONY VIVIEN. All RIGHTS RESERVED ».
- **TV** (`tv_page`) : grille de 5 colonnes, 16 projets avec titre, rôle et année. 13 pointent vers une page projet : once-your-land, badjelly, 5050-heroes, pfffirates, 101-dalmatian-street, the-world-of-kev, arcane, scareways, luzu, squirrels, muffin-jack, bugs-agency, salesman-pete.
- **COMMERCIALS** (`commercials_page-1`) : texte d'intro + galerie en colonnes de 27 visuels (1 vidéo MP4 en lecture auto, zoom au clic).
- **GAMES** (`game_page`) : texte sur Brain Up + grille de 5 colonnes, 10 jeux : the-travelling-land, maiko, orphan-age, tasty-defenders, soul-of-kaeru, catsdogs, smashescapepickles, party-quest, almost-a-hero, et Dangerous Men (sans page).
- **PERSONAL** (`personal_page`) : images en pleine largeur (65 %) avec l'année en légende (2018 → 2012).
- **ABOUT** (`about`) : photo + texte bio en anglais + email + bandeau de logos clients.
- **Design** : fond blanc, texte `rgba(0,0,0,.85)`, accent violet `#900086` (rgb 144,0,134). Polices Cargo : *Diatype Variable*, *Favorit Variable*, *Diatype Mono Variable* (Dinamo) et Inter.
  ⚠️ Diatype et Favorit sont des polices commerciales fournies sous licence par Cargo. Hors de Cargo, il faut soit acheter la licence web chez Dinamo, soit prendre une alternative gratuite proche : **Inter** ou **Geist** pour Diatype, **Space Grotesk** pour Favorit, **Geist Mono** pour Diatype Mono.
- **Liens** : anton.vivien@gmail.com, instagram.com/_ayvn_, x.com/_ayvn_, linkedin.com/in/anthonyvivien, behance.net/anthonyvivien

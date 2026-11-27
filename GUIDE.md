# Guide de migration : Cargo → GitHub + Cloudflare Pages

Objectif : site gratuit, seul le nom de domaine reste payant (environ 10 à 15 € par an).
**Règle d'or : on ne résilie Cargo qu'à la toute fin (étape 6).** C'est Cargo qui détient le domaine aujourd'hui.

---

## Étape 1 : créer le dépôt GitHub (2 min)

1. Va sur <https://github.com/new>.
2. Remplis :
   - **Repository name** : `anthony-vivien-site`
   - **Private** (Cloudflare Pages fonctionne avec un dépôt privé)
   - Ne coche **rien** (pas de README, pas de .gitignore, pas de licence) : le dépôt doit être vide.
3. Clique sur **Create repository**.
4. Envoie le contenu de ce dossier. Le plus simple : glisser-déposer tous les fichiers dans **« uploading an existing file »**, ou dans un terminal :

   ```bash
   cd anthony-vivien-site
   git remote add origin https://github.com/AArt86/anthony-vivien-site.git
   git push -u origin main
   git push -u origin ameliore
   ```

## Étape 2 : créer le projet Cloudflare Pages (5 min)

1. Connecte-toi sur <https://dash.cloudflare.com>.
2. Menu **Workers & Pages** → **Create** → onglet **Pages** → **Connect to Git**.
3. Autorise Cloudflare à accéder à GitHub, **uniquement** pour le dépôt `anthony-vivien-site`.
4. Sélectionne `anthony-vivien-site` → **Begin setup** et renseigne :

   | Champ | Valeur |
   |---|---|
   | Project name | `anthony-vivien-site` |
   | Production branch | `main` |
   | Framework preset | `None` |
   | Build command | *(laisser vide)* |
   | Build output directory | `site` |

5. **Save and Deploy**. Une minute plus tard, le site est en ligne sur `https://anthony-vivien-site.pages.dev`.
6. Dans **Settings → Builds → Branch control**, laisse **Preview deployments : All non-production branches**. La branche `ameliore` aura ainsi son propre aperçu : `https://ameliore.anthony-vivien-site.pages.dev`.

À partir de là, chaque modification poussée sur GitHub est mise en ligne automatiquement.

## Étape 3 : construire le site (dans l'autre conversation)

- Lancer `python3 scripts/import_cargo.py` (il faut l'accès à `api.cargo.site` et `freight.cargo.site`).
- Construire la **copie fidèle** sur `main` et la **version améliorée** sur `ameliore`.
- Comparer les deux aperçus `.pages.dev`, puis fusionner la version gardée dans `main`.

## Étape 4 : sortir le domaine de chez Cargo

Pour brancher `anthony-vivien.com` sur Cloudflare Pages, le domaine doit être géré par Cloudflare. Il faut donc pouvoir changer ses **serveurs DNS (nameservers)**.

**4a. Vérifie d'abord dans Cargo** (Settings → Domain) :
- Peut-on modifier les **nameservers** du domaine ?
- Peut-on obtenir un **code de transfert** (auth code / EPP code) et **déverrouiller** le domaine ?
- Note la **date d'expiration** du domaine.

**4b. Choisis le chemin :**

| Cas | Ce qu'on fait |
|---|---|
| **Cargo permet de changer les nameservers** | Ajoute `anthony-vivien.com` dans Cloudflare (*Add a domain*, plan Free), copie les 2 nameservers donnés par Cloudflare dans Cargo, attends que la zone passe **Active**, puis **Transfer Domains** dans Cloudflare avec le code de Cargo. Le domaine finit chez Cloudflare Registrar, à prix coûtant. |
| **Cargo ne permet que le code de transfert** (cas fréquent chez les créateurs de sites) | Transfère le domaine chez **OVH**, où tu as déjà un compte (commande « Transfert de domaine » avec le code de Cargo). Une fois chez OVH, remplace ses serveurs DNS par ceux de Cloudflare. Ensuite, soit tu restes chez OVH (environ 10 à 15 € par an), soit tu le transfères chez Cloudflare au bout de 60 jours. |

Points d'attention :
- Un domaine ne peut pas être transféré s'il a été **enregistré ou transféré il y a moins de 60 jours**, ou si les **coordonnées du titulaire** ont été modifiées il y a moins de 60 jours. Ne modifie donc pas ton nom ou ton email chez Cargo avant le transfert.
- Si **DNSSEC** est activé chez Cargo, désactive-le avant de changer les nameservers.
- Le transfert d'un `.com` inclut en général **un an de renouvellement**. Ce n'est pas de l'argent perdu.
- Un transfert prend en général **3 à 5 jours ouvrés**. Valide l'email de confirmation de l'ancien registrar pour accélérer.
- **Emails** : si tu utilises une adresse `@anthony-vivien.com` (pas seulement Gmail), relève ses enregistrements **MX/TXT** avant de changer les DNS, pour les recréer dans Cloudflare.

## Étape 5 : brancher le domaine sur le site

Une fois la zone `anthony-vivien.com` **Active** dans Cloudflare :

1. **Workers & Pages** → `anthony-vivien-site` → **Custom domains** → **Set up a custom domain**.
2. Ajoute `www.anthony-vivien.com` puis `anthony-vivien.com`. Cloudflare crée lui-même les enregistrements DNS et le certificat HTTPS.
3. Choisis une adresse principale (l'ancien site utilisait `www`) et redirige l'autre vers elle : **Rules → Redirect Rules**, `anthony-vivien.com/*` → `https://www.anthony-vivien.com/${1}` en 301.
4. Teste : `https://www.anthony-vivien.com`, `/tv_page`, `/arcane`, `/about`.

## Étape 6 : résilier Cargo (seulement maintenant)

À faire seulement quand :
- [ ] le nouveau site s'affiche sur `www.anthony-vivien.com` ;
- [ ] le domaine n'apparaît plus chez Cargo (transfert terminé) ;
- [ ] les emails `@anthony-vivien.com` fonctionnent, si tu en utilises.

Alors : Cargo → Account → Billing → annuler l'abonnement.

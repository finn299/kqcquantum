# KQC Quantum Inc. (KQC) · Investor Relations Website

Corporate + investor-relations site for **KQC Quantum Inc.**, the public company whose operating company is Korea Quantum Computing Co., Ltd. (한국퀀텀컴퓨팅㈜), Busan, Republic of Korea,
to be served at **kqcquantum.com**.

## Site mode

`SITE_MODE` at the top of `tools/content.py` selects what gets built:

- `"ir"` (current, per Blueshirt Group, Sep 29 2026): investor relations only. The home page is the Investor
  Relations page (featured announcement, Investor Resources boxes, email alerts, investor contact). Sub-pages:
  `presentations.html`, `filings.html`, `webcasts.html`, `news.html`, `contact.html`, `disclosure.html`.
  No corporate pages, no partner logos, no ticker badge; news items link to the original publication.
  `investors.html` and `press.html` are kept as redirects, and `webcast.html` (singular) forwards to `webcasts.html`
  so the address printed in press releases, `kqcquantum.com/webcast`, always resolves. The build removes the
  full-mode pages from the output.
- `"full"`: the complete corporate + IR build (home with business lines, about, stock, filings, governance, FAQ,
  on-site press articles). Partner logos were removed from the repository on Sep 29; restore them from git
  history (commit 438872e) if that mode is ever used again.

Switch the value and run `python3 tools/build.py`. Static HTML/CSS/JS, no framework, no build dependencies beyond Python 3 for the
page generator. Deploy the repository root to any static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages, S3).

The **Investors** tab (`investors.html`) follows the format requested by The Blueshirt Group (Sep 29, 2026), modeled on
plus.ai/investors: artwork up top → featured announcement with webcast link → Investor Resources (publicly released
assets) → Recent News → email-alert subscription → Investor Contact (`ir@kqcquantum.com`). The featured announcement,
webcast URL and resource list are data in `tools/content.py` (`FEATURED`, `RESOURCES`).

## Status: preview build

The listing vehicle, exchange, ticker and all market data were **not public as of September 29, 2026**.
Every unknown is rendered as a bracketed placeholder, e.g. `[TICKER]`, with a dashed underline, and a
"Preview build" banner is shown on any host that is not listed in `assets/js/config.js` → `productionHosts`.

Press-release pages are summaries drafted from the cited public coverage (each page says so and links the
source). Replace them with official company text before launch. Executive biographies marked "compiled"
were assembled from public profiles and interviews and need company sign-off. See `disclosure.html#sources`.

## Structure

```
index.html            Home: hero, business lines, stats, investment case, milestones, news, leadership, alerts
about.html            Company overview, business areas, values, leadership (#leadership), history (#history), offices
investors.html        Investors tab (Blueshirt format): artwork, featured announcement + webcast, resources, news, alerts, IR contact
faq.html              Investor FAQ and investment case
stock.html            Stock information: quote/chart placeholders, share structure, transfer agent, identifiers
filings.html          Filings & financials: filing table, highlights, documents, financial calendar
governance.html       Board, committee matrix, governance documents, executive officers, auditor
press.html            Press releases & news (filterable)
press/<slug>.html     Individual releases (generated)
contact.html          IR / media contact and form
disclosure.html       Forward-looking statements, no-offer notice, sources, privacy, trademarks
404.html
assets/css/main.css   Design tokens, base, navigation, components, motion
assets/css/pages.css  Page-specific layouts (hero, qubit visual, stock, governance, contact)
assets/js/config.js   Production hosts, form endpoints, draft visibility
assets/js/site.js     Navigation, reveal-on-scroll, counters, spotlight cards, marquee, timeline, press lists, forms
assets/js/field.js    Hero canvas ("quantum field")
assets/js/stock.js    Chart placeholder (no simulated prices)
assets/js/press-data.js  Generated from tools/content.py
assets/fonts/         Self-hosted Geist and Geist Mono (variable)
assets/images/        favicon.svg, kqc-symbol.svg, og-image.png, apple-touch-icon.png
tools/content.py      ALL editable content: company facts, listing placeholders, leadership, timeline, press, FAQ
tools/build.py        Page generator
tools/og-template.html  Source for og-image.png (screenshot at 1200×630)
```

## Editing content

1. Edit `tools/content.py` (press releases, leadership, timeline, listing fields, FAQ, thesis).
2. Run `python3 tools/build.py` from the repo root. It rewrites the HTML pages, `press/`, `assets/js/press-data.js`,
   `sitemap.xml` and `llms.txt`.
3. Commit.

Quick reference:

- **Ticker / exchange / issuer / CUSIP / transfer agent / auditor** → `LISTING` in `tools/content.py`.
- **Featured announcement, webcast link, investor resources** → `FEATURED` and `RESOURCES` in `tools/content.py`.
- **IR alias** → `COMPANY["email_ir"]` (`ir@kqcquantum.com`; the mailbox must exist before launch) and `irEmail` in
  `assets/js/config.js`.
- **New press release** → add a dict to `PRESS` (`type: "release"`), rebuild. Set `type: "draft"` to keep it out of
  public lists (drafts are visible with `?drafts=1` or `showDrafts: true` in `config.js`).
- **Leadership / board** → `LEADERSHIP` and `BOARD_PLACEHOLDERS`. Headshots: drop `assets/images/leadership/<slug>.jpg`
  (square, 400px or larger) and rebuild; until then the card shows the executive's name in Hangul.
- **Partner logos** → full mode only; `assets/images/partners/<slug>.svg|png` per `PARTNERS` entry (files removed Sep 29, see Site mode).
- **Canonical domain** → `COMPANY["site_url"]` (`https://kqcquantum.com`; used for canonical URLs, Open Graph, sitemap)
  and `productionHosts` in `assets/js/config.js` (hides the preview banner). `robots.txt` is generated by the build from `PUBLIC_INDEXING`.
- **Email alerts / contact form** → set `alertsEndpoint` / `contactEndpoint` in `assets/js/config.js` (Formspree,
  Basin, your own API, or the IR vendor's form). Until then forms fall back to a pre-filled `mailto:`.
- **Stock quote / chart** → replace `assets/js/stock.js` with the market-data vendor's widget when trading begins.
- **Logo** → the wordmark is set in Geist as a stand-in; drop the official SVGs into `assets/images/` and swap the
  `SYMBOL` markup / `.brand-word` in `tools/build.py` and the footer if the company prefers the exact wordmark file.

## Design notes

- Palette anchors on KQC's CI: navy `#012169` (Pantone 280C), Tiffany blue `#2AD2C9`, with an electric-blue ramp
  (`#3b74ff` → `#99b8ff`) on a near-black navy ground. Orange `#EA733D` is reserved for placeholder/pending markers.
- Type: Geist (display and text), Geist Mono (labels, data). Buttons are flat: white primary, hairline secondary.
- Motion: staggered hero entrance, canvas particle field with neighbour links, 3D orbital "qubit", marquee tape,
  scroll reveals, count-up stats, cursor spotlight on cards, timeline rail fill. Everything respects
  `prefers-reduced-motion`; the canvas pauses off-screen and when the tab is hidden.
- Accessibility: skip link, keyboard-operable dropdowns and mobile menu, focus rings, semantic landmarks, `aria`
  labels on decorative canvases, print styles for press releases.

## Local preview

```bash
python3 tools/build.py               # regenerate the pages
python3 -m http.server 8123          # static, http://localhost:8123
node server.js                       # with the password gate, http://localhost:10000
```

## Hosting on Render (two services, same repository)

- **kqc-quantum-preview** (web service, free): the password-protected review copy. `server.js` is a zero-dependency
  Node server that fronts the repository root with a single shared password (no username), clean URLs, noindex
  headers and a robots.txt that disallows crawling. The password is stored as a SHA-256 hash in `server.js`
  (override with the `PREVIEW_PASSWORD` env var; an empty string disables the gate). Deploys from `main` on every push.
- **kqc-quantum-live** (static site, free): the production site, where kqcquantum.com points. Until go-live it
  publishes the `holding/` folder, a self-contained "coming soon" page (noindex), so the custom domain, DNS and TLS
  are set up ahead of time without exposing the site. Custom domains (`kqcquantum.com`, `www` redirecting to the
  apex), the redirect/rewrite rules and the response headers from `render.yaml` are already entered in the dashboard
  (Oct 6, 2026). The DNS records the domain holder needs are listed at the top of `render.yaml`.

`render.yaml` documents both. Both services were created in the Render dashboard.

### Webcast link for press releases

Use `https://www.kqcquantum.com/webcast` (or without `www`). It resolves to the Webcasts page in every environment:
Render rewrites `/webcast` to `webcasts.html`, the preview server and any other static host serve the generated
`webcast.html`, which forwards to `webcasts.html`. When the webcast host sends the registration link, put it in
`RESOURCE_PAGES["webcasts"]` (and `FEATURED["webcast_url"]`) in `tools/content.py` and rebuild; after the event,
replace it with the replay link. The printed address never changes.

### Go-live checklist

1. `tools/content.py`: set `PUBLIC_INDEXING = True` (removes the noindex tag from every page and lets robots.txt
   allow crawling). Fill in the listing fields and the featured announcement.
2. `assets/js/config.js`: `productionHosts` already lists kqcquantum.com, so the preview banner disappears on the
   live domain by itself; set `hidePreviewBanner: true` if the site should also look final on the onrender.com address.
3. Rebuild, commit, push.
4. Render dashboard, static site `kqc-quantum`: Settings > Publish directory, change `holding` to `.` and redeploy
   (or change `staticPublishPath` in `render.yaml` if the site is managed as a Blueprint). Add the redirect and
   rewrite rules from `render.yaml` under Redirects/Rewrites if they are not there yet.
5. The preview web service can then be suspended or deleted.

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static-site generator for the KQC Quantum Inc. corporate and investor-relations site.

    python3 tools/build.py

Reads tools/content.py and writes the HTML pages, press/ articles,
assets/js/press-data.js, sitemap.xml and llms.txt into the repo root.
No third-party dependencies. Python 3.8+.
"""
import os
import re
import sys
import json
import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import content as C  # noqa: E402

CO, L = C.COMPANY, C.LISTING
SITE = CO["site_url"].rstrip("/")

# Site mode. "lean" builds the Blueshirt-scope site (home, about, investors, news, contact, disclosure)
# and links news items to their original publication. "full" builds every page. Set in tools/content.py.
MODE = str(getattr(C, "SITE_MODE", "full")).lower()
LEAN = MODE == "ir"          # investor-relations-only build (see tools/content.py)
INDEXING = bool(getattr(C, "PUBLIC_INDEXING", False))   # False = noindex meta on every page + robots.txt disallow

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def fmt_date(iso, short=False):
    y, m, d = iso.split("-")
    name = MONTHS[int(m) - 1]
    return f"{name[:3] if short else name} {int(d)}, {y}"


def initials(name):
    parts = [p for p in re.sub(r",.*$", "", name).replace(".", " ").split() if p and p[0].isupper()]
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return parts[0][:2].upper() if parts else "KQ"


PH_RE = re.compile(r"\[([A-Z][^\[\]<>]{0,110})\]")


def mark_placeholders(html):
    """Wrap [Bracketed] placeholders in <span class="ph">, text nodes only (never inside
    tags/attributes, <script> or <style>)."""
    span = r'<span class="ph" title="Placeholder: pending company confirmation">[\1]</span>'
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<title\b.*?</title>|<[^>]+>)", html, flags=re.S | re.I)
    out = []
    for part in parts:
        if part.startswith("<"):
            out.append(part)
        else:
            out.append(PH_RE.sub(span, part))
    return "".join(out)


import hashlib


def asset_v(rel):
    """Short content hash for cache-busting query strings on css/js."""
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        return "0"
    return hashlib.sha1(open(path, "rb").read()).hexdigest()[:8]


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("  wrote", rel)


# ---------------------------------------------------------------------------
# Brand + icons
# ---------------------------------------------------------------------------
SYMBOL = (
    '<svg class="brand-mark" viewBox="0 0 100 100" aria-hidden="true" focusable="false">'
    '<g fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round">'
    '<path d="M18 50 L50 18"/><path d="M82 18 L82 50"/><path d="M50 50 L82 82"/><path d="M18 82 L50 82"/></g>'
    '<g fill="currentColor"><circle cx="18" cy="18" r="9.5"/><circle cx="50" cy="18" r="9.5"/><circle cx="82" cy="18" r="9.5"/>'
    '<circle cx="18" cy="50" r="9.5"/><circle cx="50" cy="50" r="9.5"/><circle cx="82" cy="50" r="9.5"/>'
    '<circle cx="18" cy="82" r="9.5"/><circle cx="50" cy="82" r="9.5"/><circle cx="82" cy="82" r="9.5"/></g></svg>'
)

ICONS = {
    "atom": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="1.6" fill="currentColor" stroke="none"/><ellipse cx="12" cy="12" rx="10" ry="4.2"/><ellipse cx="12" cy="12" rx="10" ry="4.2" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4.2" transform="rotate(120 12 12)"/></svg>',
    "shield": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.5 4 5.6v6c0 5 3.4 8.6 8 9.9 4.6-1.3 8-4.9 8-9.9v-6z"/><rect x="9" y="10.5" width="6" height="5" rx="1"/><path d="M10.2 10.5V9a1.8 1.8 0 0 1 3.6 0v1.5"/></svg>',
    "chip": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><path d="M9 2.5v3M12 2.5v3M15 2.5v3M9 18.5v3M12 18.5v3M15 18.5v3M2.5 9h3M2.5 12h3M2.5 15h3M18.5 9h3M18.5 12h3M18.5 15h3"/></svg>',
    "doc": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M7 2.5h7l5 5V20a1.5 1.5 0 0 1-1.5 1.5h-10.5A1.5 1.5 0 0 1 5.5 20V4A1.5 1.5 0 0 1 7 2.5z"/><path d="M14 2.5v5h5M8.5 12h7M8.5 15.5h7M8.5 8.5h3"/></svg>',
    "chart": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 20.5h17"/><path d="M4 15.5l5-5 4 3.5 7-7.5"/><path d="M16 6.5h4v4"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><rect x="3.5" y="5" width="17" height="15.5" rx="2"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/></svg>',
    "pin": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 21.5s-7-6.4-7-11.5a7 7 0 0 1 14 0c0 5.1-7 11.5-7 11.5z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "gavel": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13.5 5.5 18.5 10.5M11 8l5 5M3.5 20.5l8.5-8.5M14 3l7 7-2.5 2.5-7-7z"/></svg>',
    "people": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M15.5 14.5a5 5 0 0 1 6 5"/></svg>',
    "chev": '<svg class="chev" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m2.5 4.5 3.5 3.5 3.5-3.5"/></svg>',
}


def ico(name):
    return ICONS[name]


# ---------------------------------------------------------------------------
# Layout: head, nav, footer
# ---------------------------------------------------------------------------
NAV = [
    ("Company", [
        ("about.html", "About KQC", "Mission, business lines, offices"),
        ("about.html#leadership", "Leadership", "Executive team"),
        ("about.html#history", "History", "Milestones since 2021"),
        ("governance.html", "Corporate Governance", "Board, committees, policies"),
        ("sep", None, None),
        ("https://www.kqchub.com/en/", "kqchub.com ↗", "Corporate website"),
    ]),
    ("Investors", [
        ("investors.html", "Investor Relations", "Overview and investment case"),
        ("stock.html", "Stock Information", "Quote, chart and share data"),
        ("filings.html", "Filings &amp; Financials", "Regulatory filings and reports"),
        ("governance.html", "Governance", "Board and committees"),
        ("faq.html", "Investor FAQ", "Common questions"),
        ("investors.html#alerts", "Email Alerts", "Get investor updates"),
    ]),
    ("News", None),
    ("Contact", None),
]
NAV_HREF = {"News": "press.html", "Contact": "contact.html", "Company": "about.html", "Investors": "investors.html"}
NAV_IR = [
    ("index.html", "Overview", "Investor relations home"),
    ("index.html#featured", "Featured Announcement", "Latest company announcement"),
    ("presentations.html", "Presentations", "Investor presentation"),
    ("filings.html", "Filings", "SEC filings on EDGAR"),
    ("webcasts.html", "Webcasts", "Events, replays and transcripts"),
    ("news.html", "News", "Press releases and coverage"),
    ("index.html#alerts", "Email Alerts", "Investor updates by email"),
]


def nav_html(depth):
    p = depth
    if LEAN:
        return nav_html_ir(depth)
    nav = NAV
    items = []
    for label, sub in nav:
        if sub is None:
            items.append(f'<a class="nav-item" href="{p}{NAV_HREF[label]}">{label}</a>')
            continue
        links = []
        for href, text, hint in sub:
            if href == "sep":
                links.append('<div class="sep"></div>')
                continue
            full = href if href.startswith("http") else p + href
            links.append(f'<a href="{full}">{text}<small>{hint}</small></a>')
        items.append(
            f'<div class="dropdown"><button class="nav-item" type="button">{label}{ico("chev")}</button>'
            f'<div class="dropdown-menu">{"".join(links)}</div></div>'
        )
    mobile_groups = []
    for label, sub in nav:
        if sub is None:
            mobile_groups.append(f'<div class="mobile-group"><span class="tag">{label}</span><a href="{p}{NAV_HREF[label]}">{label}</a></div>')
        else:
            ls = "".join(
                f'<a href="{href if href.startswith("http") else p + href}">{text}</a>'
                for href, text, hint in sub if href != "sep"
            )
            mobile_groups.append(f'<div class="mobile-group"><span class="tag">{label}</span>{ls}</div>')

    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container nav-row">
    <a class="brand" href="{p}index.html" aria-label="KQC Quantum Inc., investor relations home">
      {SYMBOL}<span class="brand-word">KQC</span><span class="brand-sub">Quantum<br>Inc.</span>
    </a>
    <nav class="nav-main" aria-label="Primary">{"".join(items)}</nav>
    <div class="nav-ctas">
      {"" if LEAN else f'<a class="ticker-badge" href="{p}stock.html" title="Stock information"><span class="live-dot"></span>{L["exchange_short"]}: {L["ticker"]}</a>'}
      <a class="btn btn-primary btn-sm" href="{p}contact.html">Contact IR</a>
      <button class="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <nav aria-label="Mobile">
    {"".join(mobile_groups)}
    <div class="mobile-ctas"><a class="btn btn-primary" href="{p}contact.html">Contact IR</a>{"" if LEAN else f'<a class="btn btn-ghost" href="{p}stock.html">{L["exchange_short"]}: {L["ticker"]}</a>'}</div>
  </nav>
</div>"""


def nav_html_ir(depth):
    p = depth
    links = "".join(f'<a href="{p}{href}">{text}<small>{hint}</small></a>' for href, text, hint in NAV_IR)
    mobile = "".join(f'<a href="{p}{href}">{text}</a>' for href, text, hint in NAV_IR)
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="container nav-row nav-row--ir">
    <a class="brand" href="{p}index.html" aria-label="KQC Quantum Inc., investor relations home">
      {SYMBOL}<span class="brand-word">KQC</span><span class="brand-sub">Quantum<br>Inc.</span>
    </a>
    <div class="nav-ctas">
      <div class="dropdown dropdown--right"><button class="nav-item" type="button">Investors{ico("chev")}</button>
        <div class="dropdown-menu">{links}</div></div>
      <a class="btn btn-primary btn-sm" href="{p}contact.html">Contact IR</a>
      <button class="menu-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="mobile-menu"><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-menu" id="mobile-menu" aria-hidden="true">
  <nav aria-label="Mobile">
    <div class="mobile-group"><span class="tag">Investors</span>{mobile}</div>
    <div class="mobile-ctas"><a class="btn btn-primary" href="{p}contact.html">Contact IR</a></div>
  </nav>
</div>"""


def footer_columns(p):
    if LEAN:
        return f"""<div class="footer-col">
        <div class="footer-title">Investors</div>
        <a href="{p}index.html">Overview</a>
        <a href="{p}presentations.html">Presentations</a>
        <a href="{p}filings.html">Filings</a>
        <a href="{p}webcasts.html">Webcasts</a>
        <a href="{p}news.html">News</a>
        <a href="{p}index.html#alerts">Email Alerts</a>
      </div>
      <div class="footer-col">
        <div class="footer-title">Company</div>
        <a href="{p}contact.html">Contact IR</a>
        <a href="{p}disclosure.html">Disclosure</a>
        <a href="https://www.kqchub.com/en/" target="_blank" rel="noopener noreferrer">Corporate website &#8599;</a>
      </div>"""
    return f"""<div class="footer-col">
        <div class="footer-title">Company</div>
        <a href="{p}about.html">About KQC</a>
        <a href="{p}about.html#leadership">Leadership</a>
        <a href="{p}about.html#history">History</a>
        <a href="{p}governance.html">Governance</a>
        <a href="https://www.kqchub.com/en/" target="_blank" rel="noopener noreferrer">kqchub.com &#8599;</a>
      </div>
      <div class="footer-col">
        <div class="footer-title">Investors</div>
        <a href="{p}investors.html">IR Overview</a>
        <a href="{p}stock.html">Stock Information</a>
        <a href="{p}filings.html">Filings &amp; Financials</a>
        <a href="{p}press.html">Press Releases</a>
        <a href="{p}faq.html">Investor FAQ</a>
        <a href="{p}investors.html#alerts">Email Alerts</a>
      </div>
      <div class="footer-col">
        <div class="footer-title">Businesses</div>
        <a href="https://www.kqchub.com/en/quantum-computing" target="_blank" rel="noopener noreferrer">Quantum Computing &#8599;</a>
        <a href="https://www.kqchub.com/en/quantum-security" target="_blank" rel="noopener noreferrer">Quantum Security &#8599;</a>
        <a href="https://www.kqchub.com/en/ai-infrastructure" target="_blank" rel="noopener noreferrer">AI Infrastructure &#8599;</a>
        <a href="https://www.kqchub.com/en/newsroom" target="_blank" rel="noopener noreferrer">Corporate Newsroom &#8599;</a>
      </div>"""


def footer_html(depth):
    p = depth
    return f"""<footer class="site-footer">
  <div class="container">
    <div class="footer-top">
      <div class="footer-brand">
        <a class="brand" href="{p}index.html" aria-label="KQC Quantum Inc. home">{SYMBOL}<span class="brand-word">KQC</span><span class="brand-sub">Quantum<br>Inc.</span></a>
        <p>{CO['legal_name']} {CO['tagline']}</p><p class="muted" style="font-size:.8rem">{CO['structure']}</p>
        {"" if LEAN else f'<p class="mono" style="font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:var(--faint)">{L["exchange_short"]}: {L["ticker"]}<br>{L["status_line"]}</p>'}
      </div>
      {footer_columns(p)}
      <div class="footer-col">
        <div class="footer-title">Contact</div>
        <span class="addr"><strong style="color:var(--ink-soft)">Busan HQ</strong><br>{CO['address_busan']}<br>{CO['phone_busan']}</span>
        <span class="addr"><strong style="color:var(--ink-soft)">Seoul</strong><br>{CO['address_seoul']}<br>{CO['phone_seoul']}</span>
        <a href="mailto:{CO['email_general']}">{CO['email_general']}</a>
      </div>
    </div>
    <p class="footer-disclaimer">This website may contain forward-looking statements within the meaning of applicable securities laws. Such statements involve risks and uncertainties and actual results may differ materially. Nothing on this site constitutes an offer to sell or a solicitation of an offer to buy any securities. Fields shown in [brackets] are placeholders pending company confirmation. See <a href="{p}disclosure.html" style="color:var(--muted);text-decoration:underline">Disclosure</a>.</p>
    <div class="footer-bottom">
      <div>&copy; <span data-current-year>{CO['copyright_year']}</span> {CO['legal_name']} All rights reserved.</div>
      <div class="footer-legal"><a href="{p}disclosure.html#forward-looking">Forward-Looking Statements</a><a href="{p}disclosure.html#privacy">Privacy</a><a href="{p}disclosure.html#no-offer">Disclaimer</a><a href="{p}disclosure.html#sources">Sources</a></div>
    </div>
  </div>
</footer>
<div class="preview-bar" hidden role="note"><span>Preview build &middot; bracketed fields are placeholders pending company confirmation &middot; not an offer of securities</span><button type="button">Dismiss</button></div>"""


def layout(title, description, body, depth="", body_class="", canonical="", extra_head="", scripts=(), og_type="website"):
    p = depth
    canon = f"{SITE}/{canonical}" if canonical else SITE + "/"
    script_tags = "".join(f'<script src="{p}assets/js/{s}?v={asset_v("assets/js/" + s)}"></script>' for s in scripts)
    full = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canon}">
{"" if INDEXING else '<meta name="robots" content="noindex,nofollow">'}
<meta name="theme-color" content="#02040b">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="KQC Quantum Inc.">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/images/og-image.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}/assets/images/og-image.png">
<link rel="icon" type="image/svg+xml" href="{p}assets/images/favicon.svg">
<link rel="apple-touch-icon" href="{p}assets/images/apple-touch-icon.png">
<link rel="preload" href="{p}assets/fonts/geist-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/geist-mono-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/css/main.css?v={asset_v("assets/css/main.css")}">
<link rel="stylesheet" href="{p}assets/css/pages.css?v={asset_v("assets/css/pages.css")}">
{extra_head}
</head>
<body class="{body_class}" data-depth="{p}">
{nav_html(p)}
<main id="main">
{body}
</main>
{footer_html(p)}
<script src="{p}assets/js/config.js?v={asset_v("assets/js/config.js")}"></script>
<script src="{p}assets/js/press-data.js?v={asset_v("assets/js/press-data.js")}"></script>
<script src="{p}assets/js/site.js?v={asset_v("assets/js/site.js")}"></script>
{script_tags}
</body>
</html>
"""
    return mark_placeholders(full)


def page_hero(crumbs, h1, meta_items=(), lede="", buttons=(), depth="", extra=""):
    crumb_html = '<span class="sep">/</span>'.join(
        f'<a href="{depth}{href}">{text}</a>' if href else f"<span>{text}</span>" for text, href in crumbs
    )
    meta = f'<div class="meta">{"".join(f"<span>{m}</span>" for m in meta_items)}</div>' if meta_items else ""
    btns = f'<div class="button-row">{"".join(buttons)}</div>' if buttons else ""
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    return f"""<section class="page-hero bg-grid">
  <div class="orb"></div><div class="orb two"></div>
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb">{crumb_html}</nav>
    <h1 class="fade-up" style="--d:0">{h1}</h1>
    <div class="fade-up" style="--d:1">{meta}{lede_html}{btns}{extra}</div>
  </div>
</section>"""


def btn(href, text, kind="ghost", arrow=False, ext=False):
    a = ""  # arrows retired: buttons stay flat and quiet
    e = ' target="_blank" rel="noopener noreferrer"' if ext else ""
    return f'<a class="btn btn-{kind}" href="{href}"{e}>{text}{a}</a>'


# ---------------------------------------------------------------------------
# Shared fragments
# ---------------------------------------------------------------------------
def press_public():
    return sorted([p for p in C.PRESS if p["type"] != "draft"], key=lambda x: x["date"], reverse=True)


def type_label(t):
    return {"media": "In the News", "draft": "Draft"}.get(t, "Press Release")


def press_href(p, depth=""):
    """Lean mode sends readers to the original publication; full mode to the on-site article page."""
    if LEAN and not p.get("official"):
        return p.get("source_url") or f"{depth}news.html"
    return f"{depth}press/{p['slug']}.html"


def press_attrs(p):
    return ' target="_blank" rel="noopener noreferrer"' if LEAN and p.get("source_url") and not p.get("official") else ""


def press_card(p, depth, latest=False):
    return (
        f'<article class="press-card{" featured" if latest else ""}">'
        + f'<div class="meta-row">{"<span class=badge-latest>Latest</span>" if latest else ""}<span class="date">{fmt_date(p["date"], True)}</span><span class="tag">{type_label(p["type"])}</span></div>'
        + f'<h3><a href="{press_href(p, depth)}"{press_attrs(p)}>{p["headline"]}</a></h3><p>{p["excerpt"]}</p>'
        + f'<div class="foot"><span class="link">{"Open" if LEAN and not p.get("official") else "Read"} <span class="arr">{"↗" if LEAN and not p.get("official") else "→"}</span></span><span class="tag" style="color:var(--faint)">{(p["source_name"] if not p.get("official") else "Company release") if LEAN else p["tags"][0]}</span></div></article>'
    )


def press_row(p, depth):
    tags = "".join(f'<span class="chip">{t}</span>' for t in p["tags"])
    return (
        f'<article class="press-row"><div class="date">{fmt_date(p["date"], True)}<small>{type_label(p["type"])}{"" if p.get("official") else " &middot; " + p["source_name"]}</small></div>'
        f'<div><h3><a href="{press_href(p, depth)}"{press_attrs(p)}>{p["headline"]}</a></h3><p>{p["excerpt"]}</p>{"" if LEAN else f"<div class=tags>{tags}</div>"}</div>'
        f'<span class="go">{"Open ↗" if LEAN and not p.get("official") else "Read →"}</span></article>'
    )


def avatar(m, depth=""):
    """Portrait if assets/images/leadership/<slug>.(jpg|png|webp) exists; otherwise nothing (text-first card)."""
    for ext in ("jpg", "jpeg", "png", "webp"):
        rel = f"assets/images/leadership/{m['slug']}.{ext}"
        if os.path.exists(os.path.join(ROOT, rel)):
            return f'<div class="portrait"><img src="{depth}{rel}" alt="{m["name"]}" loading="lazy"></div>'
    return ""


def leader_card(m, depth="", wide=False):
    bio = "".join(f"<p>{b}</p>" for b in m["bio"])
    return (
        f'<article class="card spot leader" id="{m["slug"]}">'
        f'{avatar(m, depth)}'
        f'<div><div class="role">{m["title"]}</div><h3>{m["name"]}<span class="korean">{m["korean"]}</span></h3></div>'
        f'{bio}<div class="note">{m["note"]}</div></article>'
    )


def image_size(path):
    """(width, height) for a PNG or SVG without third-party libraries; None if unknown."""
    try:
        with open(path, "rb") as f:
            head = f.read(4096)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            import struct
            return struct.unpack(">II", head[16:24])
        if path.lower().endswith(".svg"):
            txt = head.decode("utf-8", "ignore")
            vb = re.search(r'viewBox="\s*[-\d.]+[\s,]+[-\d.]+[\s,]+([\d.]+)[\s,]+([\d.]+)', txt)
            if vb:
                return float(vb.group(1)), float(vb.group(2))
            w = re.search(r'\swidth="([\d.]+)', txt)
            h = re.search(r'\sheight="([\d.]+)', txt)
            if w and h:
                return float(w.group(1)), float(h.group(1))
    except Exception:
        pass
    return None


def logo_tile(pt, depth=""):
    for ext in ("svg", "png", "webp"):
        rel = f"assets/images/partners/{pt['slug']}.{ext}"
        full = os.path.join(ROOT, rel)
        if os.path.exists(full):
            size = image_size(full)
            sq = " sq" if size and size[1] and (size[0] / size[1]) < 1.9 else ""
            return f'<span class="logo-tile has-logo{sq}" title="{pt["name"]}"><img src="{depth}{rel}" alt="{pt["name"]}" loading="lazy"></span>'
    return f'<span class="logo-tile"><span>{pt["name"]}</span></span>'


def logo_wall(depth=""):
    half = (len(C.PARTNERS) + 1) // 2
    rows = [C.PARTNERS[:half], C.PARTNERS[half:]]
    out = []
    for i, row in enumerate(rows):
        tiles = "".join(logo_tile(pt, depth) for pt in row)
        out.append(f'<div class="logos{" reverse" if i else ""}" aria-label="Partner logos"><div class="tape-track logo-track" data-speed="{34 if i == 0 else 27}">{tiles}</div></div>')
    return "".join(out)


def alerts_block(depth="", heading="Investor email alerts.", copy="Press releases, filings and event notices. No marketing, unsubscribe any time.", eyebrow="Email alerts"):
    return f"""<section class="cta-band bg-grid" id="alerts">
  <div class="glow"></div>
  <div class="container reveal">
    <p class="eyebrow center">{eyebrow}</p>
    <h2>{heading}</h2>
    <p class="sub">{copy}</p>
    <form class="alert-form" id="alerts-form" method="post" action="#" novalidate>
      <label class="visually-hidden" for="alert-email" style="position:absolute;left:-9999px">Email address</label>
      <input class="input" id="alert-email" type="email" name="email" placeholder="you@institution.com" required>
      <button class="btn btn-primary" type="submit">Subscribe</button>
    </form>
    <p class="form-ok notice" hidden style="margin-top:1rem">Thank you. Your request has been sent to investor relations.</p>
  </div>
</section>"""


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------
def page_home():
    d = ""
    latest = press_public()[0]
    pillars = [
        ("01", "Quantum Computing", "atom",
         "Access to IBM quantum systems as a hub of the IBM Quantum Network since 2022, industry algorithm R&amp;D, education and consulting, and Qubiteer, which turns a plain-language problem description into a quantum optimization run.",
         ["IBM Quantum hub", "Qubiteer", "Busan Metro scheduling", "Drug discovery"], "https://www.kqchub.com/en/quantum-computing"),
        ("02", "Quantum Security", "shield",
         "PQC-native hardware built with Crypto4A: the QxHSM&trade; hardware security module, the compact KQC QuHSM&trade; and QuKey Bio biometric authentication. Proofs of concept completed with IBK Industrial Bank and LS ITC.",
         ["QxHSM™", "QuHSM™", "QuKey Bio", "ML-DSA / ML-KEM"], "https://www.kqchub.com/en/quantum-security"),
        ("03", "AI Infrastructure", "chip",
         "KQC GPUaaS: an NVIDIA H200 SXM5 GPU farm co-located at Digital Edge SEL2, delivering dedicated bare-metal performance for LLM and multimodal workloads on pay-as-you-go terms.",
         ["NVIDIA H200 SXM5", "141 GB HBM3e", "GPUaaS", "NVIDIA AI Enterprise"], "https://www.kqchub.com/en/ai-infrastructure"),
    ]
    pillar_html = "".join(
        f'<article class="card spot pillar"><div class="num">{n}</div><span class="n">Business line</span><h3>{t}</h3><p>{txt}</p>'
        f'<div class="chips">{"".join(f"<span class=chip>{c}</span>" for c in chips)}</div>'
        f'<div class="foot"><span class="muted">Learn more on kqchub.com</span><a class="link link-ext" href="{url}" target="_blank" rel="noopener noreferrer">Open</a></div></article>'
        for n, t, icon, txt, chips, url in pillars
    )
    stats = [
        ("2021", "", "Incorporated in Seoul; headquartered in Busan since 2022", True),
        ("27", "", f"Employees ({CO['employees_asof']}), including 9 Ph.D. researchers", False),
        ("25", "+", "Partner organizations across industry, government and academia", False),
        ("2022", "", "Hub of the IBM Quantum Network and IBM Quantum Innovation Center", True),
        ("1", "st", "ISO/IEC 27001 certification in Korea's quantum computing industry (2026)", False),
        ("3", "", "Business lines: quantum computing, quantum security, AI infrastructure", False),
    ]
    stats_html = "".join(
        f'<div class="stat"><div class="stat-n">{"" if plain else "<span data-count=" + chr(34) + v + chr(34) + (" data-suffix=" + chr(34) + s + chr(34) if s else "") + ">"}{v}{s}{"" if plain else "</span>"}</div><div class="stat-l">{l}</div></div>'
        for v, s, l, plain in stats
    )
    thesis_html = "".join(
        f'<div class="thesis-item"><span class="n">{t["n"]}</span><div><h3>{t["title"]}</h3><p>{t["text"]}</p></div><span class="arr" aria-hidden="true">\u2192</span></div>' for t in C.THESIS
    )
    ms = [
        ("2021", "Dec 28", "Incorporated", "Korea Quantum Computing Co., Ltd. is founded by Jay J. H. Kweon and John J. Y. Kim."),
        ("2022", "Apr 7", "IBM Quantum Network hub", "Access agreement signed; the KQC Quantum Computational Center opens in Busan in July."),
        ("2024", "Jan 29", "IBM System Two roadmap", "Plans announced with IBM for an IBM Quantum System Two in Busan and watsonx for KQC clients."),
        ("2025", "Jul 1", "H200 GPU farm live", "KQC GPUaaS launches on NVIDIA H200; Crypto4A PQC partnership follows on Jul 23."),
        ("2025", "Dec 9", "PQC proven in banking", "IBK Industrial Bank completes an end-to-end post-quantum proof of concept on QxHSM™."),
        ("2026", "Mar 12", "ISO/IEC 27001", "First information-security certification in Korea's quantum computing industry."),
        ("2026", "Jun 30", "Qubiteer launched", "Natural-language quantum-AI optimization platform released for industry."),
        ("2026", "[Q4]", "[Public listing]", "[Listing on [Exchange] under the symbol [TICKER], placeholder pending the transaction.]"),
    ]
    ms_html = "".join(f'<article class="ms"><div class="yr">{y}</div><div class="d">{dt}</div><h3>{t}</h3><p>{x}</p></article>' for y, dt, t, x in ms)
    latest3 = press_public()[:3]
    press_html = "".join(press_card(p, d, i == 0) for i, p in enumerate(latest3))
    leaders = [m for m in C.LEADERSHIP if m["slug"] in ("jay-kweon", "john-kim", "stephen-oh")]
    leaders_html = "".join(
        f'<a class="card spot leader" href="about.html#{m["slug"]}">{avatar(m)}'
        f'<div><div class="role">{m["title"]}</div><h3>{m["name"]}<span class="korean">{m["korean"]}</span></h3></div><p>{m["bio"][0][:190].rsplit(" ", 1)[0]}&hellip;</p>'
        f'<span class="link">Profile <span class="arr">→</span></span></a>' for m in leaders
    )
    partners_html = logo_wall(d)
    tape_html = "" if LEAN else f"""<section class="tape" aria-label="Company highlights">
  <div class="tape-track">
    <span class="tape-item hot">{L['exchange_short']}: {L['ticker']} &middot; {L['status_line']}</span>
    <span class="tape-item">Hub of the IBM Quantum Network since 2022</span>
    <span class="tape-item bright">ISO/IEC 27001 certified</span>
    <span class="tape-item">NVIDIA H200 SXM5 GPU farm live</span>
    <span class="tape-item">PQC proofs of concept: IBK &middot; LS ITC</span>
    <span class="tape-item bright">Qubiteer quantum-AI platform launched</span>
    <span class="tape-item">27 employees &middot; 9 Ph.D.s</span>
    <span class="tape-item">Founded Dec 28, 2021 &middot; Busan &middot; Seoul</span>
  </div>
</section>
"""
    middle_html = "" if LEAN else f"""<section class="section" id="investors">
  <div class="container ir-split">
    <div>
      <div class="section-head reveal">
        <p class="eyebrow">For investors</p>
        <h2>Why KQC.</h2>
        <p class="sub">A commercial quantum operator with revenue-generating security and AI infrastructure businesses, entering the public markets. Details of the listing will be published here as they become available.</p>
      </div>
      <div class="thesis-list reveal" data-stagger>{thesis_html}</div>
      <div class="button-row reveal">{btn("investors.html", "Investor Relations", "primary", arrow=True)}{btn("filings.html", "Filings &amp; Financials")}{btn("governance.html", "Governance")}</div>
    </div>
    <aside class="card spot stock-mini reveal" aria-label="Stock snapshot">
      <p class="eyebrow">Stock snapshot</p>
      <div class="sym">{L['ticker']}<span class="exch">{L['exchange']}</span></div>
      <div class="price">N/A<small>Quote data not yet available</small></div>
      <div class="spark" data-label="Chart activates at listing"><div class="beam"></div></div>
      <div class="kv">
        <div>Issuer<b>{L['issuer']}</b></div>
        <div>Incorporation<b>{L['incorporation']}</b></div>
        <div>Headquarters<b>Busan, Korea</b></div>
        <div>Fiscal year end<b>{L['fiscal_year_end']}</b></div>
      </div>
      <div class="button-row" style="margin-top:1.4rem">{btn("stock.html", "Stock information", "ghost", arrow=True)}</div>
    </aside>
  </div>
</section>

<section class="stats-band">
  <div class="container stats" data-stagger>{stats_html}</div>
</section>

<section class="section section-tight milestones">
  <div class="container">
    <div class="row between reveal" style="align-items:flex-end">
      <div class="section-head" style="margin-bottom:0">
        <p class="eyebrow">Milestones</p>
        <h2>Company milestones.</h2>
      </div>
      <a class="link" href="about.html#history">Full history <span class="arr">→</span></a>
    </div>
    <div class="track-wrap reveal"><div class="track">{ms_html}</div></div>
    <p class="hint">Scroll horizontally &rarr;</p>
  </div>
</section>

"""
    leaders_section = "" if LEAN else f"""<section class="section section-tight">
  <div class="container">
    <div class="section-head reveal">
      <p class="eyebrow">Leadership</p>
      <h2>Executive team.</h2>
    </div>
    <div class="leader-strip" data-stagger>{leaders_html}</div>
    <div class="button-row reveal">{btn("about.html#leadership", "Full leadership team", "ghost", arrow=True)}{btn("governance.html", "Board &amp; governance")}</div>
  </div>
</section>

"""

    body = f"""<section class="hero" aria-labelledby="hero-title">
  <canvas id="qfield" class="hero-field" aria-hidden="true"></canvas>
  <div class="container hero-inner">
    <div class="hero-copy">
      <p class="eyebrow hero-eyebrow fade-up" style="--d:0"><span class="live-dot"></span>{CO['legal_name']} &nbsp;&middot;&nbsp; Busan &middot; Seoul</p>
      <h1 id="hero-title" class="fade-up" style="--d:1">The quantum <span class="shimmer">infrastructure</span> company.</h1>
      <p class="lede fade-up" style="--d:2">KQC builds and runs the infrastructure companies need to use quantum computing today: IBM-powered quantum access and algorithms, post-quantum security hardware, and an NVIDIA H200 AI cloud. Headquartered in Busan, Republic of Korea.</p>
      <div class="hero-actions fade-up" style="--d:3">
        {btn("investors.html", "Investor Relations", "primary", arrow=True)}
        {btn("about.html", "About KQC") if LEAN else btn("stock.html", "Stock Information")}
        {btn("press.html", "News" if LEAN else "Press Releases")}
      </div>
      <a class="news-line fade-up" style="--d:4" href="{press_href(latest)}"{press_attrs(latest)}><span class="tag"><span class="live-dot"></span>Latest</span><span class="date">{fmt_date(latest['date'], True)}</span><span class="t">{latest['headline']}</span><span class="go">→</span></a>
    </div>
    <div class="hero-visual fade-up" style="--d:2" aria-hidden="true">
      <div class="qubit" data-parallax>
        <div class="q-halo"></div>
        <div class="q-orbit"></div>
        <div class="q-ring q-ring-1"><i></i></div>
        <div class="q-ring q-ring-2"><i></i></div>
        <div class="q-ring q-ring-3"><i></i></div>
        <div class="q-core"></div>
      </div>
    </div>
  </div>
  <div class="hero-scroll">Scroll</div>
</section>

{tape_html}
<section class="section" id="business">
  <div class="container">
    <div class="section-head reveal">
      <p class="eyebrow">What we build</p>
      <h2>Three business lines.</h2>
      <p class="sub">KQC turns new technology into services companies can buy today: quantum access and algorithms, post-quantum security hardware, and high-performance AI infrastructure, run from Busan for customers across Korea and Asia.</p>
    </div>
    <div class="pillars" data-stagger>{pillar_html}</div>
  </div>
</section>

<section class="section section-tight logo-section">
  <div class="container">
    <div class="section-head reveal">
      <p class="eyebrow">Ecosystem</p>
      <h2>Partners and customers.</h2>
      <p class="sub">Enterprises, research institutes and universities KQC works with across quantum computing, quantum security and AI infrastructure.</p>
    </div>
  </div>
  <div class="reveal">{partners_html}</div>
</section>

{middle_html}<section class="section" id="news">
  <div class="container">
    <div class="row between reveal" style="align-items:flex-end;margin-bottom:2rem">
      <div class="section-head" style="margin-bottom:0">
        <p class="eyebrow">Newsroom</p>
        <h2>Latest from KQC.</h2>
      </div>
      <a class="link" href="press.html">{"All news" if LEAN else "All press releases"} <span class="arr">→</span></a>
    </div>
    <div class="press-grid" id="press-preview" data-limit="3" data-stagger>{press_html}</div>
  </div>
</section>

{leaders_section}{alerts_block()}
"""
    return layout(
        "KQC Quantum Inc. | Investor Relations" if LEAN else f"KQC Quantum Inc. | Investor Relations | {L['exchange_short']}: {L['ticker']}",
        "Investor relations for KQC Quantum Inc. (KQC): quantum computing, post-quantum security and AI infrastructure from Busan, Korea." + ("" if LEAN else " Press releases, stock information, filings, leadership and governance."),
        body, depth=d, body_class="home", canonical="", scripts=("field.js",),
    )


def page_about():
    d = ""
    values = [
        ("01", "Innovation", "We drive technological innovation that reshapes industry paradigms by commercializing quantum computing, post-quantum cryptography and AI infrastructure."),
        ("02", "Trust", "We protect mission-critical digital assets with proven, enterprise-class security built on hardware security modules and post-quantum cryptography."),
        ("03", "Connectivity", "We connect the global technology ecosystem through quantum-network-based joint research and industrial partnerships, delivering proven use cases across industries."),
    ]
    values_html = "".join(f'<div><div class="n">{n}</div><h3>{t}</h3><p>{x}</p></div>' for n, t, x in values)
    biz = [
        ("Quantum Computing", "atom", ["Quantum computing access (IBM Quantum Network hub)", "Industry algorithm R&amp;D and joint research", "Quantum education and consulting", "KQC Qubiteer quantum-AI optimization platform", "KQC Quantum Computational Center, Busan"]),
        ("Quantum Security", "shield", ["Crypto4A QxHSM&trade; post-quantum HSM", "KQC QuHSM&trade; compact IoT HSM", "KQC QuKey Bio biometric FIDO2 + PQC key", "PQC migration proofs of concept (IBK, LS ITC)", "KpqC and NIST algorithm support"]),
        ("AI Infrastructure", "chip", ["KQC GPUaaS on NVIDIA H200 SXM5", "Bare-metal performance, InfiniBand fabric", "Co-located at Digital Edge SEL2", "Partners: ITCEN Group, Quantum AI", "Roadmap: hybrid quantum-classical cloud"]),
    ]
    biz_html = "".join(
        f'<article class="card spot pillar" style="min-height:0"><div class="num">{"0" + str(k + 1)}</div><h3>{t}</h3><ul>{"".join(f"<li>{x}</li>" for x in items)}</ul></article>'
        for k, (t, i, items) in enumerate(biz)
    )
    leaders_html = "".join(leader_card(m) for m in C.LEADERSHIP)
    tl = []
    for yr in C.TIMELINE:
        items = "".join(
            f'<div class="tl-item"><div class="tl-date">{it["date"]}</div><div><div class="tl-title">{it["title"]}</div>{("<div class=tl-text>" + it["text"] + "</div>") if it["text"] else ""}</div></div>'
            for it in yr["items"]
        )
        tl.append(f'<div class="tl-year"><div class="yr">{yr["year"]}</div>{items}</div>')
    tl_html = "".join(tl)

    body = page_hero(
        [("Home", "index.html"), ("About KQC", None)],
        "About KQC Quantum Inc.",
        [CO["legal_name"], CO["opco_name"], "Operating since " + CO["founded"], "Busan &middot; Seoul"],
        "KQC commercializes quantum computing, quantum security and AI infrastructure for industry. Working with proven technology and global partners, the company is building a trusted and resilient quantum and AI ecosystem in Korea.",
        [btn("#leadership", "Leadership"), btn("#history", "History"), btn("governance.html", "Governance"), btn("https://www.kqchub.com/en/", "Corporate site ↗", ext=True)],
    ) + f"""
<section class="section">
  <div class="container">
    <div class="grid grid-2" style="gap:2rem;align-items:start">
      <div class="reveal">
        <p class="eyebrow">Company overview</p>
        <h2>Founded in Seoul, headquartered in Busan.</h2>
        <p>{CO["structure"]}</p>
        <p>Korea Quantum Computing Co., Ltd. was incorporated on December 28, 2021 and joined the IBM Quantum Network as a hub in April 2022, opening Korea's first commercialized quantum computing R&amp;D center at Dongseo University's Centum campus in Busan that July. The company moved its headquarters from Seoul to Busan in late 2022 and operates a second office in Gangnam, Seoul.</p>
        <p>Since then KQC has layered two further businesses onto its quantum foundation: a post-quantum security hardware line developed with Canada's Crypto4A, and an NVIDIA H200 AI GPU cloud launched in July 2025. All three lines are covered by the company's ISO/IEC 27001 certification, the first in Korea's quantum computing industry.</p>
        <p>Its customers and research partners span finance, manufacturing, life sciences, telecommunications, universities and the public sector.</p>
      </div>
      <dl class="dl reveal">
        <div><dt>Public company</dt><dd>{CO['legal_name']}</dd></div>
        <div><dt>Operating company</dt><dd>{CO['opco_name']}<br><span class="muted" style="font-weight:400">{CO['korean_name']}</span></dd></div>
        <div><dt>Operating company founded</dt><dd>{CO["founded"]}</dd></div>
        <div><dt>Chief Executive Officer</dt><dd>John J. Y. Kim, Ph.D.</dd></div>
        <div><dt>Chairman</dt><dd>Jay J. H. Kweon</dd></div>
        <div><dt>Employees</dt><dd>{CO['employees']} ({CO['employees_asof']}), incl. {CO['phds']} Ph.D.s</dd></div>
        <div><dt>Headquarters</dt><dd>Busan, Republic of Korea</dd></div>
        <div><dt>Certifications</dt><dd>ISO/IEC 27001 (2026) &middot; Venture company (2024)</dd></div>
        <div><dt>Listing</dt><dd>{L['exchange_short']}: {L['ticker']} &middot; {L['status_line']}</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="section section-tight" id="business">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Business areas</p><h2>What KQC sells.</h2></div>
    <div class="biz" data-stagger>{biz_html}</div>
  </div>
</section>

<section class="section section-tight" id="values">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Core values</p><h2>Quantum-driven. Future-oriented. Securely connected.</h2></div>
    <div class="cells values reveal" data-stagger>{values_html}</div>
  </div>
</section>

<section class="section" id="leadership">
  <div class="container">
    <div class="section-head reveal">
      <p class="eyebrow">Leadership</p>
      <h2>Executive team.</h2>
      <p class="sub">Titles as published by the company. Biographies marked as compiled were assembled from public sources and should be confirmed before launch; placeholders await company input. Board composition is on the <a class="link" href="governance.html">governance page</a>.</p>
    </div>
    <div class="leaders" data-stagger>{leaders_html}</div>
  </div>
</section>

<section class="section" id="history">
  <div class="container">
    <div class="section-head reveal">
      <p class="eyebrow">History</p>
      <h2>Milestones.</h2>
      <p class="sub">Company history as published on kqchub.com, with 2026 items from the corporate newsroom and the January 2024 IBM announcement.</p>
    </div>
    <div class="timeline reveal"><div class="rail"></div>{tl_html}</div>
  </div>
</section>

<section class="section section-tight" id="offices">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Locations</p><h2>Offices.</h2></div>
    <div class="offices" data-stagger>
      <article class="card spot office"><div class="k">Headquarters</div><h3>Busan</h3><p>{CO['address_busan_l1']}<br>{CO['address_busan_l2']}</p><p class="mono tel">T {CO['phone_busan']} &nbsp;&middot;&nbsp; F {CO['fax_busan']}</p></article>
      <article class="card spot office"><div class="k">Office</div><h3>Seoul</h3><p>{CO['address_seoul_l1']}<br>{CO['address_seoul_l2']}</p><p class="mono tel">T {CO['phone_seoul']} &nbsp;&middot;&nbsp; F {CO['fax_seoul']}</p></article>
    </div>
  </div>
</section>
"""
    return layout("About KQC | KQC Quantum Inc. Investor Relations",
                  "Company overview, business lines, leadership team, history and offices of KQC Quantum Inc. (KQC) and its operating company Korea Quantum Computing Co., Ltd., Busan, Republic of Korea.",
                  body, canonical="about.html", body_class="about")


def resource_boxes(depth=""):
    """IR mode: the four Investor Resources boxes (Presentations, Filings, Webcasts, News)."""
    out = []
    for r in C.RESOURCE_PAGES:
        if r["items"] is None:
            n = len(press_public()); status = f"{n} item{'s' if n != 1 else ''}"; pend = False
        elif r["slug"] == "filings":
            n = len([f for f in C.FILINGS if f["href"]]); pend = n == 0
            status = f"{n} filing{'s' if n != 1 else ''} on EDGAR" if n else "Coming soon"
        else:
            live = [i for i in r["items"] if i["status"] == "live"]
            pend = not live
            status = f"{len(live)} available" if live else "Coming soon"
        out.append(
            f'<a class="card spot doc-card res-box" href="{depth}{r["slug"]}.html">'
            f'<span class="res-num">{str(len(out) + 1).zfill(2)}</span><h3>{r["title"]}</h3><p>{r["blurb"]}</p>'
            f'<div class="foot"><span{" class=pend" if pend else ""}>{status}</span><span>Open \u2192</span></div></a>'
        )
    return "".join(out)


def page_investors():
    d = ""
    F = C.FEATURED
    latest3 = press_public()[:3]
    news_html = "".join(press_card(p, d, i == 0) for i, p in enumerate(latest3))
    webcast = (f'<a class="btn btn-primary btn-lg" href="{F["webcast_url"]}" target="_blank" rel="noopener noreferrer">Watch Webcast <span class="arr">\u2192</span></a>'
               if F["webcast_url"] else '<a class="btn btn-primary btn-lg" href="webcasts.html" title="The webcast link will be posted here">Webcast: Coming soon <span class="arr">\u2192</span></a>')
    if F.get("transcript"):
        webcast += f'<a class="btn btn-ghost btn-lg" href="{F["transcript"]}" target="_blank" rel="noopener">Webcast transcript (PDF)</a>'
    if F.get("presentation"):
        webcast += f'<a class="btn btn-ghost btn-lg" href="{F["presentation"]}" target="_blank" rel="noopener">Investor presentation (PDF)</a>'
    rel_item = next((x for x in C.PRESS if x["slug"] == F.get("release_slug")), None)
    release_btn = (f'<a class="btn btn-ghost btn-lg" href="press/{F["release_slug"]}.html">Read the press release</a>'
                   if rel_item and (not LEAN or rel_item.get("official")) else "")
    if F.get("release_external"):
        release_btn += f'<a class="btn btn-ghost btn-lg" href="{F["release_external"]}" target="_blank" rel="noopener noreferrer">On Business Wire ↗</a>'
    res_rows = []
    for r in C.RESOURCES:
        pending = r["status"] != "live"
        href = r["href"] or "#alerts"
        ext = href.startswith("http") or href.endswith(".pdf")
        res_rows.append(
            f'<a class="res-row{" pending" if pending else ""}" href="{href}"{" target=_blank rel=noopener" if ext else ""}>'
            f'<span class="res-ico">{str(len(res_rows) + 1).zfill(2)}</span>'
            f'<span class="res-main"><span class="res-title">{r["title"]}</span><span class="res-kind">{r["kind"]}</span></span>'
            f'<span class="res-st">{"[Pending]" if pending else "View"} <span class="arr">\u2192</span></span></a>'
        )
    resources_html = "".join(res_rows)
    more = [
        ("stock.html", "Stock Information", "Quote, chart and share data once trading begins", "chart"),
        ("filings.html", "Filings &amp; Financials", "Regulatory filings, reports and the financial calendar", "doc"),
        ("governance.html", "Corporate Governance", "Board, committees and policies", "people"),
        ("faq.html", "Investor FAQ", "Common questions about KQC and the listing", "calendar"),
    ]
    more_html = "".join(
        f'<a class="card spot doc-card" href="{h}"><h3>{t}</h3><p>{x}</p><div class="foot"><span>Open</span><span>\u2192</span></div></a>' for h, t, x, i in more
    )
    safe_harbor = """<section class="section section-tight legal" id="safe-harbor">
  <div class="container-narrow reveal">
    <p class="eyebrow">Safe harbor</p>
    <p>This page contains statements that may constitute forward-looking statements within the meaning of applicable securities laws, including statements regarding a potential business combination or listing, its terms and timing, product roadmap, partnerships and market opportunity. Such statements involve risks and uncertainties, and actual results may differ materially. Nothing on this page is an offer to sell or a solicitation of an offer to buy any securities. See the full <a class="link" href="disclosure.html#forward-looking">forward-looking statement policy</a>.</p>
  </div>
</section>"""
    if LEAN:
        resources_section = f"""<section class="section section-tight" id="resources">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Resources</p><h2>Investor Resources.</h2>
      <p class="sub">Presentations, filings, webcasts and news. Each section opens on its own page and is updated as materials are published.</p></div>
    <div class="doc-grid res-grid reveal" data-stagger>{resource_boxes()}</div>
  </div>
</section>"""
        news_section_open, news_section_close = "<!--", "-->"
        contact_side = f"""<article class="card spot card-pad-lg">
        <p class="eyebrow">Media</p>
        <h2 style="font-size:clamp(1.6rem,2.6vw,2.2rem)">Press inquiries.</h2>
        <p>Interview requests and press materials: <a class="link" href="mailto:{CO['email_press']}">{CO['email_press']}</a>.</p>
        <p class="mono" style="font-size:.9rem;color:var(--muted)">{CO['opco_name']}<br>{CO['address_seoul']}<br>T {CO['phone_seoul']}</p>
        <div class="button-row">{btn("news.html", "News", "ghost", arrow=True)}{btn("https://www.kqchub.com/en/newsroom", "Corporate newsroom ↗", ext=True)}</div>
      </article>"""
        more_section = safe_harbor
    else:
        resources_section = f"""<section class="section section-tight" id="resources">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Investor resources</p><h2>Presentations, filings and webcasts.</h2>
      <p class="sub">Presentations, releases, filings and webcasts are linked here as they are published.</p></div>
    <div class="res-list reveal" data-stagger>{resources_html}</div>
  </div>
</section>"""
        news_section_open, news_section_close = "", ""
        contact_side = f"""<div class="grid" style="gap:1rem">
        <article class="card spot"><p class="eyebrow">Listing at a glance</p>
          <dl class="dl" style="border:0;background:transparent"><div style="box-shadow:none;padding:.4rem 0;background:transparent"><dt>Ticker</dt><dd>{L['ticker']}</dd></div><div style="box-shadow:none;padding:.4rem 0;background:transparent"><dt>Exchange</dt><dd>{L['exchange']}</dd></div><div style="box-shadow:none;padding:.4rem 0;background:transparent"><dt>Listed issuer</dt><dd>{L['issuer']}</dd></div><div style="box-shadow:none;padding:.4rem 0;background:transparent"><dt>Fiscal year end</dt><dd>{L['fiscal_year_end']}</dd></div></dl></article>
        <article class="card spot"><p class="eyebrow">Media</p><p class="muted" style="margin:0">Press inquiries: <a class="link" href="mailto:{CO['email_press']}">{CO['email_press']}</a> &middot; <a class="link" href="press.html">Newsroom</a></p></article>
      </div>"""
        more_section = f"""<section class="section section-tight" id="more">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">More for investors</p><h2>More investor information.</h2></div>
    <div class="doc-grid" data-stagger>{more_html}</div>
  </div>
</section>

""" + safe_harbor

    body = f"""<section class="hero hero--ir" aria-labelledby="ir-title">
  <canvas id="qfield" class="hero-field" aria-hidden="true"></canvas>
  <div class="container hero-inner">
    <div class="hero-copy">
      {"" if LEAN else '<nav class="breadcrumb fade-up" style="--d:0" aria-label="Breadcrumb"><a href="index.html">Home</a><span class="sep">/</span><span>Investors</span></nav>'}
      <p class="eyebrow hero-eyebrow fade-up" style="--d:0"><span class="live-dot"></span>{CO['legal_name']} &nbsp;&middot;&nbsp; {"Investor Relations" if LEAN else f"{L['exchange_short']}: {L['ticker']}"}</p>
      <h1 id="ir-title" class="fade-up" style="--d:1">KQC Investor <span class="shimmer">Relations</span></h1>
      <p class="lede fade-up" style="--d:2">KQC Quantum Inc. builds the quantum, post-quantum security and AI infrastructure that industry runs on today. Announcements, resources, news and contacts for investors live on this page.</p>
      <div class="hero-actions fade-up" style="--d:3">
        {btn("#featured", "Featured announcement", "primary", arrow=True)}
        {btn("#resources", "Investor resources") if LEAN else btn("#alerts", "Subscribe to alerts")}
        {btn("#alerts", "Subscribe to alerts") if LEAN else btn("#contact", "Investor contact")}
      </div>
    </div>
    <div class="hero-visual fade-up" style="--d:2" aria-hidden="true">
      <div class="qubit" data-parallax>
        <div class="q-halo"></div>
        <div class="q-orbit"></div>
        <div class="q-ring q-ring-1"><i></i></div>
        <div class="q-ring q-ring-2"><i></i></div>
        <div class="q-ring q-ring-3"><i></i></div>
        <div class="q-core"></div>
      </div>
    </div>
  </div>
</section>

<section class="section section-tight" id="featured">
  <div class="container">
    <article class="card spot featured-card reveal">
      <div class="featured-main">
        <p class="eyebrow">{F['label']}</p>
        <h2>{F['headline']}</h2>
        <div class="featured-date mono">{F['date']}</div>
        <p class="featured-body">{F['body']}</p>
        <div class="button-row">{webcast}{release_btn}</div>
        <p class="notice" style="margin-top:1rem">{"" if F["webcast_url"] else "The webcast link will be posted here when the event is scheduled."}</p>
      </div>
      <div class="featured-side" aria-hidden="true">
        <div class="featured-art">{SYMBOL}{"" if LEAN else f'<span class="mono">{L["exchange_short"]}: {L["ticker"]}</span>'}</div>
      </div>
    </article>
  </div>
</section>

{resources_section}

{news_section_open}<section class="section section-tight" id="news">
  <div class="container">
    <div class="row between reveal" style="align-items:flex-end;margin-bottom:1.6rem">
      <div class="section-head" style="margin-bottom:0"><p class="eyebrow">Recent news</p><h2>Latest from KQC.</h2></div>
      <a class="link" href="press.html">View all news <span class="arr">\u2192</span></a>
    </div>
    <div class="press-grid" id="press-preview" data-limit="3" data-stagger>{news_html}</div>
  </div>
</section>{news_section_close}

{alerts_block(heading="Subscribe to investor alerts.", copy="Get the latest KQC investor updates delivered to your inbox: press releases, filings and event notices.", eyebrow="Subscribe")}

<section class="section section-tight" id="contact">
  <div class="container">
    <div class="grid grid-2 contact-pair" style="gap:1.5rem;align-items:stretch" data-stagger>
      <article class="card spot card-pad-lg">
        <p class="eyebrow">Investor contact</p>
        <h2 style="font-size:clamp(1.6rem,2.6vw,2.2rem)">Contact the IR team.</h2>
        <p>For investor inquiries, please contact <a class="link" href="mailto:{CO['email_ir']}">{CO['email_ir']}</a>. We welcome the opportunity to discuss the KQC investment opportunity.</p>
        <p class="mono" style="font-size:.9rem;color:var(--muted)">{CO['legal_name']}<br>c/o {CO['opco_name']}<br>{CO['address_busan']}<br>T {CO['phone_busan']}</p>
        <div class="button-row">{btn("mailto:" + CO['email_ir'], "Email investor relations", "primary", arrow=True)}{btn("contact.html", "Contact page")}</div>
      </article>
      {contact_side}
    </div>
  </div>
</section>

{more_section}
"""
    return layout("KQC Quantum Inc. | Investor Relations" if LEAN else f"Investor Relations | KQC Quantum Inc. | {L['exchange_short']}: {L['ticker']}",
                  "KQC Quantum Inc. investor relations: featured announcement and webcast, investor resources (presentations, filings, webcasts, news), email alerts and investor contact.",
                  body, canonical="" if LEAN else "investors.html", body_class="investors home" if LEAN else "investors", scripts=("field.js",))


def page_faq():
    faq_html = "".join(f'<details><summary>{q}<span class="plus"></span></summary><div class="faq-body"><p>{a}</p></div></details>' for q, a in C.FAQ)
    thesis_html = "".join(f'<article class="card spot"><p class="eyebrow">{t["n"]}</p><h3>{t["title"]}</h3><p class="muted">{t["text"]}</p></article>' for t in C.THESIS)
    body = page_hero(
        [("Home", "index.html"), ("Investors", "investors.html"), ("Investor FAQ", None)],
        "Investor FAQ",
        [CO["legal_name"], f"{L['exchange_short']}: {L['ticker']}", L["status_line"]],
        "Common questions about KQC Quantum Inc., the listing and how to reach investor relations.",
        [btn("investors.html", "Investor Relations", "primary", arrow=True), btn("investors.html#alerts", "Email alerts"), btn("mailto:" + CO["email_ir"], "Email IR")],
    ) + f"""
<section class="section section-tight">
  <div class="container">
    <div class="faq reveal">{faq_html}</div>
  </div>
</section>
<section class="section section-tight" id="thesis">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Investment case</p><h2>Why KQC.</h2>
      <p class="sub">Four reasons the company believes it is positioned to benefit as quantum computing, post-quantum security and AI infrastructure converge.</p></div>
    <div class="grid grid-2" data-stagger>{thesis_html}</div>
  </div>
</section>
"""
    return layout("Investor FAQ | KQC Quantum Inc. Investor Relations",
                  "Frequently asked questions from investors about KQC Quantum Inc. (KQC): listing status, incorporation, business lines, fiscal year, transfer agent and IR contact.",
                  body, canonical="faq.html", body_class="faq-page")


def page_stock():
    kv = [("Open", "N/A"), ("Previous close", "N/A"), ("Day range", "N/A"), ("52-week range", "N/A"), ("Volume", "N/A"), ("Avg. volume (3M)", "N/A"), ("Market cap", "N/A"), ("Shares outstanding", L["shares_outstanding"])]
    kv_html = "".join(f"<div>{k}<b>{v}</b></div>" for k, v in kv)
    share = [
        ("Common shares outstanding", L["shares_outstanding"], "[As of date]"),
        ("Public float", L["public_float"], "[As of date]"),
        ("Insider ownership", "[Pending]", "[As of date]"),
        ("Authorized shares", "[Pending]", "[Per charter]"),
        ("Warrants / convertible securities", "[Pending]", "[If applicable]"),
    ]
    share_html = "".join(f'<tr><td class="doc">{a}</td><td class="mono">{b}</td><td class="muted">{c}</td></tr>' for a, b, c in share)
    body = page_hero(
        [("Home", "index.html"), ("Investors", "investors.html"), ("Stock Information", None)],
        "Stock Information",
        [f"{L['exchange_short']}: {L['ticker']}", L["status_line"], f"CUSIP {L['cusip']}", f"ISIN {L['isin']}"],
        "Quote, chart and share-structure data will appear here once trading begins. Nothing on this page is live market data.",
        [btn("investors.html#alerts", "Get listing alerts", "primary", arrow=True), btn("filings.html", "Filings &amp; Financials")],
    ) + f"""
<section class="section section-tight">
  <div class="container">
    <article class="card spot quote-card reveal">
      <div>
        <p class="eyebrow">Quote</p>
        <div class="sym">{L['ticker']}</div>
        <div class="exch"><span>{L['exchange']}</span><span class="chip chip-orange">{L['status_line']}</span></div>
        <div class="price">N/A<span class="chg">Trading has not started</span></div>
        <div class="asof">Quote data not yet available &middot; Provider: [Market data vendor]</div>
      </div>
      <div class="kv">{kv_html}</div>
    </article>
  </div>
</section>

<section class="section section-tight">
  <div class="container">
    <article class="card chart-card reveal">
      <div class="chart-head">
        <div><p class="eyebrow" style="margin-bottom:.3rem">Price chart</p><h3 style="margin:0">{L['ticker']} &middot; {L['exchange_short']}</h3></div>
        <div class="ranges" aria-label="Chart range (inactive until listing)"><button type="button" class="active" disabled>1D</button><button type="button" disabled>1W</button><button type="button" disabled>1M</button><button type="button" disabled>6M</button><button type="button" disabled>1Y</button><button type="button" disabled>MAX</button></div>
      </div>
      <div class="chart-wrap">
        <canvas id="stock-chart" aria-label="Price chart placeholder, no data yet" role="img"></canvas>
        <div class="overlay"><div class="box">Chart activates when {L['ticker']} begins trading<small>No illustrative or simulated prices are shown on this site.</small></div></div>
      </div>
    </article>
  </div>
</section>

<section class="section section-tight" id="share-structure">
  <div class="container">
    <div class="grid grid-2" style="gap:2rem;align-items:start">
      <div class="reveal">
        <p class="eyebrow">Share structure</p>
        <h2>Capitalization.</h2>
        <div class="table-wrap"><table style="min-width:0"><thead><tr><th>Item</th><th>Value</th><th>As of</th></tr></thead><tbody>{share_html}</tbody></table></div>
      </div>
      <div class="grid" style="gap:1rem" data-stagger>
        <article class="card spot"><p class="eyebrow">Transfer agent</p><h3>{L['transfer_agent']}</h3><p class="muted">[Address, phone and shareholder-services contact to be published at listing.] Registered shareholders should contact the transfer agent for address changes, lost certificates and account questions.</p></article>
        <article class="card spot"><p class="eyebrow">Analyst coverage</p><h3>No coverage to report</h3><p class="muted">KQC will list firms that publish research on the company here. Any opinions, estimates or forecasts regarding KQC's performance made by analysts are theirs alone and do not represent the views of KQC.</p></article>
        <article class="card spot"><p class="eyebrow">Identifiers</p><dl class="dl" style="border:0;background:transparent;gap:.6rem"><div style="padding:0;background:transparent"><dt>CUSIP</dt><dd>{L['cusip']}</dd></div><div style="padding:0;background:transparent"><dt>ISIN</dt><dd>{L['isin']}</dd></div><div style="padding:0;background:transparent"><dt>SEC CIK</dt><dd>{L['cik']}</dd></div></dl></article>
      </div>
    </div>
  </div>
</section>

<section class="section section-tight legal">
  <div class="container reveal">
    <div class="callout">Stock price data, when available, will be provided by a third-party vendor and delayed by at least 15 minutes unless otherwise noted. KQC does not guarantee the accuracy or timeliness of market data and is not responsible for investment decisions made on the basis of it. Past performance is not indicative of future results.</div>
  </div>
</section>
"""
    return layout(f"Stock Information | {L['exchange_short']}: {L['ticker']} | KQC Quantum Inc.",
                  "Stock quote, chart, share structure, transfer agent and identifiers for KQC Quantum Inc. (KQC). Market data fields are placeholders until trading begins.",
                  body, canonical="stock.html", body_class="stock", scripts=("stock.js",))


def page_governance():
    exec_board = [m for m in C.LEADERSHIP if m.get("board")]
    board_cards = "".join(
        f'<article class="card spot board-card"><div class="role">{m["board"]}</div><h3>{m["name"]}</h3><p class="muted" style="font-size:.9rem">{m["title"]}, {CO["short_name"]}. {m["bio"][0][:150].rsplit(" ", 1)[0]}&hellip;</p><a class="link" href="about.html#{m["slug"]}">Biography <span class="arr">→</span></a></article>'
        for m in exec_board
    ) + "".join(
        f'<article class="card spot board-card"><div class="role">{b["role"]}</div><h3>{b["name"]}</h3><p class="muted" style="font-size:.9rem">[Biography, independence determination and committee assignments to be published at listing.]</p><div class="comm">{"".join(f"<span class=chip>{c}</span>" for c in b["committees"])}</div></article>'
        for b in C.BOARD_PLACEHOLDERS
    )
    rows = [("Jay J. H. Kweon", "Chair", "", "", ""), ("John J. Y. Kim, Ph.D.", "", "", "", "")]
    rows += [(b["name"] + f" ({i + 1})", "Independent", "C" if "Audit (Chair)" in b["committees"] else ("M" if "Audit" in b["committees"] else ""),
              "C" if "Compensation (Chair)" in b["committees"] else ("M" if "Compensation" in b["committees"] else ""),
              "C" if "Nominating &amp; Governance (Chair)" in b["committees"] else ("M" if "Nominating &amp; Governance" in b["committees"] else ""))
             for i, b in enumerate(C.BOARD_PLACEHOLDERS)]

    def mark(v):
        return '<span class="mark-chair">CHAIR</span>' if v == "C" else ('<span class="mark-member">&#9679;</span>' if v == "M" else '<span class="muted">&middot;</span>')

    comm_html = "".join(f'<tr><td class="doc">{n}</td><td>{r or "Executive"}</td><td class="center">{mark(a)}</td><td class="center">{mark(c)}</td><td class="center">{mark(g)}</td></tr>' for n, r, a, c, g in rows)
    docs = ["Code of Business Conduct and Ethics", "Corporate Governance Guidelines", "Audit Committee Charter", "Compensation Committee Charter", "Nominating and Corporate Governance Committee Charter", "Insider Trading Policy", "Whistleblower and Complaint Procedures", "Related-Party Transactions Policy", "Clawback Policy", "Articles of Incorporation and Bylaws"]
    docs_html = "".join(f'<div class="doc-row"><span class="name">{t}</span><span class="st">[PDF pending]</span></div>' for t in docs)
    execs_html = "".join(f'<tr><td class="doc">{m["name"]}</td><td>{m["title"]}</td><td class="muted">{m["korean"]}</td></tr>' for m in C.LEADERSHIP)

    body = page_hero(
        [("Home", "index.html"), ("Investors", "investors.html"), ("Corporate Governance", None)],
        "Corporate Governance",
        [CO["legal_name"], "Board of Directors", "Committees", "Policies"],
        "The board structure, committee charters and governance policies below are a template pending completion of the listing. Independent directors, independence determinations and adopted policies will be published here.",
        [btn("about.html#leadership", "Executive team", "primary", arrow=True), btn("filings.html", "Filings &amp; Financials")],
    ) + f"""
<section class="section section-tight" id="board">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Board of Directors</p><h2>Directors.</h2>
      <p class="sub">Executive directors reflect the company's published leadership; independent director seats are placeholders.</p></div>
    <div class="grid grid-3" data-stagger>{board_cards}</div>
  </div>
</section>

<section class="section section-tight" id="committees">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Committee composition</p><h2>Committees.</h2></div>
    <div class="table-wrap reveal"><table class="comm-table"><thead><tr><th>Director</th><th>Role</th><th class="center">Audit</th><th class="center">Compensation</th><th class="center">Nominating &amp; Governance</th></tr></thead><tbody>{comm_html}</tbody></table></div>
    <p class="notice mt-1">[Template. Committee membership to be confirmed by the board.]</p>
  </div>
</section>

<section class="section section-tight" id="documents">
  <div class="container">
    <div class="grid grid-2" style="gap:2rem;align-items:start">
      <div class="reveal">
        <p class="eyebrow">Governance documents</p><h2>Policies and charters.</h2>
        <div class="doc-list" style="margin-top:1.4rem">{docs_html}</div>
      </div>
      <div class="grid" style="gap:1rem" data-stagger>
        <article class="card spot"><p class="eyebrow">Executive officers</p>
          <div class="table-wrap" style="border:0;background:transparent"><table style="min-width:0"><thead><tr><th>Name</th><th>Title</th><th>Korean</th></tr></thead><tbody>{execs_html}</tbody></table></div></article>
        <article class="card spot"><p class="eyebrow">Independent auditor</p><h3>{L['auditor']}</h3><p class="muted">[To be published at listing.]</p></article>
        <article class="card spot"><p class="eyebrow">Contact the board</p><p class="muted">Shareholders and other interested parties may communicate with the Board of Directors, the independent directors or a committee by writing to the Corporate Secretary at {CO['address_busan']}, or by email to {CO['email_ir']}. [Procedure to be confirmed.]</p></article>
      </div>
    </div>
  </div>
</section>
"""
    return layout("Corporate Governance | KQC Quantum Inc. Investor Relations",
                  "Board of directors, committee composition, governance documents and executive officers of KQC Quantum Inc. (KQC).",
                  body, canonical="governance.html", body_class="governance")


def page_filings():
    def row(f):
        filed = fmt_date(f["date"], True) if f["date"] else "Not yet filed"
        if f["href"]:
            link = f'<a href="{f["href"]}" target="_blank" rel="noopener noreferrer">{f["desc"]}</a>'
            st = '<span class="dot-live"></span>Filed'
        else:
            link = f["desc"]; st = '<span class="dot-pending"></span>Pending'
        return f'<tr><td class="mono">{f["form"]}<br><small class="muted">{f["filer"]}</small></td><td class="doc">{link}</td><td class="mono">{filed}</td><td>{st}</td></tr>'
    f_html = "".join(row(f) for f in C.FILINGS)
    ir_home = "index.html" if LEAN else "investors.html"
    body = page_hero(
        [("Home", "index.html")] + ([] if LEAN else [("Investors", "investors.html")]) + [("Filings", None) if LEAN else ("Filings &amp; Financials", None)],
        "Filings" if LEAN else "Filings &amp; Financials",
        [CO["legal_name"], "Investor Relations", L["status_line"]] if LEAN else [f"SEC CIK {L['cik']}", f"Fiscal year end {L['fiscal_year_end']}", f"Auditor {L['auditor']}"],
        "Documents relating to the proposed business combination are filed with the SEC by Charlton Aria Acquisition Corporation (Nasdaq: CHAR) until KQC Quantum Inc. becomes a registrant with the filing of its Form S-4. Every row links to the filing on EDGAR." if LEAN else
        "Regulatory filings, financial reports and the financial calendar will be published here. Until the first filing is made, the table below is a template.",
        [btn(L["edgar_url"], "Charlton Aria on EDGAR ↗", "primary", ext=True), btn(ir_home + "#alerts", "Filing alerts")] + ([btn("index.html", "Investor Relations")] if LEAN else []),
    ) + f"""
<section class="section section-tight" id="sec">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Regulatory filings</p><h2>SEC filings.</h2>
      <p class="sub">Each filing opens on the SEC's EDGAR system. Shareholders of Charlton Aria and other interested persons are urged to read the proxy statement/prospectus and other relevant documents filed with the SEC when they become available, because they will contain important information about the business combination.</p></div>
    <div class="table-wrap reveal"><table><thead><tr><th>Form</th><th>Description</th><th>Filed</th><th>Status</th></tr></thead><tbody>{f_html}</tbody></table></div>
  </div>
</section>
""" + ("" if LEAN else f"""
<section class="section section-tight" id="highlights">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">Financial highlights</p><h2>Selected data.</h2>
      <p class="sub">Financial figures will be published here from the company's audited statements and filings. No third-party or unaudited figures are shown.</p></div>
    <div class="cells cells-4 reveal" data-stagger>
      <div class="stat"><div class="stat-n">[Pending]</div><div class="stat-l">FY2024 revenue [audited figure pending]</div></div>
      <div class="stat"><div class="stat-n">[Pending]</div><div class="stat-l">FY2025 revenue [audited figure pending]</div></div>
      <div class="stat"><div class="stat-n">[Pending]</div><div class="stat-l">Cash and equivalents [as of date]</div></div>
      <div class="stat"><div class="stat-n">27</div><div class="stat-l">Employees ({CO['employees_asof']}), including 9 Ph.D.s</div></div>
    </div>
  </div>
</section>

<section class="section section-tight" id="reports">
  <div class="container">
    <div class="grid grid-2" style="gap:2rem;align-items:start">
      <div class="reveal">
        <p class="eyebrow">Annual reports &amp; presentations</p><h2>Documents.</h2>
        <div class="doc-list" style="margin-top:1.4rem">
          <div class="doc-row"><span class="name">Annual report [FY2025]</span><span class="st">[PDF pending]</span></div>
          <div class="doc-row"><span class="name">Investor presentation</span><span class="st">[PDF pending]</span></div>
          <div class="doc-row"><span class="name">Corporate fact sheet</span><span class="st">[PDF pending]</span></div>
          <div class="doc-row"><span class="name">ISO/IEC 27001 certificate</span><span class="st">[PDF pending]</span></div>
        </div>
      </div>
      <div class="reveal">
        <p class="eyebrow">Financial calendar</p><h2>Dates.</h2>
        <div class="table-wrap" style="margin-top:1.4rem"><table style="min-width:0"><thead><tr><th>Date</th><th>Event</th></tr></thead><tbody>
          <tr><td class="mono">[Date]</td><td class="doc">[First periodic report]</td></tr>
          <tr><td class="mono">[Date]</td><td class="doc">[Annual meeting of shareholders]</td></tr>
          <tr><td class="mono">[Date]</td><td class="doc">[Fiscal year end: {L['fiscal_year_end']}]</td></tr>
        </tbody></table></div>
      </div>
    </div>
  </div>
</section>
""") + (alerts_block() if LEAN else "")
    return layout(("Filings | " if LEAN else "Filings & Financials | ") + "KQC Quantum Inc. Investor Relations",
                  "SEC filings for KQC Quantum Inc. (KQC), linked from EDGAR." if LEAN else "SEC filings, financial highlights, annual reports and the financial calendar for KQC Quantum Inc. (KQC).",
                  body, canonical="filings.html", body_class="filings")


def resource_items_html(items):
    rows = []
    for i, it in enumerate(items):
        pending = it["status"] != "live"
        href = it["href"] or "#alerts"
        ext = href.startswith("http") or href.endswith(".pdf")
        rows.append(
            f'<a class="res-row{" pending" if pending else ""}" href="{href}"{" target=_blank rel=noopener" if ext else ""}>'
            f'<span class="res-ico">{str(i + 1).zfill(2)}</span>'
            f'<span class="res-main"><span class="res-title">{it["title"]}</span><span class="res-kind">{it["kind"]}{(" &middot; " + it["date"]) if it.get("date") else ""}</span></span>'
            f'<span class="res-st">{"Coming soon" if pending else "View"} <span class="arr">\u2192</span></span></a>'
        )
    return "".join(rows)


def webcast_panel(r):
    """Player-style panel for the featured webcast. NetRoadshow refuses to be framed, so the panel opens the event."""
    it = next((i for i in r["items"] if i["status"] == "live" and i["href"]), None)
    if not it:
        return ""
    return f"""<a class="webcast-panel reveal" href="{it['href']}" target="_blank" rel="noopener noreferrer" aria-label="Watch the {it['title']} on NetRoadshow (opens in a new tab)">
      <span class="wp-art" aria-hidden="true">{SYMBOL}</span>
      <span class="wp-play" aria-hidden="true"><svg viewBox="0 0 24 24" width="30" height="30"><path d="M8 5.5v13l11-6.5z" fill="currentColor"/></svg></span>
      <span class="wp-meta"><span class="eyebrow" style="margin:0">Webcast &middot; {it.get('date', '')}</span><span class="wp-title">{it['title']}</span>
        <span class="wp-note">Hosted by NetRoadshow. Opens in a new tab; the host may ask for a name and email before playback.</span></span>
    </a>"""


def page_resource(slug):
    r = next(x for x in C.RESOURCE_PAGES if x["slug"] == slug)
    if slug == "presentations":
        lede = "Investor presentations and related materials. Subscribe to email alerts to be notified when new materials are posted."
        note = "" if any(i["status"] == "live" for i in r["items"]) else "No presentation has been published yet."
    else:
        lede = "Webcasts and investor events for KQC Quantum Inc. Subscribe to email alerts to be notified of new events."
        note = "" if any(i["status"] == "live" for i in r["items"]) else "No webcast has been scheduled yet."
    body = page_hero(
        [("Home", "index.html"), (r["title"], None)],
        r["title"],
        [CO["legal_name"], "Investor Relations", L["status_line"]],
        lede,
        [btn("index.html#alerts", "Email alerts", "primary", arrow=True), btn("index.html", "Investor Relations"), btn("contact.html", "Contact IR")],
    ) + f"""
<section class="section section-tight">
  <div class="container">
    <div class="section-head reveal"><p class="eyebrow">{r["title"]}</p><h2>{r["blurb"]}</h2>
      <p class="sub">{(note + " Items marked Coming soon will link to the published materials.") if any(i["status"] != "live" for i in r["items"]) else ("The webcast opens on the host's site in a new tab; the transcript opens as PDF." if slug == "webcasts" else "Documents open as PDF in a new tab.")}</p></div>
    {webcast_panel(r) if slug == "webcasts" else ""}
    <div class="res-list reveal" data-stagger>{resource_items_html(r["items"])}</div>
  </div>
</section>

{alerts_block()}
"""
    return layout(f"{r['title']} | KQC Quantum Inc. Investor Relations",
                  f"KQC Quantum Inc. investor relations: {r['blurb'].lower()}",
                  body, canonical=f"{slug}.html", body_class="resource")


def page_redirect(target, title):
    """Tiny page that forwards an old or alias URL to its real page (investors.html, press.html, webcast.html in IR mode)."""
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title>'
            f'<meta http-equiv="refresh" content="0; url={target}"><link rel="canonical" href="{SITE}/{target}"><link rel="icon" type="image/svg+xml" href="assets/images/favicon.svg">'
            f'<meta name="robots" content="noindex"></head><body><p>This page has moved to <a href="{target}">{target}</a>.</p></body></html>\n')


def page_press():
    if LEAN:
        return page_news()
    rows = "".join(press_row(p, "") for p in press_public())
    body = page_hero(
        [("Home", "index.html"), ("Press", None)],
        "Press Releases &amp; News",
        [f"{len(press_public())} items", "2024 &ndash; 2026", "Corporate newsroom on kqchub.com"],
        "Company announcements and selected media coverage. Items marked as prepared from public coverage will be replaced by official company text before launch.",
        [btn("investors.html#alerts", "Press release alerts", "primary", arrow=True), btn("https://www.kqchub.com/en/newsroom", "Corporate newsroom ↗", ext=True), btn("contact.html", "Media contact")],
    ) + f"""
<section class="section section-tight">
  <div class="container">
    <div class="filters reveal" id="press-filters" aria-label="Filter news"></div>
    <p class="notice" style="margin:-.6rem 0 1.2rem"><span id="press-count">{len(press_public())} items</span></p>
    <div class="press-list" id="press-list">{rows}</div>
  </div>
</section>
"""
    return layout("Press Releases & News | KQC Quantum Inc.",
                  "Press releases and news coverage of KQC Quantum Inc. (KQC) and its operating company Korea Quantum Computing Co., Ltd.: quantum computing, post-quantum security and AI infrastructure announcements.",
                  body, canonical="press.html", body_class="press")


def page_news():
    items = press_public()
    years = sorted({p["date"][:4] for p in items})
    rows = "".join(press_row(p, "") for p in items)
    body = page_hero(
        [("Home", "index.html"), ("News", None)],
        "News",
        [f"{len(items)} items", f"{years[0]} &ndash; {years[-1]}", "Company releases and press coverage"],
        "Company press releases are published here in full. Press coverage links to the publication that carried it.",
        [btn("index.html#alerts", "Email alerts", "primary", arrow=True), btn("https://www.kqchub.com/en/newsroom", "Corporate newsroom ↗", ext=True), btn("contact.html", "Media contact")],
    ) + f"""
<section class="section section-tight">
  <div class="container">
    <div class="press-list press-list--static reveal">{rows}</div>
  </div>
</section>
"""
    return layout("News | KQC Quantum Inc. Investor Relations",
                  "News and press coverage of KQC Quantum Inc. and its operating company Korea Quantum Computing Co., Ltd.",
                  body, canonical="news.html", body_class="press")


def page_press_article(p):
    d = "../"
    src = f' &middot; <a href="{p["source_url"]}" target="_blank" rel="noopener noreferrer">Source: {p["source_name"]} ↗</a>' if p.get("source_url") else ""
    if p.get("official"):
        note = ""
    elif p["type"] == "draft":
        note = "Draft template. Not for publication. Hidden from public lists until <code>type</code> is changed from <code>draft</code> in tools/content.py."
    elif p["type"] == "media":
        note = f"Summary of third-party coverage prepared for the investor site. It is not a company press release; the views reported are those of the publication and the individuals quoted. Read the original at {p['source_name']}."
    else:
        note = f"Prepared from public coverage ({p['source_name']}, {fmt_date(p['date'])}) for the investor site. Official company text should replace this summary before publication."
    kind = type_label(p["type"])
    dateline = f'<strong>{p["location"].upper()}, {fmt_date(p["date"])}.</strong> '
    paras = [f"<p>{para}</p>" for para in p["body"]]
    for i, para in enumerate(p["body"]):
        if not para.startswith("<"):
            paras[i] = "<p>" + dateline + para + "</p>"
            break
    body_html = "".join(paras)
    boiler = "" if p.get("official") else f"""
        <div class="press-divider"></div>
        <h3>About Korea Quantum Computing Co., Ltd. (operating company)</h3>
        <p>{C.BOILERPLATE}</p>
        <h3>Forward-looking statements</h3>
        <p>This communication may contain forward-looking statements within the meaning of applicable securities laws, including statements regarding the company's products, partnerships, facilities, certifications and plans for a public listing. Forward-looking statements are based on current expectations and are subject to risks and uncertainties, many of which are beyond the company's control, and actual results may differ materially. This communication is for informational purposes only and does not constitute an offer to sell or a solicitation of an offer to buy any securities.</p>
        <h3>Investor and media contact</h3>
        <p class="mono" style="font-size:.9rem">{CO['legal_name']}<br>Investor Relations: {CO['email_ir']}<br>General: {CO['email_general']}<br>T {CO['phone_busan']}<br>{CO['site_url'].replace('https://', '')}/investors &middot; kqchub.com</p>"""
    body = f"""<section class="page-hero bg-grid" style="padding-bottom:1.5rem">
  <div class="orb"></div>
  <div class="container">
    <nav class="breadcrumb" aria-label="Breadcrumb"><a href="../index.html">Home</a><span class="sep">/</span><a href="{"../news.html" if LEAN else "../press.html"}">{"News" if LEAN else "Press"}</a><span class="sep">/</span><span>{kind}</span></nav>
    <p class="eyebrow fade-up" style="--d:0">{kind}</p>
  </div>
</section>
<section class="section section-tight">
  <div class="container-narrow">
    <article class="press-article reveal in-view">
      <div class="press-meta-bar"><span>{fmt_date(p['date'])}</span><span>{p['location']}</span><span>{L['exchange_short']}: {L['ticker']}</span><span>{kind}{src}</span></div>
      <h1>{p['headline']}</h1>
      <p class="subhead">{p['sub']}</p>
      {f'<div class="draft-note"><span>{note}</span></div>' if note else ''}
      <div class="press-body">{body_html}{boiler}
      </div>
      <div class="press-nav">{btn("../news.html" if LEAN else "../press.html", "← All news" if LEAN else "← All press releases")}<button class="btn btn-ghost" type="button" onclick="window.print()">Print</button>{btn(p["source_url"], "On Business Wire ↗" if p.get("official") else "Original coverage ↗", ext=True) if p.get("source_url") else ""}</div>
    </article>
    <div class="more-news">
      <div class="row between" style="margin-bottom:1.2rem"><p class="eyebrow" style="margin:0">More news</p><a class="link" href="{"../news.html" if LEAN else "../press.html"}">{"All news" if LEAN else "All press releases"} <span class="arr">→</span></a></div>
      <div class="press-grid" id="press-more" data-current="{p['slug']}">{"".join(press_card(x, d) for x in [q for q in press_public() if q["slug"] != p["slug"]][:3])}</div>
    </div>
  </div>
</section>
"""
    title = f"{p['headline'][:90]}{'…' if len(p['headline']) > 90 else ''} | KQC Press"
    return layout(title, p["excerpt"][:300], body, depth=d, canonical=f"press/{p['slug']}.html", body_class="press-article-page", og_type="article")


def page_disclosure():
    sources = [
        ("Company website and newsroom", "https://www.kqchub.com/en/", "Products, leadership titles, history, offices, brand"),
        ("IBM Newsroom, Jan 29 2024", "https://newsroom.ibm.com/2024-01-29-Korea-Quantum-Computing-and-IBM-Collaborate-to-Bring-IBM-watsonx-and-Quantum-Computing-to-Korea", "IBM collaboration and System Two plans"),
        ("The Electronic Times, Jun 30 2026", "https://www.etnews.com/20260630000013", "Qubiteer launch"),
        ("MoneyToday, Jun 4 2026", "https://www.mt.co.kr/industry/2026/06/04/2026060409530962952", "LS ITC proof of concept"),
        ("Digital Daily, May 27 2026", "https://www.ddaily.co.kr/page/view/2026052716082283402", "CTO interview"),
        ("MoneyToday, Apr 16 2026", "https://www.mt.co.kr/industry/2026/04/16/2026041612523010217", "Excellent Technology Award"),
        ("Today Energy, Mar 12 2026", "https://www.todayenergy.kr/news/articleView.html?idxno=295122", "ISO/IEC 27001 certification"),
        ("The Electronic Times, Dec 9 2025", "https://www.etnews.com/20251209000100", "IBK proof of concept"),
        ("VentureSquare, Nov 20 2025", "https://www.venturesquare.net/1015228", "Quantum AI MOU"),
        ("EBN, Oct 14 2025", "https://www.ebn.co.kr/news/articleView.html?idxno=1682211", "KSBI MOU"),
        ("The Electronic Times, Jul 23 2025", "https://www.etnews.com/20250723000230", "Crypto4A partnership"),
        ("ZDNet Korea, Jul 10 2025", "https://zdnet.co.kr/view/?no=20250710160445", "KIOST MOU"),
        ("ZDNet Korea, Jul 3 2025", "https://zdnet.co.kr/view/?no=20250703101837", "H200 GPU farm launch"),
        ("Catch / NICE BizInfo", "https://www.catch.co.kr/Comp/CompSummary/OU6371", "Headcount (27 as of 2025)"),
    ]
    src_html = "".join(f'<tr><td class="doc"><a href="{u}" target="_blank" rel="noopener noreferrer">{n} ↗</a></td><td class="muted">{w}</td></tr>' for n, u, w in sources)
    body = page_hero(
        [("Home", "index.html"), ("Disclosure", None)],
        "Disclosure &amp; Legal",
        ["Forward-looking statements", "No offer", "Privacy", "Sources"],
        "Important information about the content of this website.",
    ) + f"""
<section class="section section-tight legal" id="forward-looking">
  <div class="container-narrow reveal">
    <p class="eyebrow">Forward-looking statements</p><h2>Safe harbor.</h2>
    <p>This website contains statements that may constitute forward-looking statements within the meaning of Section 27A of the U.S. Securities Act of 1933, as amended, Section 21E of the U.S. Securities Exchange Act of 1934, as amended, and other applicable securities laws. Forward-looking statements include, without limitation, statements regarding a potential public listing and its terms and timing; the deployment of an IBM Quantum System Two and the KQC Quantum Computing Center in Busan; product roadmaps including Qubiteer, QxHSM&trade;, QuHSM&trade;, QuKey Bio and KQC GPUaaS; certifications; partnerships; market opportunity; and financial performance.</p>
    <p>These statements are based on current expectations and assumptions and are subject to known and unknown risks and uncertainties, many of which are beyond the company's control, including the completion of any listing transaction, regulatory approvals, competition, technological change, customer adoption, the availability of capital and macroeconomic conditions in Korea and globally. Actual results may differ materially from those expressed or implied. The company undertakes no obligation to update any forward-looking statement except as required by law.</p>
  </div>
</section>
<section class="section section-tight legal" id="no-offer">
  <div class="container-narrow reveal">
    <p class="eyebrow">No offer or solicitation</p><h2>Not an offer of securities.</h2>
    <p>This website and its contents are for informational purposes only and do not constitute an offer to sell, or a solicitation of an offer to buy, any securities in any jurisdiction, nor shall there be any sale of securities in any jurisdiction in which such offer, solicitation or sale would be unlawful prior to registration or qualification under the securities laws of that jurisdiction. Any offering of securities will be made only by means of a prospectus or other offering document meeting the requirements of applicable law.</p>
    <p>Market-data fields, ticker symbols, exchange names, identifiers, board composition, committee assignments and filing tables shown in [brackets] are placeholders and do not represent facts about any listed security.</p>
  </div>
</section>
<section class="section section-tight legal" id="sources">
  <div class="container-narrow reveal">
    <p class="eyebrow">Sources and status</p><h2>How this site was prepared.</h2>
    <p>Company facts on this site were drawn from the company's corporate website and from published press coverage as of September 2026. Press-release pages marked as prepared from public coverage are summaries drafted for this investor site and are not official company releases until replaced with company text. Where coverage was in Korean, quotations are translations. Executive biographies marked as compiled were assembled from public profiles and interviews and should be confirmed by the company.</p>
    <div class="table-wrap" style="margin-top:1.2rem"><table style="min-width:0"><thead><tr><th>Source</th><th>Used for</th></tr></thead><tbody>{src_html}</tbody></table></div>
  </div>
</section>
<section class="section section-tight legal" id="privacy">
  <div class="container-narrow reveal">
    <p class="eyebrow">Privacy</p><h2>Privacy notice.</h2>
    <p>This website does not set tracking cookies and does not use third-party analytics. Fonts are served from this site's own servers. If you submit the email-alert or contact forms, the information you provide is used only to respond to your request and to send the investor communications you asked for; you may unsubscribe at any time. [Data-protection contact, retention periods and any analytics or alert vendors to be confirmed and disclosed here before launch, in line with Korea's Personal Information Protection Act and other applicable law.] The company's corporate privacy policy is available at <a href="https://www.kqchub.com/en/privacypolicy" target="_blank" rel="noopener noreferrer">kqchub.com</a>.</p>
  </div>
</section>
<section class="section section-tight legal" id="trademarks">
  <div class="container-narrow reveal">
    <p class="eyebrow">Trademarks</p><h2>Marks.</h2>
    <p>KQC, the KQC symbol, QuHSM&trade;, QuKey Bio and Qubiteer are trademarks of KQC Quantum Inc. or its operating company Korea Quantum Computing Co., Ltd. QxHSM&trade; and QxVault&trade; are trademarks of Crypto4A Technologies Inc. IBM, IBM Quantum and watsonx are trademarks of International Business Machines Corporation. NVIDIA and H200 are trademarks of NVIDIA Corporation. Other names may be trademarks of their respective owners and are used for identification only.</p>
  </div>
</section>
"""
    return layout("Disclosure & Legal | KQC Quantum Inc. Investor Relations",
                  "Forward-looking statements, no-offer notice, sources, privacy notice and trademarks for the KQC Quantum Inc. investor relations website.",
                  body, canonical="disclosure.html", body_class="disclosure")


def page_contact():
    body = page_hero(
        [("Home", "index.html"), ("Contact", None)],
        "Contact Investor Relations",
        [CO["email_ir"], CO["email_general"], CO["phone_busan"]],
        "Investor, analyst and media inquiries. Responses to investor and media inquiries are prioritized; for time-sensitive matters, please call the Busan headquarters.",
    ) + f"""
<section class="section section-tight">
  <div class="container contact-grid">
    <div class="contact-cards" data-stagger>
      <article class="card spot"><p class="eyebrow">Investor relations</p><h3>Investors &amp; analysts</h3><p class="muted">Questions about the company, the listing or this website.</p><p class="mono" style="font-size:.9rem">{CO['email_ir']}<br>{CO['email_general']}</p></article>
      <article class="card spot"><p class="eyebrow">Media</p><h3>Press inquiries</h3><p class="muted">Interview requests, press materials and brand assets.</p><p class="mono" style="font-size:.9rem">{CO['email_press']}</p></article>
      <article class="card spot office"><div class="k">Headquarters</div><h3>Busan</h3><p>{CO['address_busan_l1']}<br>{CO['address_busan_l2']}</p><p class="mono tel">T {CO['phone_busan']} &nbsp;&middot;&nbsp; F {CO['fax_busan']}</p></article>
      <article class="card spot office"><div class="k">Office</div><h3>Seoul</h3><p>{CO['address_seoul_l1']}<br>{CO['address_seoul_l2']}</p><p class="mono tel">T {CO['phone_seoul']} &nbsp;&middot;&nbsp; F {CO['fax_seoul']}</p></article>
    </div>
    <article class="card card-pad-lg reveal">
      <p class="eyebrow">Send a message</p>
      <h3>How can we help?</h3>
      <form id="contact-form" method="post" action="#" novalidate>
        <div class="form-row">
          <div class="field"><label for="c-name">Name *</label><input class="input" id="c-name" name="name" type="text" required autocomplete="name"></div>
          <div class="field"><label for="c-email">Email *</label><input class="input" id="c-email" name="email" type="email" required autocomplete="email"></div>
        </div>
        <div class="form-row">
          <div class="field"><label for="c-org">Organization</label><input class="input" id="c-org" name="org" type="text" autocomplete="organization"></div>
          <div class="field"><label for="c-type">Inquiry type</label><select class="select" id="c-type" name="inquiry"><option>Investor Relations</option><option>Analyst coverage</option><option>Media / Press</option><option>Business development</option><option>Careers</option><option>Other</option></select></div>
        </div>
        <div class="field"><label for="c-msg">Message *</label><textarea class="textarea" id="c-msg" name="message" required></textarea></div>
        <label class="consent"><input type="checkbox" name="consent" required> I agree that KQC may use the information provided to respond to my inquiry, as described in the <a href="disclosure.html#privacy" style="text-decoration:underline">privacy notice</a>.</label>
        <div class="button-row"><button class="btn btn-primary" type="submit">Send message</button></div>
      </form>
    </article>
  </div>
</section>
"""
    return layout("Contact Investor Relations | KQC Quantum Inc.",
                  "Contact KQC Quantum Inc. investor relations and media relations. Offices in Busan and Seoul, Republic of Korea.",
                  body, canonical="contact.html", body_class="contact")


def page_404():
    body = f"""<section class="nf bg-grid"><div class="container"><div class="code">404 &middot; Superposition collapsed</div><h1>Page not found.</h1><p class="lede" style="margin:0 auto 1.6rem">The page you were looking for does not exist or has moved.</p><div class="button-row" style="justify-content:center">{btn("index.html", "Home", "primary", arrow=True)}{btn("news.html" if LEAN else "investors.html", "News" if LEAN else "Investor Relations")}{btn("contact.html" if LEAN else "press.html", "Contact IR" if LEAN else "Press")}</div></div></section>"""
    return layout("Page not found | KQC Quantum Inc.", "Page not found.", body, canonical="404.html", body_class="notfound")


# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------
def press_data_js():
    src = press_public() if LEAN else C.PRESS
    items = [{k: p[k] for k in ("slug", "date", "type", "headline", "excerpt", "tags", "source_name")} for p in src]
    if LEAN:
        for it, p in zip(items, src):
            it["url"] = p.get("source_url", "")
    return "/* Generated by tools/build.py from tools/content.py. Do not edit by hand. */\nwindow.KQC_PRESS = " + json.dumps(items, ensure_ascii=False, indent=1) + ";\n"


def sitemap(pages):
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod></url>\n" for p in pages)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'


def holding_page():
    """Self-contained "coming soon" page in holding/, published by the static site until go-live."""
    import shutil
    hdir = os.path.join(ROOT, "holding")
    os.makedirs(os.path.join(hdir, "assets"), exist_ok=True)
    for f in ("geist-latin-wght-normal.woff2", "geist-mono-latin-wght-normal.woff2", "orbitron-latin-800-normal.woff2"):
        shutil.copy(os.path.join(ROOT, "assets", "fonts", f), os.path.join(hdir, "assets", f))
    shutil.copy(os.path.join(ROOT, "assets", "images", "favicon.svg"), os.path.join(hdir, "assets", "favicon.svg"))
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{CO['legal_name']} | Investor Relations</title>
<meta name="description" content="Investor relations for {CO['legal_name']}.">
<meta name="robots" content="noindex,nofollow">
<link rel="icon" type="image/svg+xml" href="assets/favicon.svg">
<style>
@font-face {{ font-family: Geist; src: url(assets/geist-latin-wght-normal.woff2) format("woff2"); font-weight: 100 900; font-display: swap; }}
@font-face {{ font-family: "Geist Mono"; src: url(assets/geist-mono-latin-wght-normal.woff2) format("woff2"); font-weight: 100 900; font-display: swap; }}
@font-face {{ font-family: Orbitron; src: url(assets/orbitron-latin-800-normal.woff2) format("woff2"); font-weight: 800; font-display: swap; }}
:root {{ color-scheme: dark; }}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; min-height: 100%; }}
body {{ background: radial-gradient(900px 520px at 78% 18%, rgba(1,33,105,.55), transparent 62%), #02040b; color: #eef3ff; font: 16px/1.6 Geist, system-ui, -apple-system, "Segoe UI", sans-serif; display: grid; place-items: center; padding: 24px 16px; min-height: 100svh; }}
main {{ width: 100%; max-width: 640px; }}
.brand {{ display: flex; align-items: center; gap: 14px; margin-bottom: 44px; }}
.brand svg {{ width: 34px; height: 34px; color: #99b8ff; filter: drop-shadow(0 0 10px rgba(59,116,255,.45)); }}
.brand b {{ font-family: Orbitron, "Geist Mono", ui-monospace, monospace; font-size: 1.28rem; letter-spacing: .06em; font-weight: 800; color: #fff; line-height: 1; }}
.brand span {{ font-family: "Geist Mono", ui-monospace, monospace; font-size: .62rem; letter-spacing: .22em; text-transform: uppercase; color: #8593bb; border-left: 1px solid rgba(153,184,255,.3); padding-left: 12px; line-height: 1.2; }}
.eyebrow {{ font-family: "Geist Mono", ui-monospace, monospace; font-size: .68rem; letter-spacing: .2em; text-transform: uppercase; color: #8aa6e8; display: flex; align-items: center; gap: 10px; margin: 0 0 14px; }}
.eyebrow::before {{ content: ""; width: 22px; height: 1px; background: linear-gradient(90deg, #3b74ff, transparent); }}
h1 {{ font-size: clamp(2rem, 5vw, 3rem); line-height: 1.05; letter-spacing: -.03em; margin: 0 0 18px; font-weight: 500; }}
p {{ margin: 0 0 14px; color: #b9c4e6; max-width: 46ch; }}
a {{ color: #99b8ff; text-decoration: none; }} a:hover {{ text-decoration: underline; }}
.foot {{ margin-top: 48px; padding-top: 18px; border-top: 1px solid rgba(153,184,255,.14); font-size: .74rem; color: #56638c; line-height: 1.6; }}
</style>
</head>
<body>
<main>
  <div class="brand">{SYMBOL}<b>KQC</b><span>Quantum<br>Inc.</span></div>
  <p class="eyebrow">Investor Relations</p>
  <h1>{CO['legal_name']}</h1>
  <p>The investor relations site for {CO['legal_name']} will be available here soon.</p>
  <p>Investor inquiries: <a href="mailto:{CO['email_ir']}">{CO['email_ir']}</a></p>
  <div class="foot">&copy; {CO['copyright_year']} {CO['legal_name']} All rights reserved. Nothing on this page constitutes an offer to sell or a solicitation of an offer to buy any securities.</div>
</main>
</body>
</html>
"""
    write("holding/index.html", html)
    write("holding/robots.txt", "User-agent: *\nDisallow: /\n")


def robots_txt():
    if not INDEXING:
        return "User-agent: *\nDisallow: /\n"
    return f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n"


def llms_txt():
    if LEAN:
        lines = [f"# {CO['legal_name']} (KQC): Investor Relations", "",
                 f"> {CO['tagline']} {CO['structure']} Listing status: {L['status_line']}.", "",
                 "## Pages", "- /index.html: Investor relations home (featured announcement, investor resources, email alerts, investor contact)",
                 "- /presentations.html: Investor presentations", "- /filings.html: SEC filings", "- /webcasts.html: Webcasts and replays",
                 "- /news.html: News and press coverage (links to the original publications)", "- /contact.html: Contact investor relations", "- /disclosure.html: Legal notices and sources", "",
                 "## News"]
        for p in press_public():
            lines.append(f"- {p['date']}: {p['headline']} ({p.get('source_url') or '/news.html'})")
        return "\n".join(lines) + "\n"
    lines = [f"# {CO['legal_name']} (KQC): Investor Relations", "",
             f"> {CO['tagline']} Founded {CO['founded']}; headquartered in Busan, Republic of Korea. Listing status: {L['status_line']} ({L['exchange_short']}: {L['ticker']} are placeholders).", "",
             "## Pages", "- /index.html: Overview", "- /about.html: Company, leadership, history", "- /investors.html: Featured announcement, resources, news, alerts, IR contact", "- /faq.html: Investor FAQ",
             "- /stock.html: Stock information (placeholders until listing)", "- /filings.html: Filings and financials", "- /governance.html: Board and governance", "- /press.html: Press releases and news", "- /contact.html: Contact", "- /disclosure.html: Legal and sources", "",
             "## Press releases"]
    for p in press_public():
        lines.append(f"- {p['date']}: {p['headline']} (/press/{p['slug']}.html)")
    return "\n".join(lines) + "\n"


def remove(rel):
    path = os.path.join(ROOT, rel)
    if os.path.exists(path):
        os.remove(path)
        print("  removed", rel)


def main():
    print(f"Building KQC IR site ({MODE} mode) →", ROOT)
    if LEAN:
        pages = {
            "index.html": page_investors(), "presentations.html": page_resource("presentations"), "filings.html": page_filings(),
            "webcasts.html": page_resource("webcasts"), "news.html": page_news(), "contact.html": page_contact(),
            "disclosure.html": page_disclosure(), "404.html": page_404(),
        }
        # webcast.html: singular alias used in press releases (kqcquantum.com/webcast); Render also rewrites /webcast
        redirects = {"investors.html": ("index.html", "Investor Relations"), "investor.html": ("index.html", "Investor Relations"),
                     "press.html": ("news.html", "News"),
                     "webcast.html": ("webcasts.html", "Webcasts")}
        for rel, html in pages.items():
            write(rel, html)
        for rel, (target, title) in redirects.items():
            write(rel, page_redirect(target, title))
        # pages that exist only in the full build
        for rel in ("about.html", "stock.html", "governance.html", "faq.html"):
            remove(rel)
        official = [p for p in press_public() if p.get("official")]
        keep = {f"{p['slug']}.html" for p in official}
        press_dir = os.path.join(ROOT, "press")
        if os.path.isdir(press_dir):
            for f in os.listdir(press_dir):
                if f.endswith(".html") and f not in keep:
                    remove(f"press/{f}")
        for p in official:
            write(f"press/{p['slug']}.html", page_press_article(p))
        write("assets/js/press-data.js", press_data_js())
        public_pages = [k for k in pages if k != "404.html"] + [f"press/{p['slug']}.html" for p in official]
        write("sitemap.xml", sitemap(public_pages))
        write("robots.txt", robots_txt())
        write("llms.txt", llms_txt())
        holding_page()
        print(f"Done: {len(pages)} pages + {len(redirects)} redirects (IR mode, indexing {'on' if INDEXING else 'off'}).")
        return
    pages = {
        "index.html": page_home(), "about.html": page_about(), "investors.html": page_investors(), "faq.html": page_faq(), "stock.html": page_stock(),
        "governance.html": page_governance(), "filings.html": page_filings(), "press.html": page_press(),
        "disclosure.html": page_disclosure(), "contact.html": page_contact(), "404.html": page_404(),
    }
    for rel, html in pages.items():
        write(rel, html)
    for p in C.PRESS:
        write(f"press/{p['slug']}.html", page_press_article(p))
    write("assets/js/press-data.js", press_data_js())
    public_pages = [k for k in pages if k != "404.html"] + [f"press/{p['slug']}.html" for p in press_public()]
    write("sitemap.xml", sitemap(public_pages))
    write("robots.txt", robots_txt())
    write("llms.txt", llms_txt())
    print(f"Done: {len(pages)} pages, {len(C.PRESS)} press articles (indexing {'on' if INDEXING else 'off'}).")


if __name__ == "__main__":
    main()

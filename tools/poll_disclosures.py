#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Disclosure poller for the KQC Quantum Inc. investor-relations site.

Checks two sources, records anything new under data/, then rebuilds the site:

  * SEC EDGAR, through the submissions API, for every tracked registrant. Today that is Charlton Aria
    Acquisition Corp (CIK 0002024459), which files the transaction documents. KQC Quantum Inc. is added
    automatically once EDGAR knows it (it gets its own CIK when the Form S-4 is filed).
  * Press releases: KQC distributes through Business Wire. Business Wire answers scripts with HTTP 403, so new
    releases are discovered through Nasdaq's per-symbol RSS feed (Business Wire delivers every ticker-tagged
    release to it; CHAR now, KQC once it trades) with the Business Wire newsroom search tried as well. Each release
    is reproduced on the site (news.html and press/<slug>.html) from whichever copy can be read (Business Wire,
    else the nasdaq.com copy, which also names the Business Wire original) and linked to Business Wire. A release
    whose text could not be read is still listed, linking out, and its text is retried on later runs.

Run by .github/workflows/disclosures.yml at 9 AM and 5 PM Eastern, and by hand:

    python3 tools/poll_disclosures.py             # fetch, update data/, rebuild the site
    python3 tools/poll_disclosures.py --dry-run   # fetch and report, change nothing
    python3 tools/poll_disclosures.py --no-build  # update data/ but do not run tools/build.py

Data files (committed, hand-editable; the poller only appends, it never rewrites an existing entry):
    data/filings.json    SEC filings shown on filings.html
    data/releases.json   Business Wire releases shown on news.html

No third-party dependencies. Python 3.9+ (zoneinfo).
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

try:
    from zoneinfo import ZoneInfo
    EASTERN = ZoneInfo("America/New_York")
except Exception:  # pragma: no cover
    EASTERN = dt.timezone(dt.timedelta(hours=-5))

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
FILINGS_PATH = os.path.join(DATA, "filings.json")
RELEASES_PATH = os.path.join(DATA, "releases.json")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Registrants whose EDGAR filings are shown. CIK (10 digits) -> label shown under the form type.
EDGAR_CIKS = {
    "0002024459": "Charlton Aria",
}
# EDGAR entity names to watch for: when an entity whose name contains one of these appears on EDGAR,
# its CIK is added to the tracked set (and remembered in data/filings.json). Label = value.
DISCOVER_ENTITIES = {
    "kqc quantum": "KQC Quantum Inc.",
}
# Ignore filings before this date (CHAR's own pre-transaction filings are not KQC investor material).
# The extension proxy of Sep 23 2026 is the first document that concerns the KQC transaction.
EDGAR_SINCE = "2026-09-23"
# Third-party and administrative form types that are not company disclosures.
EDGAR_EXCLUDE_FORMS = {
    "3", "3/A", "4", "4/A", "5", "5/A", "SC 13G", "SC 13G/A", "SCHEDULE 13G", "SCHEDULE 13G/A",
    "SC 13D", "SC 13D/A", "SCHEDULE 13D", "SCHEDULE 13D/A", "13F-HR", "13F-HR/A", "13F-NT",
    "UPLOAD", "CORRESP", "CERT", "D", "D/A", "SD",
}
# SEC asks for a descriptive User-Agent with a contact address on every automated request.
SEC_USER_AGENT = "KQC Quantum Inc. investor-relations site ir@kqcquantum.com"
BROWSER_USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/130.0.0.0 Safari/537.36")

# Press releases. KQC distributes through Business Wire, which answers scripted clients with HTTP 403, so the
# feed of record is Nasdaq's per-symbol RSS (Business Wire delivers every release tagged with a ticker to it).
# Tickers to watch: Charlton Aria now; add "KQC" once the combined company trades. Tickers found on EDGAR for the
# tracked registrants are added automatically (data/releases.json "tickers").
NASDAQ_TICKERS = ["CHAR"]
NASDAQ_RSS = "https://www.nasdaq.com/feed/rssoutbound?symbol={symbol}"
# Business Wire newsroom search, tried as well (best effort): every release whose full text mentions KQC Quantum.
BW_SEARCH_URL = "https://www.businesswire.com/newsroom?keywords=ENTIRE_RELEASE%3Atrue%3AKQC+Quantum"
# Only releases issued by or about KQC are kept (the SPAC's own releases and other companies' mentions are not).
RELEASE_HEADLINE_MUST_CONTAIN = ("KQC",)
# A release recorded without its text (or without the Business Wire link) is retried on later runs for this long.
RETRY_DAYS = 14
BW_RELEASE_RE = re.compile(r'href="(?:https://www\.businesswire\.com)?(/news/home/(\d{14})/en/[^"#?]*)"')

# Labels for Form 8-K items (Regulation S-K / Form 8-K instructions), used in generated descriptions.
ITEM_LABELS = {
    "1.01": "entry into a material definitive agreement", "1.02": "termination of a material definitive agreement",
    "1.03": "bankruptcy or receivership", "2.01": "completion of acquisition or disposition of assets",
    "2.02": "results of operations and financial condition", "2.03": "creation of a direct financial obligation",
    "2.04": "triggering events that accelerate a financial obligation", "2.05": "costs associated with exit or disposal activities",
    "2.06": "material impairments", "3.01": "notice of delisting or failure to satisfy a listing standard",
    "3.02": "unregistered sales of equity securities", "3.03": "material modification to rights of security holders",
    "4.01": "changes in the registrant's certifying accountant", "4.02": "non-reliance on previously issued financial statements",
    "5.01": "changes in control of the registrant", "5.02": "departure or appointment of directors or officers",
    "5.03": "amendments to the articles of incorporation or bylaws", "5.05": "amendments to the code of ethics",
    "5.06": "change in shell company status", "5.07": "submission of matters to a vote of security holders",
    "5.08": "shareholder director nominations", "7.01": "Regulation FD disclosure", "8.01": "other events",
    "9.01": "financial statements and exhibits",
}
FORM_LABELS = {
    "425": "Communication regarding the proposed business combination (Rule 425)",
    "DEF 14A": "Definitive proxy statement", "DEFA14A": "Additional definitive proxy materials",
    "DEFM14A": "Definitive proxy statement relating to a merger or acquisition", "DEFR14A": "Revised definitive proxy statement",
    "PRE 14A": "Preliminary proxy statement", "PREM14A": "Preliminary proxy statement relating to a merger or acquisition",
    "PRER14A": "Revised preliminary proxy statement",
    "S-4": "Registration statement on Form S-4 (proxy statement/prospectus)", "S-4/A": "Amendment to the registration statement on Form S-4",
    "S-1": "Registration statement on Form S-1", "S-1/A": "Amendment to the registration statement on Form S-1",
    "F-4": "Registration statement on Form F-4", "F-4/A": "Amendment to the registration statement on Form F-4",
    "424B3": "Prospectus (Rule 424(b)(3))", "424B4": "Prospectus (Rule 424(b)(4))", "424B5": "Prospectus supplement (Rule 424(b)(5))",
    "EFFECT": "Notice of effectiveness", "10-K": "Annual report", "10-K/A": "Amendment to the annual report",
    "10-Q": "Quarterly report", "10-Q/A": "Amendment to the quarterly report", "20-F": "Annual report (foreign private issuer)",
    "6-K": "Report of foreign private issuer", "8-K": "Current report", "8-K/A": "Amendment to a current report",
    "NT 10-K": "Notification of late filing (annual report)", "NT 10-Q": "Notification of late filing (quarterly report)",
    "S-8": "Registration statement for employee benefit plan securities", "8-A12B": "Registration of securities on a national exchange",
    "25-NSE": "Notification of removal from listing", "15-12G": "Termination of registration", "CB": "Tender offer/rights offering notification",
}
KEEP_CAPS = {"kqc", "sec", "llc", "lp", "l.p.", "inc.", "ltd.", "co.", "ii", "iii", "iv", "ceo", "cfo", "coo", "ipo", "spac",
             "nasdaq", "nyse", "usd", "u.s.", "fd", "s-4", "f-4", "8-k", "10-k", "10-q", "edgar", "nrs", "d-wave", "posco", "ibk"}
MONTHS = ("january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december")

LOG = []


def log(msg):
    print(msg, flush=True)
    LOG.append(msg)


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def fetch(url, user_agent, accept="text/html,application/json;q=0.9,*/*;q=0.8", retries=3, timeout=40):
    last = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": user_agent, "Accept": accept, "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "identity", "Cache-Control": "no-cache",
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read()
                charset = r.headers.get_content_charset() or "utf-8"
                return raw.decode(charset, errors="replace")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError) as e:
            last = e
            code = getattr(e, "code", None)
            if code in (403, 404, 410):
                break
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GET {url} failed: {last}")


def fetch_json(url, user_agent):
    return json.loads(fetch(url, user_agent, accept="application/json"))


# ---------------------------------------------------------------------------
# Data files
# ---------------------------------------------------------------------------
def load_json(path, default):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def sentence_case(s):
    """EDGAR document descriptions are ALL CAPS; make them readable without losing acronyms and names."""
    s = html.unescape(s or "").strip()
    if not s:
        return s
    if sum(1 for c in s if c.isupper()) < 0.6 * max(1, sum(1 for c in s if c.isalpha())):
        return s  # already mixed case
    words = s.lower().split()
    out = []
    for i, w in enumerate(words):
        core = w.strip(",.;:()")
        if core in KEEP_CAPS:
            out.append(w.upper())
        elif core in MONTHS or i == 0:
            out.append(w[:1].upper() + w[1:])
        else:
            out.append(w)
    text = " ".join(out)
    text = re.sub(r"\bkqc\b", "KQC", text, flags=re.I)
    return text


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", " ", s or "")).replace("\xa0", " ")


def squash(s):
    return re.sub(r"\s+", " ", s or "").strip()


def iso_to_long(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1].title()} {int(d)}, {y}"


def slugify(s, maxwords=9):
    s = html.unescape(s).lower()
    s = re.sub(r"^kqc quantum,? inc\.? and charlton aria acquisition corp(oration)? announces?\s+", "", s)
    s = re.sub(r"^kqc quantum,? inc\.? announces?\s+", "", s)
    s = re.sub(r"[’'\"“”]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    words = [w for w in s.split("-") if w]
    return "-".join(words[:maxwords]) or "release"


# ---------------------------------------------------------------------------
# EDGAR
# ---------------------------------------------------------------------------
def edgar_discover(filings_doc):
    """Add CIKs for entities named in DISCOVER_ENTITIES once they exist on EDGAR."""
    known = dict(filings_doc.get("ciks", {}))
    for name, label in DISCOVER_ENTITIES.items():
        if any(v == label for v in known.values()) or any(v == label for v in EDGAR_CIKS.values()):
            continue
        try:
            url = "https://efts.sec.gov/LATEST/search-index?keysTyped=" + urllib.parse.quote(name)
            hits = fetch_json(url, SEC_USER_AGENT).get("hits", {}).get("hits", [])
        except Exception as e:
            log(f"  EDGAR entity search for '{name}' failed: {e}")
            continue
        for h in hits:
            entity = (h.get("_source", {}).get("entity") or "").lower()
            cik = str(h.get("_id") or "").zfill(10)
            if name in entity and cik.isdigit() and cik not in known and cik not in EDGAR_CIKS:
                known[cik] = label
                log(f"  EDGAR: new registrant found: {h['_source'].get('entity')} (CIK {cik})")
    filings_doc["ciks"] = known
    return {**EDGAR_CIKS, **known}


class _IndexTable(HTMLParser):
    """Rows of the Document Format Files table on an EDGAR filing index page."""

    def __init__(self):
        super().__init__()
        self.rows, self._row, self._cell, self._href, self._in_table = [], None, None, None, False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "table" and "tableFile" in (a.get("class") or ""):
            self._in_table = True
        elif self._in_table and tag == "tr":
            self._row = []
        elif self._row is not None and tag in ("td", "th"):
            self._cell, self._href = [], None
        elif self._cell is not None and tag == "a" and a.get("href"):
            self._href = a["href"]

    def handle_endtag(self, tag):
        if tag == "table" and self._in_table:
            self._in_table = False
        elif tag in ("td", "th") and self._cell is not None and self._row is not None:
            self._row.append((squash("".join(self._cell)), self._href))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._row:
                self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def edgar_doc_url(href):
    """Normalize EDGAR document links (inline-XBRL viewer links become plain document links)."""
    if href.startswith("/ix?doc="):
        href = href[len("/ix?doc="):]
    if href.startswith("/"):
        href = "https://www.sec.gov" + href
    return href


def edgar_filing_documents(cik, accession):
    """Primary document and exhibits of one filing, from its index page."""
    acc_nodash = accession.replace("-", "")
    base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc_nodash}/"
    page = fetch(base + f"{accession}-index.htm", SEC_USER_AGENT)
    p = _IndexTable()
    p.feed(page)
    docs = []
    for row in p.rows:
        if len(row) < 4 or row[0][0] in ("Seq", ""):
            continue
        desc, (name, href), typ = row[1][0], row[2], row[3][0]
        if not href or typ in ("GRAPHIC", "XML", "ZIP", "JSON", "EXCEL", "EX-101.INS", "EX-101.SCH", "EX-101.CAL",
                               "EX-101.DEF", "EX-101.LAB", "EX-101.PRE", "EX-104") or typ.startswith("EX-101"):
            continue
        docs.append({"type": typ, "desc": desc, "name": name.replace(" iXBRL", "").strip(), "href": edgar_doc_url(href)})
    return base, docs


def edgar_describe(form, items, report_date, exhibits, primary_name):
    form_u = form.upper()
    if form_u in ("8-K", "8-K/A"):
        labels = [ITEM_LABELS.get(i, f"Item {i}") for i in items if i != "9.01"]
        head = "Current report" if form_u == "8-K" else "Amendment to the current report"
        if "7.01" in items and exhibits and all(e["type"].startswith("EX-99") for e in exhibits) and len(labels) == 1:
            return f"{head} (Regulation FD): " + "; ".join(e["desc_clean"] for e in exhibits)
        return head + (": " + "; ".join(labels) if labels else "")
    if form_u == "425":
        if "8k" in (primary_name or "").lower():
            return "Communication regarding the proposed business combination (Rule 425): the Form 8-K and its exhibits"
        if exhibits:
            return "Communication regarding the proposed business combination (Rule 425): " + "; ".join(e["desc_clean"] for e in exhibits)
        return FORM_LABELS["425"]
    if form_u in ("10-Q", "10-Q/A") and report_date:
        return f"{FORM_LABELS[form_u]} for the quarter ended {iso_to_long(report_date)}"
    if form_u in ("10-K", "10-K/A", "20-F") and report_date:
        return f"{FORM_LABELS[form_u]} for the fiscal year ended {iso_to_long(report_date)}"
    return FORM_LABELS.get(form_u, sentence_case(form))


def poll_edgar(filings_doc, dry_run):
    ciks = edgar_discover(filings_doc)
    existing = {f["accession"] for f in filings_doc["filings"]}
    added = []
    for cik, label in ciks.items():
        try:
            sub = fetch_json(f"https://data.sec.gov/submissions/CIK{cik}.json", SEC_USER_AGENT)
        except Exception as e:
            log(f"  EDGAR submissions for CIK {cik} failed: {e}")
            continue
        tick = [t for t in (sub.get("tickers") or []) if t]
        if tick:
            filings_doc.setdefault("tickers", {})[cik] = tick[0]   # primary class only (CHARR/CHARU carry the same news)
        rec = sub.get("filings", {}).get("recent", {})
        n = len(rec.get("accessionNumber", []))
        rows = []
        for i in range(n):
            form = rec["form"][i]
            date = rec["filingDate"][i]
            acc = rec["accessionNumber"][i]
            if date < EDGAR_SINCE or form.upper() in EDGAR_EXCLUDE_FORMS or acc in existing:
                continue
            rows.append({
                "accession": acc, "cik": cik, "filer": label, "form": form, "date": date,
                "period": rec.get("reportDate", [""] * n)[i] or "",
                "items": [x.strip() for x in (rec.get("items", [""] * n)[i] or "").split(",") if x.strip()],
                "primary": rec.get("primaryDocument", [""] * n)[i] or "",
                "primary_desc": rec.get("primaryDocDescription", [""] * n)[i] or "",
            })
        log(f"  EDGAR {label} (CIK {cik}): {n} filings on record, {len(rows)} new since {EDGAR_SINCE}")
        for r in rows:
            try:
                base, docs = edgar_filing_documents(cik, r["accession"])
            except Exception as e:
                log(f"    index page for {r['accession']} failed ({e}); linking to the filing folder")
                base, docs = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{r['accession'].replace('-', '')}/", []
            primary = next((d for d in docs if d["name"] == r["primary"]), None) or (docs[0] if docs else None)
            exhibits = []
            for d in docs:
                if d["type"].upper().startswith("EX-"):
                    desc = sentence_case(d["desc"])
                    if len(d["desc"]) >= 80:
                        desc += "…"
                    exhibits.append({"type": d["type"], "desc": desc, "desc_clean": desc.rstrip("…"), "href": d["href"]})
            entry = {
                "accession": r["accession"], "cik": cik, "filer": label, "form": r["form"], "date": r["date"],
                "period": r["period"], "items": r["items"],
                "desc": edgar_describe(r["form"], r["items"], r["period"], exhibits, r["primary"]),
                "href": primary["href"] if primary else base + r["primary"] if r["primary"] else base,
                "index": base + f"{r['accession']}-index.htm",
                "exhibits": [{k: e[k] for k in ("type", "desc", "href")} for e in exhibits],
                "source": "edgar", "added": now_iso(),
            }
            added.append(entry)
            log(f"    + {r['form']} filed {r['date']}: {entry['desc'][:90]}")
            time.sleep(0.2)  # stay well inside SEC's 10 requests/second
    if added and not dry_run:
        filings_doc["filings"] = sorted(filings_doc["filings"] + added, key=lambda f: (f["date"], f["accession"]), reverse=True)
    return added


# ---------------------------------------------------------------------------
# Business Wire
# ---------------------------------------------------------------------------
def extract_element(page, attr, value, tag="div"):
    """Outer HTML of the first <tag ... attr="value"> element, found by counting nested tags of the same name."""
    m = re.search(r"<%s\b[^>]*\b%s=\"%s\"[^>]*>" % (tag, attr, re.escape(value)), page)
    if not m:
        return None
    start = m.start()
    depth = 0
    for t in re.finditer(r"<(/?)%s\b[^>]*?(/?)>" % tag, page[start:]):
        if t.group(2) == "/":
            continue
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return page[start:start + t.end()]
    return page[start:]


def inner_html(outer):
    if not outer:
        return ""
    return re.sub(r"^<[^>]+>", "", re.sub(r"</[^>]+>$", "", outer.strip()))


def top_level_blocks(fragment):
    """Split an HTML fragment into its top-level elements (tag, outer html)."""
    blocks, pos = [], 0
    tag_re = re.compile(r"<([a-zA-Z0-9]+)\b[^>]*>")
    while True:
        m = tag_re.search(fragment, pos)
        if not m:
            break
        tag = m.group(1).lower()
        if tag in ("br", "img", "hr", "input", "meta", "link"):
            pos = m.end()
            continue
        depth, end = 0, None
        for t in re.finditer(r"<(/?)%s\b[^>]*?(/?)>" % tag, fragment[m.start():]):
            if t.group(2) == "/":
                continue
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = m.start() + t.end()
                break
        if end is None:
            end = len(fragment)
        blocks.append((tag, fragment[m.start():end]))
        pos = end
    return blocks


def unwrap_smartlink(href):
    """Business Wire wraps outbound links in a click tracker; link to the destination instead."""
    try:
        u = urllib.parse.urlsplit(html.unescape(href))
        if u.netloc.endswith("businesswire.com") and u.path.startswith("/ct/CT"):
            q = urllib.parse.parse_qs(u.query)
            if q.get("url"):
                return q["url"][0]
    except Exception:
        pass
    return html.unescape(href)


def clean_inline(fragment):
    """Keep the inline markup the site uses (a, strong, em, br); drop everything else."""
    s = fragment
    s = re.sub(r"<(script|style)\b.*?</\1>", "", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "<br>", s, flags=re.I)

    def fix_a(m):
        attrs = m.group(1)
        hm = re.search(r'href="([^"]*)"', attrs)
        if not hm:
            return "<a>"   # anchor without a destination: keep the text only
        href = unwrap_smartlink(hm.group(1))
        if href.startswith("mailto:"):
            return f'<a href="{html.escape(href, quote=True)}">'
        if "nasdaq.com/" in href:
            return "<a>"   # ticker "entity token" links in the nasdaq.com copy: keep the text, drop the link
        return f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener noreferrer">'
    s = re.sub(r"<a\b([^>]*)>", fix_a, s, flags=re.I)
    s = re.sub(r"<a>(.*?)</a>", r"\1", s, flags=re.S)
    s = re.sub(r"<(/?)b\b[^>]*>", r"<\1strong>", s, flags=re.I)
    s = re.sub(r"<(/?)i\b[^>]*>", r"<\1em>", s, flags=re.I)
    s = re.sub(r"<(/?)(strong|em)\b[^>]*>", r"<\1\2>", s, flags=re.I)
    s = re.sub(r"</?(?!a\b|/a\b|strong\b|/strong\b|em\b|/em\b|br\b|ul\b|/ul\b|ol\b|/ol\b|li\b|/li\b)[a-zA-Z0-9]+\b[^>]*>", "", s)
    s = re.sub(r"<(ul|ol|li)\b[^>]*>", r"<\1>", s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"[ \t\r\n]+", " ", s).strip()
    s = re.sub(r"\s*<br>\s*", "<br>", s)
    s = re.sub(r"(<br>){2,}", "<br>", s)
    s = re.sub(r"^(<br>)+|(<br>)+$", "", s)
    s = re.sub(r"<(strong|em)>\s*</\1>", "", s)
    return s.strip()


def is_heading(cleaned):
    """A paragraph that is entirely bold (or bold-italic) is a section heading in Business Wire markup."""
    inner = re.sub(r"^<strong>(.*)</strong>$", r"\1", cleaned, flags=re.S)
    if inner == cleaned:
        return False
    return "<strong>" not in inner and len(strip_tags(inner)) < 160


def story_blocks_to_body(blocks):
    """Turn the flat list of (tag, outer html) blocks of a wire-service release into the site's body fragments:
    plain paragraphs, "<strong>Heading</strong>" lines and "<ul>…</ul>" lists. The dateline of the first paragraph
    ("CITY--(BUSINESS WIRE)--") is removed and returned as the location. Returns (body, location, leftovers) where
    leftovers are the raw paragraph fragments that follow a "View source version" line (syndicated copies put the
    contacts there)."""
    body, location, leftovers = [], "", []
    first_text_done, after_source = False, False
    for tag, outer in blocks:
        if tag in ("style", "script"):
            continue
        inner = inner_html(outer)
        if after_source:
            if tag == "p":
                leftovers.append(inner)
            continue
        if tag in ("ul", "ol"):
            items = [clean_inline(inner_html(o)) for t, o in top_level_blocks(inner) if t == "li"]
            items = [i for i in items if strip_tags(i).strip()]
            if items:
                body.append(f"<{tag}>" + "".join(f"<li>{i}</li>" for i in items) + f"</{tag}>")
            continue
        if tag in ("h2", "h3", "h4"):
            txt = squash(strip_tags(inner))
            if txt:
                body.append(f"<strong>{html.escape(txt)}</strong>")
            continue
        cleaned = clean_inline(inner)
        text = strip_tags(cleaned).strip()
        if not text:
            continue
        if text.startswith("View source version on businesswire.com"):
            after_source = True
            continue
        if not first_text_done:
            m = re.match(r"^(.+?)--\s*\(\s*(?:<[^>]+>\s*)*BUSINESS WIRE\s*(?:<[^>]+>\s*)*\)\s*--\s*", cleaned, flags=re.S)
            if m:
                loc = squash(strip_tags(m.group(1)))
                location = " ".join(w[:1] + w[1:].lower() if w.isupper() and len(w) > 2 else w for w in loc.split())
                cleaned = cleaned[m.end():].strip()
                cleaned = re.sub(r"^(</(?:strong|em|a)>\s*)+", "", cleaned).strip()
                first_text_done = True
            elif len(text) > 200 or body:
                first_text_done = True   # no dateline on this copy; stop looking after the first real paragraph
        if is_heading(cleaned) and "<a " not in cleaned:
            cleaned = "<strong>" + squash(strip_tags(cleaned)) + "</strong>"
        body.append(cleaned)
    return body, location, leftovers


def contacts_to_fragments(paragraph_fragments):
    """Contact blocks (one paragraph each, lines separated by <br>) in the format tools/content.py uses."""
    out = []
    for frag in paragraph_fragments:
        c = clean_inline(frag)
        c = re.sub(r"</?(?:strong|em)>", "", c)
        c = re.sub(r"\s*<br>\s*", "<br>", c).strip()
        text = strip_tags(c).strip()
        if not text or text.lower().startswith(("source:", "view source")):
            continue
        out.append(f'<span class="mono" style="font-size:.9rem">{c}</span>')
    return out


def finish_release(headline, date_iso, time_et, sub, body, location, contacts):
    if contacts:
        body = body + ["<strong>Contacts</strong>"] + contacts
    # Excerpt shown in news lists: the company's own subheadline when there is one, else the opening paragraph.
    excerpt = sub
    if not excerpt:
        for b in body:
            if (b.startswith("<strong>") and b.endswith("</strong>")) or b.startswith("<ul") or b.startswith("<ol"):
                continue
            txt = squash(strip_tags(b))
            if len(txt) > 60:
                excerpt = txt
                break
    if len(excerpt) > 320:
        cut = excerpt[:320]
        end = max(cut.rfind(". "), cut.rfind("; "))
        excerpt = cut[:end + 1].strip() if end >= 120 else cut.rsplit(" ", 1)[0].rstrip(",;:") + "…"
    ok = bool(headline) and len([b for b in body if not b.startswith("<strong>")]) >= 3 and bool(contacts or any("About" in b for b in body))
    return {
        "headline": headline, "date": date_iso, "time_et": time_et, "sub": sub, "location": location or "Wilmington, Del. & Busan, South Korea",
        "excerpt": excerpt or sub or headline, "body": body if ok else None, "parsed": ok,
    }


def eastern(d):
    """(YYYY-MM-DD, 'H:MM AM ET') for an aware datetime."""
    d = d.astimezone(EASTERN)
    return d.date().isoformat(), d.strftime("%-I:%M %p ET") if os.name != "nt" else d.strftime("%I:%M %p ET")


def parse_release(page, url):
    """Headline, date, subhead, body fragments and contacts from a Business Wire release page."""
    ld = None
    for m in re.finditer(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', page, re.S):
        try:
            obj = json.loads(html.unescape(m.group(1)) if "&quot;" in m.group(1) else m.group(1))
        except Exception:
            continue
        objs = obj if isinstance(obj, list) else [obj]
        for o in objs:
            if isinstance(o, dict) and o.get("@type") in ("NewsArticle", "Article"):
                ld = o
                break
        if ld:
            break
    headline = squash(html.unescape((ld or {}).get("headline") or ""))
    if not headline:
        m = re.search(r"<h1\b[^>]*>(.*?)</h1>", page, re.S)
        headline = squash(strip_tags(m.group(1))) if m else ""
    if not headline:
        m = re.search(r'<meta property="og:title" content="([^"]*)"', page)
        headline = squash(html.unescape(m.group(1))) if m else ""

    published = (ld or {}).get("datePublished") or ""
    date_iso, time_et = "", ""
    if published:
        try:
            d = dt.datetime.fromisoformat(published.replace("Z", "+00:00"))
            if d.tzinfo is None:
                d = d.replace(tzinfo=dt.timezone.utc)
            date_iso, time_et = eastern(d)
        except Exception:
            pass
    if not date_iso:
        m = re.search(r"/news/home/(\d{4})(\d{2})(\d{2})\d{6}/", url)
        date_iso = f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else dt.date.today().isoformat()

    sub = squash(strip_tags(inner_html(extract_element(page, "id", "bw-release-subhead"))))

    story = extract_element(page, "id", "bw-release-story")
    body, location = [], ""
    if story:
        blocks = [b for b in top_level_blocks(inner_html(story)) if b[0] not in ("style", "script")]
        # the story is usually wrapped in one more div (or several)
        while len(blocks) == 1 and blocks[0][0] == "div":
            blocks = [b for b in top_level_blocks(inner_html(blocks[0][1])) if b[0] not in ("style", "script")]
        body, location, _ = story_blocks_to_body(blocks)

    contact_paras = []
    for m in re.finditer(r'id="(bw-release-contact-\d+)"', page):
        block = extract_element(page, "id", m.group(1))
        contact_paras += [inner_html(o) for t, o in top_level_blocks(inner_html(block or "")) if t == "p"]
    return finish_release(headline, date_iso, time_et, sub, body, location, contacts_to_fragments(contact_paras))


NASDAQ_DATE_RE = re.compile(r"Published</p>\s*<p>\s*([A-Z][a-z]{2} \d{1,2}, 20\d{2}) (\d{1,2}):(\d{2})\s*([ap]m)\s*E[DS]T", re.I)


def parse_release_nasdaq(page, url):
    """Same, from the syndicated copy on nasdaq.com (/press-release/…), which also names the Business Wire original.
    Returns the release dict plus 'bw_url'."""
    m = re.search(r"<h1\b[^>]*>(.*?)</h1>", page, re.S)
    headline = squash(strip_tags(m.group(1))) if m else ""
    if not headline:
        m = re.search(r"<title>(.*?)</title>", page, re.S)
        headline = squash(strip_tags(m.group(1))).replace(" | Nasdaq", "") if m else ""
    date_iso, time_et = "", ""
    m = NASDAQ_DATE_RE.search(page)
    if m:
        try:
            d = dt.datetime.strptime(f"{m.group(1)} {m.group(2)}:{m.group(3)} {m.group(4).upper()}", "%b %d, %Y %I:%M %p")
            date_iso, time_et = d.date().isoformat(), d.strftime("%-I:%M %p ET") if os.name != "nt" else d.strftime("%I:%M %p ET")
        except Exception:
            pass
    bw = re.search(r"https://www\.businesswire\.com/news/home/(\d{14})/en/[^\s\"'<]*", page)
    bw_url = html.unescape(bw.group(0)).rstrip("/") + "/" if bw else ""

    # the article body is the text block with the most paragraphs
    best, best_n = None, 0
    for m in re.finditer(r'<div class="nsdq-mercury-text-block">', page):
        block = extract_element(page[m.start():], "class", "nsdq-mercury-text-block")
        n = block.count("<p") if block else 0
        if n > best_n:
            best, best_n = block, n
    body, location, sub, contacts = [], "", "", []
    if best:
        blocks = [b for b in top_level_blocks(inner_html(best)) if b[0] not in ("style", "script")]
        while len(blocks) == 1 and blocks[0][0] == "div":
            blocks = [b for b in top_level_blocks(inner_html(blocks[0][1])) if b[0] not in ("style", "script")]
        # a short italic/plain paragraph before the dateline paragraph is the subheadline
        texts = [(t, squash(strip_tags(inner_html(o)))) for t, o in blocks]
        dateline_at = next((i for i, (t, x) in enumerate(texts) if "(BUSINESS WIRE)" in x.upper()), None)
        if dateline_at is not None:
            pre = [x for t, x in texts[:dateline_at] if x and t == "p"]
            if pre and len(pre[-1]) < 400:
                sub = pre[-1]
            blocks = blocks[dateline_at:]
        body, location, leftovers = story_blocks_to_body(blocks)
        contacts = contacts_to_fragments(leftovers)
    rel = finish_release(headline, date_iso, time_et, sub, body, location, contacts)
    rel["bw_url"] = bw_url
    return rel


def headline_key(h):
    return re.sub(r"[^a-z0-9]+", "", html.unescape(h or "").lower())[:120]


def is_company_release(headline):
    return any(k.lower() in (headline or "").lower() for k in RELEASE_HEADLINE_MUST_CONTAIN)


def discover_nasdaq(tickers):
    """Business Wire releases for each ticker from Nasdaq's per-symbol RSS feed (title, time, Nasdaq copy)."""
    import email.utils
    import xml.etree.ElementTree as ET
    found = []
    for t in tickers:
        url = NASDAQ_RSS.format(symbol=urllib.parse.quote(t))
        try:
            xml = fetch(url, BROWSER_USER_AGENT, accept="application/rss+xml,application/xml;q=0.9,*/*;q=0.8")
            root = ET.fromstring(xml.encode("utf-8") if isinstance(xml, str) else xml)
        except Exception as e:
            log(f"  Nasdaq feed for {t} failed: {e}")
            continue
        n = 0
        for item in root.iter("item"):
            title = squash(html.unescape(item.findtext("title") or ""))
            link = (item.findtext("link") or "").strip()
            pub = item.findtext("pubDate") or ""
            desc = squash(strip_tags(html.unescape(item.findtext("description") or "")))
            date_iso, time_et = "", ""
            try:
                date_iso, time_et = eastern(email.utils.parsedate_to_datetime(pub))
            except Exception:
                pass
            if title and link:
                found.append({"headline": title, "nasdaq_url": link, "date": date_iso, "time_et": time_et, "desc": desc, "via": f"Nasdaq RSS ({t})"})
                n += 1
        log(f"  Nasdaq feed for {t}: {n} releases listed")
    return found


def discover_businesswire():
    """Best effort: the Business Wire newsroom search (it answers some clients with HTTP 403)."""
    try:
        page = fetch(BW_SEARCH_URL, BROWSER_USER_AGENT)
    except Exception as e:
        log(f"  Business Wire search unavailable ({str(e)[-60:]}); relying on the Nasdaq feed")
        return []
    found = {}
    for m in BW_RELEASE_RE.finditer(page):
        found.setdefault(m.group(2), "https://www.businesswire.com" + html.unescape(m.group(1)))
    log(f"  Business Wire search: {len(found)} releases listed")
    return [{"bw_url": u, "bw_id": i, "headline": "", "via": "Business Wire search"} for i, u in found.items()]


def fetch_release_pages(cand):
    """Fill in the release text (and the Business Wire URL) from whichever copy answers: Business Wire first, then
    nasdaq.com. Returns (release dict or None, source label)."""
    if cand.get("bw_url"):
        try:
            rel = parse_release(fetch(cand["bw_url"], BROWSER_USER_AGENT), cand["bw_url"])
            if rel["headline"]:
                return rel, "Business Wire"
        except Exception as e:
            log(f"    Business Wire page unavailable ({str(e)[-50:]})")
    if cand.get("nasdaq_url"):
        try:
            rel = parse_release_nasdaq(fetch(cand["nasdaq_url"], BROWSER_USER_AGENT), cand["nasdaq_url"])
            if rel["headline"]:
                if rel.get("bw_url") and not cand.get("bw_url"):
                    cand["bw_url"] = rel["bw_url"]
                    cand["bw_id"] = re.search(r"/news/home/(\d{14})/", rel["bw_url"]).group(1)
                return rel, "Nasdaq"
        except Exception as e:
            log(f"    nasdaq.com page unavailable ({str(e)[-50:]})")
    return None, ""


def poll_releases(releases_doc, dry_run):
    """New press releases from the Nasdaq per-ticker feeds and (when reachable) the Business Wire search."""
    known_ids = {r["id"] for r in releases_doc["releases"]} | set(releases_doc.get("ignored", [])) | set(releases_doc.get("seeded_ids", []))
    known_heads = {headline_key(r["headline"]) for r in releases_doc["releases"]} | set(releases_doc.get("seeded_heads", []))
    known_nasdaq = {r.get("nasdaq_url") for r in releases_doc["releases"] if r.get("nasdaq_url")} | set(releases_doc.get("ignored", []))

    tickers = list(dict.fromkeys(NASDAQ_TICKERS + releases_doc.get("tickers", [])))
    candidates = discover_nasdaq(tickers) + discover_businesswire()

    added, ignored = [], []
    seen_now = set()
    for cand in candidates:
        key = cand.get("bw_id") or cand.get("nasdaq_url")
        if key in known_ids or key in known_nasdaq or key in seen_now:
            continue
        if cand.get("headline") and headline_key(cand["headline"]) in known_heads:
            continue
        if cand.get("headline") and not is_company_release(cand["headline"]):
            ignored.append(key)
            log(f"    skipped (not a KQC release): {cand['headline'][:70]}")
            continue
        seen_now.add(key)
        rel, src = fetch_release_pages(cand)
        headline = (rel or {}).get("headline") or cand.get("headline") or ""
        if not headline:
            log(f"    {key}: no copy of the release could be read; will retry next run")
            continue
        if not is_company_release(headline):
            ignored.append(key)
            log(f"    skipped (not a KQC release): {headline[:70]}")
            continue
        if headline_key(headline) in known_heads:
            continue
        date_iso = (rel or {}).get("date") or cand.get("date") or dt.date.today().isoformat()
        slug = slugify(headline) + "-" + date_iso[:4]
        taken = {r["slug"] for r in releases_doc["releases"]} | set(releases_doc.get("seeded_slugs", []))
        base, n = slug, 2
        while slug in taken:
            slug = f"{base}-{n}"
            n += 1
        bw_url = cand.get("bw_url") or ""
        entry = {
            "id": cand.get("bw_id") or ("nasdaq-" + re.sub(r"[^a-z0-9]+", "-", cand["nasdaq_url"].rsplit("/", 1)[-1].lower())[:80]),
            "slug": slug, "date": date_iso, "time_et": (rel or {}).get("time_et") or cand.get("time_et", ""),
            "headline": headline, "sub": (rel or {}).get("sub") or cand.get("desc", ""),
            "excerpt": (rel or {}).get("excerpt") or cand.get("desc") or headline,
            "location": (rel or {}).get("location") or "Wilmington, Del. & Busan, South Korea",
            "url": bw_url or cand.get("nasdaq_url", ""), "nasdaq_url": cand.get("nasdaq_url", ""),
            "source_name": "Business Wire" if bw_url else "Business Wire via Nasdaq",
            "body": (rel or {}).get("body"), "text_from": src if (rel or {}).get("body") else "",
            "added": now_iso(),
        }
        if entry["body"]:
            log(f"    + {date_iso} {headline[:70]} ({len(entry['body'])} paragraphs, text from {src})")
        else:
            log(f"    + {date_iso} {headline[:70]} (no readable copy yet: linking out, will retry the text)")
        added.append(entry)
        known_heads.add(headline_key(headline))
        time.sleep(0.5)

    # second chance for releases recorded without their text or without the Business Wire link
    upgraded = 0
    for r in releases_doc["releases"]:
        if r.get("body") and r.get("url", "").startswith("https://www.businesswire.com"):
            continue
        if r.get("added", "") < (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=RETRY_DAYS)).isoformat():
            continue
        cand = {"bw_url": r["url"] if r.get("url", "").startswith("https://www.businesswire.com") else "", "nasdaq_url": r.get("nasdaq_url", "")}
        rel, src = fetch_release_pages(cand)
        if not rel:
            continue
        if cand.get("bw_url") and not r.get("url", "").startswith("https://www.businesswire.com"):
            r["url"], r["source_name"], r["id"] = cand["bw_url"], "Business Wire", cand.get("bw_id", r["id"])
            upgraded += 1
        if rel.get("body") and not r.get("body"):
            r.update({"body": rel["body"], "sub": rel["sub"] or r.get("sub", ""), "excerpt": rel["excerpt"], "location": rel["location"],
                      "time_et": rel["time_et"] or r.get("time_et", ""), "text_from": src})
            upgraded += 1
            log(f"    text added for {r['headline'][:60]} (from {src})")
        time.sleep(0.5)

    if not dry_run:
        if added:
            releases_doc["releases"] = sorted(releases_doc["releases"] + added, key=lambda r: (r["date"], r["id"]), reverse=True)
        if ignored:
            releases_doc["ignored"] = sorted(set(releases_doc.get("ignored", [])) | set(ignored))
    return added, ignored, upgraded


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="fetch and report; change nothing")
    ap.add_argument("--no-build", action="store_true", help="update data/ but do not rebuild the site")
    ap.add_argument("--skip-edgar", action="store_true")
    ap.add_argument("--skip-releases", action="store_true", help="do not look for press releases")
    args = ap.parse_args()

    filings_doc = load_json(FILINGS_PATH, {"updated": "", "ciks": {}, "filings": []})
    releases_doc = load_json(RELEASES_PATH, {"updated": "", "releases": [], "ignored": []})
    # releases already written by hand into tools/content.py (PRESS) are never re-added
    try:
        sys.path.insert(0, HERE)
        import content as C  # noqa
        seeded = [re.search(r"/news/home/(\d{14})/", p.get("source_url", "") or "") for p in C.PRESS]
        releases_doc["seeded_ids"] = sorted({m.group(1) for m in seeded if m})
        releases_doc["seeded_slugs"] = sorted({p["slug"] for p in C.PRESS})
        releases_doc["seeded_heads"] = sorted({headline_key(p["headline"]) for p in C.PRESS})
    except Exception as e:
        log(f"  could not read tools/content.py ({e}); continuing without its release list")

    log(f"Disclosure poll {now_iso()}" + (" (dry run)" if args.dry_run else ""))
    new_filings = [] if args.skip_edgar else poll_edgar(filings_doc, args.dry_run)
    have = list(releases_doc.get("tickers", []))
    for t in (filings_doc.get("tickers") or {}).values():
        if t not in have and t not in NASDAQ_TICKERS:
            have.append(t)
            log(f"  EDGAR lists ticker {t}; its Nasdaq news feed is now watched")
    if have != list(releases_doc.get("tickers", [])):
        releases_doc["tickers"], releases_doc["_tickers_changed"] = have, True
    new_releases, ignored, upgraded = ([], [], 0) if args.skip_releases else poll_releases(releases_doc, args.dry_run)

    tickers_changed = releases_doc.pop("_tickers_changed", False)
    changed = bool(new_filings or new_releases or ignored or upgraded or tickers_changed)
    summary_parts = [f"{f['form']} ({iso_to_long(f['date'])})" for f in new_filings]
    summary_parts += [f"release: {r['headline'][:60]}" for r in new_releases]
    if upgraded and not summary_parts:
        summary_parts.append(f"release text added for {upgraded} item{'s' if upgraded != 1 else ''}")
    if ignored and not summary_parts:
        summary_parts.append(f"ignored {len(ignored)} non-KQC release{'s' if len(ignored) != 1 else ''}")
    summary = "; ".join(summary_parts) if summary_parts else "nothing new"

    if changed and not args.dry_run:
        filings_doc["updated"] = releases_doc["updated"] = now_iso()
        for k in ("seeded_ids", "seeded_slugs", "seeded_heads"):
            releases_doc.pop(k, None)
        save_json(FILINGS_PATH, filings_doc)
        save_json(RELEASES_PATH, releases_doc)
        log(f"  wrote data/filings.json ({len(filings_doc['filings'])} filings) and data/releases.json ({len(releases_doc['releases'])} releases)")
        if not args.no_build and (new_filings or new_releases or upgraded):
            subprocess.run([sys.executable, os.path.join(HERE, "build.py")], check=True, cwd=ROOT)
    elif args.dry_run and changed:
        log("  dry run: nothing written")

    log(f"Result: {summary}")
    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as f:
            f.write(f"changed={'true' if changed and not args.dry_run else 'false'}\n")
            f.write(f"publish={'true' if (new_filings or new_releases or upgraded) and not args.dry_run else 'false'}\n")
            f.write(f"summary={summary.replace(chr(10), ' ')[:400]}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())

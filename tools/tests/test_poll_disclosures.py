#!/usr/bin/env python3
"""Offline tests for tools/poll_disclosures.py (no network): run  python3 tools/tests/test_poll_disclosures.py"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import poll_disclosures as P  # noqa: E402

FIX = os.path.join(HERE, "fixtures")


def read(name):
    with open(os.path.join(FIX, name), encoding="utf-8") as f:
        return f.read()


class BusinessWireParsing(unittest.TestCase):
    def setUp(self):
        self.url = "https://www.businesswire.com/news/home/20261021973123/en/KQC-Quantum-Inc.-and-Charlton-Aria"
        self.rel = P.parse_release(read("bw_release.html"), self.url)

    def test_headline_and_date(self):
        self.assertTrue(self.rel["headline"].startswith("KQC Quantum, Inc. and Charlton Aria"))
        self.assertEqual(self.rel["date"], "2026-10-22")        # 20:10 UTC = 4:10 PM Eastern, same day
        self.assertEqual(self.rel["time_et"], "4:10 PM ET")
        self.assertEqual(self.rel["location"], "Wilmington, Del. & Busan, South Korea")

    def test_subhead_is_excerpt(self):
        self.assertEqual(self.rel["sub"], "Charlton Aria shareholder approvals effectively extend business combination deadline through up to October 25, 2027")
        self.assertEqual(self.rel["excerpt"], self.rel["sub"])

    def test_body_fragments(self):
        body = self.rel["body"]
        self.assertTrue(self.rel["parsed"])
        self.assertTrue(body[0].startswith("KQC Quantum, Inc. (“KQC Parent”)"), body[0][:80])
        self.assertNotIn("BUSINESS WIRE", body[0])
        self.assertIn("<strong>About KQC Quantum, Inc.</strong>", body)
        # tracker links are unwrapped to their destination and open in a new tab
        about = next(b for b in body if b.startswith("KQC Quantum, Inc. is the Delaware"))
        self.assertIn('<a href="http://www.kqcquantum.com" target="_blank" rel="noopener noreferrer">www.kqcquantum.com</a>', about)
        self.assertNotIn("cts.businesswire.com", "".join(body))
        # inline bold inside a paragraph is kept, class/style attributes are not
        info = next(b for b in body if b.startswith("In connection with the Business Combination"))
        self.assertIn("<strong>SHAREHOLDERS OF CHAR", info)
        self.assertNotIn("class=", info)
        self.assertIn("<em>Charlton Aria Acquisition Corporation, 221 W 9th St #848, Wilmington, DE 19801</em>", info)
        # bulleted list survives as one fragment
        ul = next(b for b in body if b.startswith("<ul>"))
        self.assertEqual(ul.count("<li>"), 3)
        self.assertTrue(ul.startswith("<ul><li>the risk that"))
        # a bold line with a link keeps the link
        full = next(b for b in body if "Full disclosure available at" in b)
        self.assertIn("<a href=", full)
        # contacts rendered the way tools/content.py writes them
        self.assertIn("<strong>Contacts</strong>", body)
        contacts = [b for b in body if b.startswith('<span class="mono"')]
        self.assertEqual(len(contacts), 3)
        self.assertEqual(contacts[0], '<span class="mono" style="font-size:.9rem">Charlton Aria Acquisition Corporation<br>Paul Strickland, Chief Financial Officer<br><a href="mailto:paul@charltonaria.com">paul@charltonaria.com</a></span>')
        self.assertEqual(body[-1], contacts[-1])
        # nothing empty, no stray tags
        for b in body:
            self.assertTrue(P.strip_tags(b).strip(), b)
            self.assertNotIn("<span>", b.replace('<span class="mono"', ""))

    def test_search_results_regex(self):
        ids = {m.group(2) for m in P.BW_RELEASE_RE.finditer(read("bw_release.html"))}
        self.assertEqual(ids, {"20261021973123", "20261008910978", "20261007549201"})

    def test_slug(self):
        self.assertEqual(P.slugify(self.rel["headline"]), "shareholder-approval-of-business-combination-deadline-extension")
        self.assertEqual(P.slugify("KQC Quantum, Inc. Announces Third Quarter 2027 Results"), "third-quarter-2027-results")

    def test_unparseable_page_falls_back_to_external(self):
        rel = P.parse_release("<html><head><title>x</title></head><body><h1>KQC Quantum Announces Something</h1></body></html>", self.url)
        self.assertEqual(rel["headline"], "KQC Quantum Announces Something")
        self.assertIsNone(rel["body"])
        self.assertFalse(rel["parsed"])
        self.assertEqual(rel["date"], "2026-10-21")  # from the URL when there is no JSON-LD


class NasdaqParsing(unittest.TestCase):
    def test_feed(self):
        saved = P.fetch
        try:
            P.fetch = lambda url, ua, **kw: read("nasdaq_rss.xml")
            found = P.discover_nasdaq(["CHAR"])
        finally:
            P.fetch = saved
        self.assertEqual(len(found), 3)
        self.assertEqual(found[0]["date"], "2026-10-22")          # 20:10 UTC -> Oct 22, 4:10 PM EDT
        self.assertEqual(found[0]["time_et"], "4:10 PM ET")
        self.assertTrue(found[0]["headline"].startswith("KQC Quantum, Inc. and Charlton Aria"))
        self.assertEqual(found[0]["nasdaq_url"], "https://www.nasdaq.com/press-release/kqc-quantum-inc-and-charlton-aria-acquisition-corporation-announce-shareholder")
        self.assertEqual(found[0]["desc"], "Shareholder approvals would extend the business combination deadline through up to October 25, 2027.")
        self.assertFalse(P.is_company_release(found[2]["headline"]))   # the SPAC's own release

    def test_release_page(self):
        rel = P.parse_release_nasdaq(read("nasdaq_release.html"), "https://www.nasdaq.com/press-release/x")
        self.assertTrue(rel["parsed"])
        self.assertEqual((rel["date"], rel["time_et"]), ("2026-10-22", "4:10 PM ET"))
        self.assertEqual(rel["bw_url"], "https://www.businesswire.com/news/home/20261021973123/en/")
        self.assertEqual(rel["sub"], "Charlton Aria shareholder approvals effectively extend business combination deadline through up to October 25, 2027")
        self.assertEqual(rel["location"], "Wilmington, Del. & Busan, South Korea")
        body = rel["body"]
        self.assertTrue(body[0].startswith("KQC Quantum, Inc. (“KQC Parent”)"))
        self.assertIn("(Nasdaq: CHAR)", body[0])                 # entity-token link unwrapped
        self.assertNotIn("nasdaq.com", "".join(body))
        self.assertNotIn("View source version", "".join(body))
        self.assertNotIn("Source: KQC", "".join(body))
        self.assertIn("<strong>About KQC Quantum, Inc.</strong>", body)
        self.assertIn('<a href="http://www.kqcquantum.com" target="_blank" rel="noopener noreferrer">www.kqcquantum.com</a>', "".join(body))
        contacts = [b for b in body if b.startswith('<span class="mono"')]
        self.assertEqual(len(contacts), 3)
        self.assertEqual(contacts[1], '<span class="mono" style="font-size:.9rem">KQC Investor Relations<br>Chris Mammone<br>Managing Director, The Blueshirt Group<br><a href="mailto:ir@kqcquantum.com">ir@kqcquantum.com</a></span>')
        self.assertEqual(body[body.index("<strong>Contacts</strong>") - 1][:35], "Forward-looking statements speak on")


class EdgarParsing(unittest.TestCase):
    def test_index_table(self):
        p = P._IndexTable()
        p.feed(read("edgar_index.htm"))
        rows = [r for r in p.rows if r[0][0] not in ("Seq", "")]
        self.assertEqual([r[3][0] for r in rows], ["8-K", "EX-3.1", "EX-10.1", "GRAPHIC", "XML", "EX-101.SCH"])
        self.assertEqual(rows[0][2][0], "ea0309338-8k425_charlton.htm iXBRL")
        self.assertEqual(P.edgar_doc_url(rows[0][2][1]), "https://www.sec.gov/Archives/edgar/data/2024459/000121390026111715/ea0309338-8k425_charlton.htm")

    def test_descriptions(self):
        ex = [{"type": "EX-3.1", "desc_clean": "Amendment to the articles"}, {"type": "EX-10.1", "desc_clean": "Amendment to the trust agreement"}]
        self.assertEqual(P.edgar_describe("8-K", ["1.01", "3.03", "5.03", "5.07", "8.01", "9.01"], "2026-10-19", ex, "ea0309338-8k425_charlton.htm"),
                         "Current report: entry into a material definitive agreement; material modification to rights of security holders; "
                         "amendments to the articles of incorporation or bylaws; submission of matters to a vote of security holders; other events")
        fd = [{"type": "EX-99.1", "desc_clean": "Investor presentation, dated October 2026"}, {"type": "EX-99.2", "desc_clean": "Script to investor presentation"}]
        self.assertEqual(P.edgar_describe("8-K", ["7.01", "9.01"], "2026-10-07", fd, "x.htm"),
                         "Current report (Regulation FD): Investor presentation, dated October 2026; Script to investor presentation")
        self.assertEqual(P.edgar_describe("425", [], "", fd, "ea0307998-8k425_charlton.htm"),
                         "Communication regarding the proposed business combination (Rule 425): the Form 8-K and its exhibits")
        self.assertEqual(P.edgar_describe("10-Q", [], "2026-09-30", [], "q.htm"), "Quarterly report for the quarter ended September 30, 2026")
        self.assertEqual(P.edgar_describe("S-4", [], "", [], "s4.htm"), "Registration statement on Form S-4 (proxy statement/prospectus)")
        self.assertEqual(P.edgar_describe("DEFA14A", [], "", [], "x.htm"), "Additional definitive proxy materials")

    def test_sentence_case(self):
        self.assertEqual(P.sentence_case("PRESS RELEASE DATED OCTOBER 7, 2026"), "Press release dated October 7, 2026")
        self.assertEqual(P.sentence_case("INVESTOR PRESENTATION, DATED OCTOBER 2026"), "Investor presentation, dated October 2026")
        self.assertEqual(P.sentence_case("BUSINESS COMBINATION AGREEMENT, DATED AS OF OCTOBER 6, 2026, BY AND AMONG THE COMPANY, PARENT, MERGER SUB, AND KQC KOREA"),
                         "Business combination agreement, dated as of October 6, 2026, by and among the company, parent, merger sub, and KQC korea")
        self.assertEqual(P.sentence_case("Already Mixed Case"), "Already Mixed Case")


class EndToEndWithMockedNetwork(unittest.TestCase):
    """Run the whole poll against canned responses: one new EDGAR filing, one new Business Wire release,
    one non-KQC search result. Checks the data files, the summary and GITHUB_OUTPUT."""

    SUBMISSIONS = {
        "name": "Charlton Aria Acquisition Corp", "filings": {"recent": {
            "accessionNumber": ["0001213900-26-999999", "0001213900-26-111715", "0000886982-26-000405", "0001213900-26-086235"],
            "filingDate": ["2026-11-14", "2026-10-22", "2026-08-11", "2026-08-06"],
            "reportDate": ["2026-09-30", "2026-10-19", "", "2026-06-30"],
            "form": ["10-Q", "8-K", "SCHEDULE 13G/A", "10-Q"],
            "primaryDocument": ["ea0399999-10q_charlton.htm", "ea0309338-8k425_charlton.htm", "primary_doc.xml", "ea0299152-10q_charlton.htm"],
            "primaryDocDescription": ["QUARTERLY REPORT", "CURRENT REPORT", "", "QUARTERLY REPORT"],
            "items": ["", "1.01,3.03,5.03,5.07,8.01,9.01", "", ""],
        }}}

    def fake_fetch(self, url, user_agent, **kw):
        self.calls.append(url)
        if "data.sec.gov/submissions/CIK0002024459.json" in url:
            return json.dumps(self.SUBMISSIONS)
        if "efts.sec.gov" in url and "keysTyped" in url:
            return json.dumps({"hits": {"hits": [{"_id": "2099999", "_source": {"entity": "KQC Quantum, Inc. (KQC)", "tickers": "KQC"}}]}})
        if "data.sec.gov/submissions/CIK0002099999.json" in url:
            return json.dumps({"filings": {"recent": {"accessionNumber": [], "filingDate": [], "reportDate": [], "form": [],
                                                       "primaryDocument": [], "primaryDocDescription": [], "items": []}}})
        if url.endswith("-index.htm"):
            return read("edgar_index.htm").replace("EX-3.1", "EX-31.1").replace("ea0309338-8k425_charlton.htm", "ea0399999-10q_charlton.htm")
        if "businesswire.com" in url:
            raise RuntimeError(f"GET {url} failed: HTTP Error 403: Forbidden")   # what Business Wire does to scripts
        if url == P.NASDAQ_RSS.format(symbol="CHAR"):
            new_item = ("<item><title>KQC Quantum, Inc. Announces Something New</title>"
                        "<link>https://www.nasdaq.com/press-release/kqc-quantum-inc-announces-something-new</link>"
                        "<pubDate>Tue, 01 Dec 2026 13:30:00 +0000</pubDate><description>Something new, in short.</description></item>")
            return read("nasdaq_rss.xml").replace("<item>", new_item + "<item>", 1)
        if "/press-release/kqc-quantum-inc-announces-something-new" in url:
            return read("nasdaq_release.html").replace("20261021973123", "20261201000002").replace(
                "KQC Quantum, Inc. and Charlton Aria Acquisition Corporation Announce Shareholder Approval of Business Combination Deadline Extension",
                "KQC Quantum, Inc. Announces Something New").replace("Oct 22, 2026 4:10pm EDT", "Dec 1, 2026 8:30am EST")
        raise AssertionError("unexpected URL " + url)

    def test_full_run(self):
        import shutil
        import tempfile
        self.calls = []
        tmp = tempfile.mkdtemp()
        repo_data = os.path.join(os.path.dirname(os.path.dirname(HERE)), "data")
        for n in ("filings.json", "releases.json"):
            shutil.copy(os.path.join(repo_data, n), os.path.join(tmp, n))
        saved = (P.fetch, P.FILINGS_PATH, P.RELEASES_PATH, P.time.sleep, sys.argv, os.environ.get("GITHUB_OUTPUT"))
        gh_out = os.path.join(tmp, "gh_output.txt")
        try:
            P.fetch, P.FILINGS_PATH, P.RELEASES_PATH, P.time.sleep = self.fake_fetch, os.path.join(tmp, "filings.json"), os.path.join(tmp, "releases.json"), lambda s: None
            sys.argv = ["poll_disclosures.py", "--no-build"]
            os.environ["GITHUB_OUTPUT"] = gh_out
            self.assertEqual(P.main(), 0)
            with open(P.FILINGS_PATH, encoding="utf-8") as f:
                filings = json.load(f)
            with open(P.RELEASES_PATH, encoding="utf-8") as f:
                releases = json.load(f)
            with open(gh_out, encoding="utf-8") as f:
                out = f.read()
        finally:
            P.fetch, P.FILINGS_PATH, P.RELEASES_PATH, P.time.sleep, sys.argv, prev = saved
            if prev is None:
                os.environ.pop("GITHUB_OUTPUT", None)
            else:
                os.environ["GITHUB_OUTPUT"] = prev
            shutil.rmtree(tmp, ignore_errors=True)
        # the 10-Q is new, the 8-K was already known, the 13G/A is excluded, the Aug 10-Q predates EDGAR_SINCE
        self.assertEqual(len(filings["filings"]), 9)
        new = filings["filings"][0]
        self.assertEqual((new["form"], new["date"], new["filer"]), ("10-Q", "2026-11-14", "Charlton Aria"))
        self.assertEqual(new["desc"], "Quarterly report for the quarter ended September 30, 2026")
        self.assertTrue(new["href"].endswith("/ea0399999-10q_charlton.htm"))
        self.assertEqual([e["type"] for e in new["exhibits"]], ["EX-31.1", "EX-10.1"])
        self.assertNotIn("source", {})
        # KQC Quantum Inc. was discovered on EDGAR and its (empty) filing list polled
        self.assertEqual(filings["ciks"], {"0002099999": "KQC Quantum Inc."})
        self.assertTrue(any("CIK0002099999.json" in c for c in self.calls))
        # releases: the known ones untouched, one new KQC release added from the Nasdaq feed (text and Business Wire
        # link taken from the nasdaq.com copy), the SPAC's own release ignored, Business Wire's 403 survived
        self.assertEqual(len(releases["releases"]), 2)
        new_rel = releases["releases"][0]
        self.assertEqual(new_rel["id"], "20261201000002")
        self.assertEqual(new_rel["url"], "https://www.businesswire.com/news/home/20261201000002/en/")
        self.assertEqual(new_rel["nasdaq_url"], "https://www.nasdaq.com/press-release/kqc-quantum-inc-announces-something-new")
        self.assertEqual((new_rel["date"], new_rel["time_et"]), ("2026-12-01", "8:30 AM ET"))
        self.assertEqual(new_rel["slug"], "something-new-2026")
        self.assertEqual(new_rel["source_name"], "Business Wire")
        self.assertEqual(new_rel["text_from"], "Nasdaq")
        self.assertTrue(new_rel["body"])
        self.assertEqual(releases["ignored"], ["https://www.nasdaq.com/press-release/charlton-aria-acquisition-corporation-announces-extension-deadline-initial-business"])
        self.assertEqual(releases.get("tickers", []), [])
        self.assertNotIn("seeded_ids", releases)
        self.assertNotIn("_tickers_changed", releases)
        fetched_pages = [c for c in self.calls if "/press-release/" in c]
        self.assertEqual(fetched_pages, ["https://www.nasdaq.com/press-release/kqc-quantum-inc-announces-something-new"],
                         "releases already on the site must not be fetched again")
        self.assertIn("changed=true", out)
        self.assertIn("summary=10-Q (November 14, 2026); release: KQC Quantum, Inc. Announces Something New", out)

    def test_retry_fills_in_text_later(self):
        """A release recorded while nasdaq.com was unavailable gets its text and Business Wire link on a later run."""
        import shutil
        import tempfile
        tmp = tempfile.mkdtemp()
        releases = {"updated": "", "tickers": [], "ignored": [], "releases": [{
            "id": "nasdaq-kqc-quantum-inc-announces-something-new", "slug": "something-new-2026", "date": "2026-12-01", "time_et": "",
            "headline": "KQC Quantum, Inc. Announces Something New", "sub": "Something new, in short.", "excerpt": "Something new, in short.",
            "location": "Wilmington, Del. & Busan, South Korea", "url": "https://www.nasdaq.com/press-release/kqc-quantum-inc-announces-something-new",
            "nasdaq_url": "https://www.nasdaq.com/press-release/kqc-quantum-inc-announces-something-new", "source_name": "Business Wire via Nasdaq",
            "body": None, "text_from": "", "added": P.now_iso()}]}
        with open(os.path.join(tmp, "releases.json"), "w", encoding="utf-8") as f:
            json.dump(releases, f)
        saved = (P.fetch, P.RELEASES_PATH, P.time.sleep)
        try:
            self.calls = []
            P.fetch, P.RELEASES_PATH, P.time.sleep = self.fake_fetch, os.path.join(tmp, "releases.json"), lambda s: None
            doc = P.load_json(P.RELEASES_PATH, {})
            # the other feed items are already on the site (hand-written in tools/content.py / data/releases.json)
            doc["seeded_ids"], doc["seeded_slugs"] = [], []
            doc["seeded_heads"] = [P.headline_key(h) for h in (
                "KQC Quantum, Inc. and Charlton Aria Acquisition Corporation Announce Shareholder Approval of Business Combination Deadline Extension",
                "KQC Quantum, Inc. and Charlton Aria Acquisition Corporation Announce Investor Webcast to Review Proposed Business Combination")]
            added, ignored, upgraded = P.poll_releases(doc, dry_run=False)
        finally:
            P.fetch, P.RELEASES_PATH, P.time.sleep = saved
            shutil.rmtree(tmp, ignore_errors=True)
        self.assertEqual(added, [])            # the feed item matches the recorded headline, so nothing is added twice
        self.assertEqual(upgraded, 2)          # text filled in, link upgraded to Business Wire
        r = doc["releases"][0]
        self.assertEqual(r["url"], "https://www.businesswire.com/news/home/20261201000002/en/")
        self.assertEqual(r["id"], "20261201000002")
        self.assertEqual(r["source_name"], "Business Wire")
        self.assertTrue(r["body"] and r["text_from"] == "Nasdaq")
        self.assertEqual(r["time_et"], "8:30 AM ET")


class DataMerge(unittest.TestCase):
    def test_content_loads_data_files(self):
        """tools/content.py must expose FILINGS and PRESS built from data/*.json."""
        sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
        import content as C
        self.assertTrue(any(f["form"] == "8-K" and f["date"] == "2026-10-22" for f in C.FILINGS))
        self.assertTrue(any(f["form"] == "S-4" and not f["href"] for f in C.FILINGS), "pending S-4 placeholder row")
        filed = [f["date"] for f in C.FILINGS if f["date"]]
        self.assertEqual(filed, sorted(filed, reverse=True))
        self.assertEqual(C.FILINGS[-1]["form"], "S-4", "pending rows come last")
        slugs = [p["slug"] for p in C.PRESS]
        self.assertEqual(len(slugs), len(set(slugs)))
        oct22 = next(p for p in C.PRESS if p["date"] == "2026-10-22")
        self.assertTrue(oct22.get("official"))
        self.assertIn("businesswire.com/news/home/20261021973123", oct22["source_url"])
        self.assertTrue(oct22["body"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

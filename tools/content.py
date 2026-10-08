# -*- coding: utf-8 -*-
"""
Single source of truth for everything editable on the KQC investor-relations site.

Edit this file, then run  python3 tools/build.py  from the repo root.
Bracketed values such as "[TICKER]" are placeholders pending company confirmation;
they render with a dashed underline so they are easy to spot in review.
"""

# ---------------------------------------------------------------------------
# Site mode
#   "ir"   : investor-relations site only (Blueshirt scope, Sep 29 2026). Home = Investor Relations;
#            Presentations / Filings / Webcasts / News pages; Contact; Disclosure. No corporate pages,
#            no partner logos, no ticker badge, no on-site press articles (news links to the source).
#   "full" : the complete corporate + IR build (kept for reference).
# ---------------------------------------------------------------------------
SITE_MODE = "ir"

# Search-engine indexing. False while the site is a public staging build (every page gets a noindex
# meta tag and robots.txt disallows crawling). Flip to True when kqcquantum.com goes live.
PUBLIC_INDEXING = False

# ---------------------------------------------------------------------------
# Company facts
# ---------------------------------------------------------------------------
COMPANY = {
    "legal_name": "KQC Quantum Inc.",                 # the public company this site represents (per Blueshirt Group / JP, Sep 29 2026)
    "short_name": "KQC",
    "opco_name": "Korea Quantum Computing Co., Ltd.",  # operating company in the Republic of Korea
    "korean_name": "한국퀀텀컴퓨팅㈜",                    # Korean name of the operating company
    "structure": "KQC Quantum Inc. is the Delaware parent company of Korea Quantum Computing Co., Ltd. (한국퀀텀컴퓨팅㈜), its operating company in the Republic of Korea, headquartered in Busan with an office in Seoul.",
    "tagline": "Quantum computing, post-quantum security and AI infrastructure, deployed for industry.",
    "founded": "December 28, 2021",
    "founded_year": "2021",
    "hq_city": "Busan, Republic of Korea",
    "employees": "27",
    "employees_asof": "as of 2025",
    "phds": "9",
    "site_url": "https://kqcquantum.com",           # canonical URL of THIS site (per Blueshirt Group, Sep 29 2026)
    "corporate_url": "https://www.kqchub.com/en/",
    "email_general": "support@kqchub.com",
    "email_press": "press@kqcquantum.com",            # media / press inquiries (per JP, Oct 7 2026)
    "email_ir": "ir@kqcquantum.com",                 # IR alias per Blueshirt Group; create the mailbox before launch
    "phone_busan": "+82-51-791-0825",
    "fax_busan": "+82-51-791-0826",
    "phone_seoul": "+82-2-6070-6700",
    "fax_seoul": "+82-2-6070-9751",
    "address_busan": "9F, Dongseo University Centum Campus, 55 Centumjungang-ro, Haeundae-gu, Busan 48058, Republic of Korea",
    "address_busan_l1": "9F, Dongseo University Centum Campus, 55 Centumjungang-ro",
    "address_busan_l2": "Haeundae-gu, Busan 48058, Republic of Korea",
    "address_seoul": "3F, 19 Eonju-ro 148-gil, Gangnam-gu, Seoul 06054, Republic of Korea",
    "address_seoul_l1": "3F, 19 Eonju-ro 148-gil",
    "address_seoul_l2": "Gangnam-gu, Seoul 06054, Republic of Korea",
    "copyright_year": "2026",
}

# Featured announcement on the Investors page (plus.ai/investors format, per Blueshirt Group).
# Fill in when the transaction is announced; the release_slug should point at the official release.
FEATURED = {
    "label": "Featured announcement",
    "headline": "KQC Quantum, Inc. and Charlton Aria Acquisition Corporation announce definitive business combination agreement",
    "date": "October 7, 2026",
    "body": (
        "KQC Quantum, Inc., the Delaware parent company of Korea Quantum Computing Co., Ltd., and Charlton Aria Acquisition "
        "Corporation (Nasdaq: CHAR) have entered into a definitive business combination agreement. On completion, shares of the "
        "combined company are expected to trade on The Nasdaq Stock Market under the ticker symbol \u201cKQC.\u201d The transaction "
        "values KQC at a pre-money equity value of approximately $80 million at $11.00 per share, with existing KQC shareholders "
        "rolling 100% of their equity into the combined company. Closing is expected in the first half of 2027, subject to "
        "Charlton Aria shareholder approval, an extension of Charlton Aria\u2019s business combination deadline and other customary conditions."
    ),
    "webcast_url": "https://www.netroadshow.com/nrs-login/guest-login#!/?show=bec1e37d",   # NetRoadshow event (does not allow framing; opens in a new tab)
    "presentation": "assets/docs/KQC-Investor-Presentation-October-2026.pdf",
    "transcript": "assets/docs/KQC-Announcement-Webcast-Transcript.pdf",   # webcast script / transcript PDF   # investor presentation PDF (button in the featured block)
    "release_slug": "business-combination-announcement-2026",   # on-site copy of the release in PRESS
    "release_external": "https://www.businesswire.com/news/home/20261007549201/en/KQC-Quantum-Inc.-and-Charlton-Aria-Acquisition-Corporation-Announce-Definitive-Business-Combination-Agreement-to-Take-Koreas-Enterprise-Quantum-Computing-and-Quantum-Safe-Security-Company-Public-on-Nasdaq",
}

# Investor Resources in IR mode: four boxes on the home page (Presentations, Filings, Webcasts, News),
# each linking to its own page. Items: status "live" | "pending"; href "" = pending.
RESOURCE_PAGES = [
    {"slug": "presentations", "title": "Presentations", "blurb": "Investor presentation and related materials.",
     "items": [
         {"title": "KQC Investor Presentation, October 2026", "kind": "PDF, 28 pages", "href": "assets/docs/KQC-Investor-Presentation-October-2026.pdf", "status": "live", "date": "October 8, 2026"},
     ]},
    {"slug": "filings", "title": "Filings", "blurb": "SEC filings, linked directly to EDGAR.", "items": []},
    {"slug": "webcasts", "title": "Webcasts", "blurb": "Business combination webcast.",
     "items": [
         {"title": "Business Combination Announcement Webcast", "kind": "Webcast on NetRoadshow", "href": "https://www.netroadshow.com/nrs-login/guest-login#!/?show=bec1e37d", "status": "live", "date": "October 8, 2026, 10:30 a.m. ET"},
         {"title": "Business Combination Announcement Webcast: Transcript", "kind": "PDF, 4 pages", "href": "assets/docs/KQC-Announcement-Webcast-Transcript.pdf", "status": "live", "date": "October 8, 2026"},
         {"title": "Press release: Investor Webcast to Review Proposed Business Combination", "kind": "Press release", "href": "press/investor-webcast-announcement-2026.html", "status": "live", "date": "October 8, 2026"},
     ]},
    {"slug": "news", "title": "News", "blurb": "Press releases and news coverage.", "items": None},
]

# Investor Resources list used by the full build. status: "live" | "pending"
RESOURCES = [
    {"title": "KQC Investor Presentation, October 2026", "kind": "PDF", "href": "assets/docs/KQC-Investor-Presentation-October-2026.pdf", "status": "live"},
    {"title": "Business Combination Press Release", "kind": "Press release", "href": "press/listing-announcement-template.html", "status": "pending"},
    {"title": "Business Combination Announcement Webcast", "kind": "Webcast", "href": "https://www.netroadshow.com/nrs-login/guest-login#!/?show=bec1e37d", "status": "live"},
    {"title": "Press Releases", "kind": "News", "href": "press.html", "status": "live"},
    {"title": "Latest SEC Filing, Form [8-K]", "kind": "SEC.gov", "href": "https://www.sec.gov/cgi-bin/browse-edgar?company=korea+quantum+computing&type=&dateb=&owner=include&count=40&action=getcompany", "status": "pending"},
    {"title": "Corporate Governance", "kind": "Board and policies", "href": "governance.html", "status": "live"},
]

# Listing / market data.  Everything here is a placeholder until the transaction is public.
LISTING = {
    "ticker": "KQC",                     # expected ticker of the combined company on Nasdaq (announced Oct 7 2026)
    "exchange": "The Nasdaq Stock Market",
    "exchange_short": "Nasdaq",
    "status_line": "Business combination pending",
    # Business-combination counterparty (public since the Oct 7 2026 announcement).
    "spac_name": "Charlton Aria Acquisition Corporation",
    "spac_ticker": "CHAR",
    "spac_exchange": "Nasdaq",
    "spac_url": "https://www.charltonaria.com/",
    "issuer": "KQC Quantum Inc.",
    "incorporation": "Delaware",
    "cusip": "[CUSIP]",
    "isin": "[ISIN]",
    "fiscal_year_end": "[December 31]",
    "shares_outstanding": "[Pending]",
    "public_float": "[Pending]",
    "transfer_agent": "[Transfer agent]",
    "auditor": "Shinhan Accounting Corporation (RSM International network)",
    "counsel": "Baker McKenzie & KL Partners Joint Venture Law Firm",
    "cik": "[CIK]",                      # KQC Quantum Inc.'s own CIK, assigned when the S-4 is filed
    "edgar_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0002024459&type=&dateb=&owner=include&count=40",   # Charlton Aria (CHAR) until KQC has its own record
    "spac_cik": "0002024459",
}

# SEC filings shown on the Filings page. Until KQC Quantum Inc. is itself an SEC registrant, the transaction documents
# are filed by Charlton Aria Acquisition Corporation (CIK 0002024459). href "" = not yet filed.
EDGAR = "https://www.sec.gov/Archives/edgar/data/2024459/"
FILINGS = [
    {"form": "8-K", "filer": "Charlton Aria", "desc": "Current report: Business Combination Agreement, Sponsor Support Agreement, Parent Support Agreement and the joint press release (exhibits)",
     "date": "2026-10-07", "href": EDGAR + "000121390026107409/"},
    {"form": "425", "filer": "Charlton Aria", "desc": "Communication regarding the proposed business combination (press release)",
     "date": "2026-10-07", "href": EDGAR + "000121390026107415/"},
    {"form": "DEF 14A", "filer": "Charlton Aria", "desc": "Definitive proxy statement: extraordinary general meeting to extend the business combination deadline",
     "date": "2026-10-07", "href": EDGAR + "000121390026107429/"},
    {"form": "PRE 14A", "filer": "Charlton Aria", "desc": "Preliminary proxy statement: extension of the business combination deadline",
     "date": "2026-09-23", "href": EDGAR + "000121390026102408/"},
    {"form": "S-4", "filer": "KQC Quantum Inc.", "desc": "Registration statement, including the proxy statement of Charlton Aria and the prospectus of KQC",
     "date": "", "href": ""},
]
_UNUSED = {
}

# ---------------------------------------------------------------------------
# Leadership (source: kqchub.com/en/company/about, Sep 2026).  Bios marked
# "compiled" were assembled from public profiles / interviews and should be
# confirmed by the company before launch.
# ---------------------------------------------------------------------------
LEADERSHIP = [
    {
        "name": "Jay J. H. Kweon",
        "korean": "권지훈",
        "title": "Chairman",
        "slug": "jay-kweon",
        "board": "Chairman of the Board [to be confirmed]",
        "bio": [
            "Mr. Kweon co-founded Korea Quantum Computing in 2021 and serves as Chairman. His career spans capital markets, foreign-investment promotion and large-scale development in Korea, including roles as a financial analyst at AXA in New York, senior strategist at Hanwha Securities, head of sales and trading at ABN AMRO Korea, and head of corporate finance at Arthur D. Little Korea.",
            "From 2004 to 2007 he led the Foreign Investment Promotion Bureau of Busan Metropolitan City, and he later served as CEO and President of Centum Science Park Inc. and as Chairman of JK Partners &amp; Company. He holds a BA from Yonsei University and BS and MS degrees in Economics from Iowa State University.",
        ],
        "note": "Biography compiled from public profiles and press coverage; to be confirmed by the company.",
    },
    {
        "name": "John J. Y. Kim, Ph.D.",
        "korean": "김준영",
        "title": "Chief Executive Officer",
        "slug": "john-kim",
        "board": "Director &amp; CEO [to be confirmed]",
        "bio": [
            "Dr. Kim co-founded Korea Quantum Computing in 2021 and leads the company's strategy across quantum computing, post-quantum security and AI infrastructure. An economist by training (Ph.D., industrial organization), he previously advised SK Telecom through his own consulting practice, served as a research professor at the University of Southern California and worked at the SK Economic Research Institute on spectrum policy.",
            "He spent roughly five years in investment banking focused on M&amp;A, joint ventures and cross-border transactions, represented the Korea International Trade Association in China, and from 2014 served as master project manager on the Almaty International Airport project before founding KQC.",
        ],
        "note": "Biography compiled from published interviews (The Electronic Times, Dec 2025; Quantum Times, Jan 2026); to be confirmed by the company.",
    },
    {
        "name": "Stephen Oh, Ph.D.",
        "korean": "오상근",
        "title": "Vice President &amp; Chief Technology Officer",
        "slug": "stephen-oh",
        "bio": [
            "Dr. Oh leads KQC's technology organization, spanning quantum algorithm development and the company's post-quantum security hardware line, including the Crypto4A QxHSM™ platform, KQC QuHSM™ and KQC QuKey Bio. He is a public advocate of hardware-rooted post-quantum migration and has outlined KQC's four-stage PQC transition framework in industry media.",
            "[Full biography, education and prior roles to be provided by the company.]",
        ],
        "note": "Partial biography; to be completed by the company.",
    },
    {
        "name": "Seog Yil Yoon",
        "korean": "윤석일",
        "title": "Vice President &amp; Chief Commercial Officer",
        "slug": "seog-yil-yoon",
        "bio": ["[Biography to be provided by the company.]"],
        "note": "Placeholder.",
    },
    {
        "name": "Jaesun Jin",
        "korean": "진재선",
        "title": "Senior Director &amp; Chief Business Officer",
        "slug": "jaesun-jin",
        "bio": ["[Biography to be provided by the company.]"],
        "note": "Placeholder.",
    },
    {
        "name": "Changhoi Kim",
        "korean": "김창회",
        "title": "Executive Vice President, CRO-R",
        "slug": "changhoi-kim",
        "bio": ["[Biography to be provided by the company.]"],
        "note": "Placeholder.",
    },
    {
        "name": "Sehwan Han",
        "korean": "한세환",
        "title": "Executive Director &amp; Chief Financial Officer",
        "slug": "sehwan-han",
        "bio": ["[Biography to be provided by the company.]"],
        "note": "Placeholder.",
    },
]

# Board placeholders (independent directors are unknown; committee structure is a template).
BOARD_PLACEHOLDERS = [
    {"role": "Independent Director", "name": "[Name pending]", "committees": ["Audit (Chair)", "Nominating &amp; Governance"]},
    {"role": "Independent Director", "name": "[Name pending]", "committees": ["Compensation (Chair)", "Audit"]},
    {"role": "Independent Director", "name": "[Name pending]", "committees": ["Nominating &amp; Governance (Chair)", "Compensation"]},
]

# ---------------------------------------------------------------------------
# Milestones (official history from kqchub.com plus 2026 newsroom items)
# ---------------------------------------------------------------------------
TIMELINE = [
    {"year": "2026", "items": [
        {"date": "Jun 30", "title": "KQC Qubiteer launched", "text": "Quantum-AI hybrid optimization platform released."},
        {"date": "Jun 4", "title": "PQC proof of concept with LS ITC", "text": "Post-quantum authentication, secret management and certificate automation validated for industrial infrastructure."},
        {"date": "Apr 16", "title": "Excellent Technology Award", "text": "Recognized in the quantum computing category at the 12th Korea Excellent Enterprise Awards."},
        {"date": "Mar 12", "title": "ISO/IEC 27001 certified", "text": "First information-security certification in Korea's quantum computing industry, covering all business lines."},
    ]},
    {"year": "2025", "items": [
        {"date": "Dec 9", "title": "PQC proof of concept with IBK", "text": "NIST-standard post-quantum algorithms validated end-to-end on QxHSM with IBK Industrial Bank."},
        {"date": "Nov 19", "title": "MOU with Quantum AI", "text": "Proprietary LLM and multimodal services on KQC's GPUaaS platform."},
        {"date": "Nov 13", "title": "MOU with Primotera", "text": "Quantum-enabled drug discovery for autoimmune and fibrotic diseases."},
        {"date": "Oct 15", "title": "MOU with the Korean Society of Bioinformatics", "text": "Quantum computing for bioinformatics and life-science research."},
        {"date": "Jul 23", "title": "Strategic partnership with Crypto4A", "text": "Commercializing post-quantum cryptography hardware in Korea and Asia."},
        {"date": "Jul 10", "title": "MOU with KIOST", "text": "Quantum algorithms for predicting change in marine ecosystems."},
        {"date": "Jul 1", "title": "KQC AI GPU Farm launched", "text": "NVIDIA H200 GPU-as-a-Service co-located at Digital Edge SEL2."},
        {"date": "Jun 2", "title": "MOU with ITCEN Group", "text": "Business collaboration for the KQC GPUaaS business."},
        {"date": "Apr 30", "title": "National R&amp;D project on quantum advantage", "text": "Optimizing Busan urban-rail scheduling with quantum computing, jointly with Busan Transportation Corporation."},
        {"date": "Apr 21", "title": "R&amp;D engagement with POSCO Holdings", "text": "Feasibility study on quantum discovery of high-performance cathode materials."},
    ]},
    {"year": "2024", "items": [
        {"date": "Nov 5", "title": "Certified as a venture company", "text": ""},
        {"date": "Oct 28", "title": "MOU with POSCO Holdings", "text": "Quantum computing research in next-generation advanced materials."},
        {"date": "Aug 11", "title": "Joint research with Busan Transportation Corporation", "text": "Smart urban-rail innovation using quantum information technologies."},
        {"date": "May 23", "title": "Quantum access agreement with Qunova", "text": "Development of quantum solutions and FMO-VQE verification."},
        {"date": "Jan 29", "title": "Expanded collaboration with IBM", "text": "Plans for an IBM Quantum System Two in Busan by 2028 and IBM watsonx for KQC clients."},
        {"date": "Jan 24", "title": "MOU with BlockS", "text": "Quantum simulator development and quantum security commercialization."},
    ]},
    {"year": "2023", "items": [
        {"date": "Nov 20", "title": "MOU with IQM", "text": "Research collaboration and strategic business partnership."},
        {"date": "Oct 24", "title": "Hanlim Pharmaceutical joins KQC Quantum Membership", "text": "Quantum discovery of drug candidates for MASLD."},
        {"date": "Sep 20", "title": "MOU with Dankook University Hospital", "text": "Foundation for quantum-enabled healthcare research."},
        {"date": "Jun 15", "title": "MOU with KT and KT Cloud", "text": "Accelerating market adoption of quantum computing in Korea."},
        {"date": "Jan 2", "title": "KQC Quantum &amp; AI Research Institute established", "text": "Dedicated in-house research institute."},
    ]},
    {"year": "2022", "items": [
        {"date": "Nov 7", "title": "MOU with Busan Metropolitan City and ETRI", "text": "Tripartite collaboration to build Busan's quantum information ecosystem."},
        {"date": "Jul 11", "title": "KQC Quantum Computational Center opens", "text": "Korea's first commercialized quantum computing R&amp;D center, at Dongseo University Centum Campus."},
        {"date": "Apr 7", "title": "Joined the IBM Quantum Network as a hub", "text": "Launch of IBM Quantum access services and quantum R&amp;D initiatives."},
    ]},
    {"year": "2021", "items": [
        {"date": "Dec 28", "title": "Incorporation", "text": "Korea Quantum Computing Co., Ltd. is incorporated."},
    ]},
]

# ---------------------------------------------------------------------------
# Press releases and news.  type: "release" | "media" | "draft"
# Bodies are drafted from the cited public coverage; official company text
# should replace them before publication (each page carries that note).
# ---------------------------------------------------------------------------
BOILERPLATE = (
    "Korea Quantum Computing Co., Ltd. (KQC) is a Busan-headquartered quantum and AI infrastructure company "
    "founded in December 2021. KQC has operated as a hub of the IBM Quantum Network since 2022 and builds "
    "an integrated stack for industry: quantum computing access and algorithm development, post-quantum "
    "cryptography (PQC) security hardware including the Crypto4A QxHSM&trade;, KQC QuHSM&trade; and KQC QuKey Bio, "
    "and an NVIDIA H200-based AI GPU cloud (KQC GPUaaS). The company holds ISO/IEC 27001 certification and works "
    "with partners across finance, manufacturing, life sciences and the public sector. Learn more at "
    "<a href=\"https://www.kqchub.com/en/\" target=\"_blank\" rel=\"noopener noreferrer\">kqchub.com</a>."
)

PRESS = [
    {'slug': 'investor-webcast-announcement-2026', 'date': '2026-10-08', 'type': 'release', 'official': True, 'headline': 'KQC Quantum, Inc. and Charlton Aria Acquisition Corporation Announce Investor Webcast to Review Proposed Business Combination', 'sub': 'Investor webcast available October 8, 2026, at 10:30 a.m. Eastern Time', 'excerpt': 'An investor webcast reviewing the proposed business combination, with remarks from KQC Chairman Ji Hoon Kweon, KQC CEO Joon Young Kim and Charlton Aria CFO Paul Strickland, is available beginning October 8, 2026, at 10:30 a.m. Eastern Time.', 'location': 'Wilmington, Del. & Busan, South Korea', 'source_name': 'Business Wire', 'source_url': 'https://www.businesswire.com/news/home/20261008910978/en/KQC-Quantum-Inc.-and-Charlton-Aria-Acquisition-Corporation-Announce-Investor-Webcast-to-Review-Proposed-Business-Combination', 'tags': ['Webcast', 'Business Combination'], 'body': ['KQC Quantum, Inc. (“KQC Parent”), the Delaware parent company of Korea Quantum Computing Co., Ltd. (“KQC” or the “Company”), which helps enterprises adopt quantum computing and quantum-safe security, and Charlton Aria Acquisition Corporation (Nasdaq: CHAR) (“Charlton Aria”), a publicly traded special purpose acquisition company, today announced that an investor webcast reviewing their recently announced proposed business combination will be available beginning today, October 8, 2026, at 10:30 a.m. Eastern Time.', 'The webcast will feature remarks from Ji Hoon Kweon, Chairman of KQC; Joon Young Kim, Chief Executive Officer of KQC; and Paul Strickland, Chief Financial Officer of Charlton Aria. The presentation will cover KQC’s quantum computing and quantum-safe security offerings, customer projects, commercialization strategy and terms of the proposed business combination.', '<strong>Webcast Details</strong>', 'Date: October 8, 2026<br>Time: 10:30 a.m. Eastern Time / 7:30 a.m. Pacific Time<br>Access: <a href="https://www.netroadshow.com/nrs-login/guest-login#!/?show=bec1e37d" target="_blank" rel="noopener noreferrer">HERE</a>', 'An on-demand replay of the webcast and the accompanying investor presentation will be available on the Investor Relations section of KQC’s website at <a href="../index.html">www.kqcquantum.com</a>.', 'As announced on October 7, 2026, KQC Parent and Charlton Aria entered into a definitive business combination agreement. Upon completion of the proposed transaction, Charlton Aria will become a wholly owned subsidiary of KQC Parent, with shares of common stock of the combined company expected to trade on Nasdaq under the ticker symbol “KQC.” The transaction is expected to close in the first half of 2027, subject to approval by Charlton Aria shareholders, an extension of Charlton Aria’s business combination deadline and other closing conditions.', '<strong>About KQC</strong>', 'KQC Quantum Inc. is the Delaware parent company of Korea Quantum Computing Co., Ltd., which was founded in 2021 and is headquartered in Busan, South Korea, with an office in Seoul. KQC helps enterprises put quantum computing and quantum-safe security to work. Its Qubiteer platform uses AI to turn business problems into models that can be solved with classical, quantum or hybrid methods; KQC provides access to multiple quantum technologies, including systems from D-Wave; and it supplies and integrates post-quantum cryptography products for financial, industrial and public-sector customers. For more information, visit www.kqcquantum.com.', '<strong>About Charlton Aria Acquisition Corporation</strong>', 'Charlton Aria Acquisition Corporation (Nasdaq: CHAR) is a blank check company incorporated in the Cayman Islands as an exempted company with limited liability for the purpose of effecting a merger, share exchange, asset acquisition, share purchase, recapitalization, reorganization or similar business combination with one or more businesses or entities.', '<strong>Important Information About the Proposed Transaction and Where to Find It</strong>', 'In connection with the Business Combination, KQC intends to file a registration statement on Form S-4 with the U.S. Securities and Exchange Commission (the “SEC”). The registration statement will include a proxy statement of CHAR and a prospectus of KQC. In connection with the Extension, CHAR intends to file a proxy statement with the SEC. After they have been filed and, where applicable, declared effective, the definitive proxy statements will be mailed to CHAR’s shareholders as of the applicable record dates. SHAREHOLDERS OF CHAR AND OTHER INTERESTED PERSONS ARE URGED TO READ THESE DOCUMENTS, ANY AMENDMENTS TO THEM AND ANY OTHER RELEVANT DOCUMENTS FILED WITH THE SEC CAREFULLY AND IN THEIR ENTIRETY WHEN THEY BECOME AVAILABLE, BECAUSE THEY WILL CONTAIN IMPORTANT INFORMATION ABOUT CHAR, KQC, THE BUSINESS COMBINATION AND THE EXTENSION. These documents, once available, can be obtained free of charge at the SEC’s website, or by request to Charlton Aria Acquisition Corporation, 221 W 9th St #848, Wilmington, DE 19801.', '<strong>No Offer or Solicitation</strong>', 'This communication is for informational purposes only. It does not constitute an offer to sell, or the solicitation of an offer to buy, any securities, or a solicitation of any vote or approval, in any jurisdiction. No securities shall be offered or sold in any jurisdiction in which such offer, solicitation or sale would be unlawful before registration or qualification under the securities laws of that jurisdiction. No offer of securities shall be made except by means of a prospectus meeting the requirements of Section 10 of the Securities Act of 1933, as amended. Full disclosure available at: www.kqcquantum.com.', '<strong>Participants in Solicitation</strong>', 'CHAR, KQC and their respective directors and executive officers may be deemed participants in the solicitation of proxies from CHAR’s shareholders in connection with the Business Combination and the Extension. Information about CHAR’s directors and executive officers and their interests in CHAR is set out in CHAR’s filings with the SEC. Additional information about the interests of those participants will be included in the proxy statement/prospectus and the Extension proxy statement when available.', '<strong>Forward-Looking Statements</strong>', 'This communication contains “forward-looking statements” within the meaning of the U.S. federal securities laws. These include statements about the proposed business combination (the “Business Combination”) between Charlton Aria Acquisition Corporation (“CHAR”) and KQC Quantum, Inc. (“KQC”), the expected timing of the Business Combination, the proposed extension of CHAR’s deadline to complete a business combination (the “Extension”), the anticipated benefits of the Business Combination, and KQC’s business strategy, products, customer projects, commercial milestones and future operations. Forward-looking statements can generally be identified by words such as “believe,” “expect,” “intend,” “plan,” “anticipate,” “may,” “will,” “should,” “could,” “would,” “potential,” “seek,” “target,” “aim” and similar expressions. These statements are based on current expectations and assumptions and are subject to risks and uncertainties, many of which are outside the parties’ control. Actual results may differ materially.', 'Factors that could cause actual results to differ include, among others:', '<ul><li>the risk that the Business Combination is not completed on time or at all;</li><li>failure to obtain the approval of CHAR’s shareholders for the Business Combination or the Extension;</li><li>the level of redemptions by CHAR’s public shareholders and the amount of cash available at closing;</li><li>failure to satisfy the minimum cash condition or any other closing condition;</li><li>failure to obtain or maintain the listing of the combined company’s securities on Nasdaq;</li><li>KQC’s ability to commercialize its products and convert pilots and proofs of concept into production deployments and recurring revenue;</li><li>the early stage of development of the quantum computing and post-quantum security markets;</li><li>competition, technological change and reliance on third-party hardware and partners;</li><li>regulatory matters in the Republic of Korea and the United States;</li><li>the costs of the Business Combination and of operating as a public company; and</li><li>the other risks to be described in the registration statement on Form S-4 and CHAR’s filings with the SEC.</li></ul>', 'Forward-looking statements speak only as of the date they are made. Except as required by law, neither CHAR nor KQC undertakes any obligation to update or revise them.', '<strong>Contacts</strong>', '<span class="mono" style="font-size:.9rem">Charlton Aria Acquisition Corporation<br>Paul Strickland, Chief Financial Officer<br><a href="mailto:paul@charltonaria.com">paul@charltonaria.com</a></span>', '<span class="mono" style="font-size:.9rem">KQC Investor Relations<br>Chris Mammone<br>Managing Director, The Blueshirt Group<br><a href="mailto:ir@kqcquantum.com">ir@kqcquantum.com</a></span>', '<span class="mono" style="font-size:.9rem">KQC Media Relations (U.S.)<br>Joon Young Kim, Chief Executive Officer<br>Jeehun Hwang, Senior Technical Advisor<br><a href="mailto:press@kqcquantum.com">press@kqcquantum.com</a></span>']},
    {
        "slug": "business-combination-announcement-2026",
        "date": "2026-10-07",
        "type": "release",
        "official": True,          # company press release, reproduced in full (Business Wire, Oct 7 2026, 8:30 AM ET)
        "featured": True,
        "headline": "KQC Quantum, Inc. and Charlton Aria Acquisition Corporation Announce Definitive Business Combination Agreement to Take Korea’s Enterprise Quantum Computing and Quantum-Safe Security Company Public on Nasdaq",
        "sub": "KQC helps enterprises put quantum computing and post-quantum cryptography to work through Qubiteer, its AI-driven hybrid quantum platform, access to multiple quantum technologies, and quantum-safe security products. Combined company, KQC Quantum, Inc., expected to list on Nasdaq; proceeds to fund product commercialization and the conversion of customer pilots into deployments.",
        "excerpt": "KQC Quantum, Inc. and Charlton Aria Acquisition Corporation (Nasdaq: CHAR) have entered into a definitive business combination agreement. The combined company is expected to trade on Nasdaq under the ticker symbol “KQC”; closing is expected in the first half of 2027.",
        "location": "Wilmington, Del. & Busan, South Korea",
        "source_name": "Business Wire",
        "source_url": "https://www.businesswire.com/news/home/20261007549201/en/KQC-Quantum-Inc.-and-Charlton-Aria-Acquisition-Corporation-Announce-Definitive-Business-Combination-Agreement-to-Take-Koreas-Enterprise-Quantum-Computing-and-Quantum-Safe-Security-Company-Public-on-Nasdaq",
        "tags": ["Business Combination", "Nasdaq"],
        "body": [
            "<strong>Transaction Highlights</strong>",
            "<ul>"
            "<li><strong>Enterprise quantum, built for adoption.</strong> KQC works in the layer between quantum hardware and industry: it defines customer problems, builds the models, runs them on the most suitable classical, quantum or hybrid resource, and integrates the results. Its Qubiteer platform, currently in development, uses AI to turn business problems into solvable models and to select the best-fit solver.</li>"
            "<li><strong>Hardware-agnostic by design.</strong> KQC provides access to third party quantum systems across superconducting, trapped-ion, neutral-atom, photonic and quantum annealing platforms, allowing it to match each workload to the most suitable technology as quantum hardware evolves.</li>"
            "<li><strong>Industrial and financial references.</strong> KQC has completed quantum computing projects with POSCO Holdings in battery materials and with Busan Transportation Corporation in urban rail scheduling, and paid post-quantum security proofs of concept with Industrial Bank of Korea (IBK) and LS ITC.</li>"
            "<li><strong>A second growth engine in quantum-safe security.</strong> Following the finalization of the first U.S. post-quantum cryptography standards in 2024, KQC supplies and integrates quantum-safe hardware security, authentication and key-management products for enterprises beginning their migration.</li>"
            "<li><strong>Transaction terms.</strong> The transaction values KQC at a pre-money equity value of $80 million, with KQC shareholders receiving shares of the combined company valued at $11.00 per share. Existing KQC shareholders will roll 100% of their equity into the combined company.</li>"
            "<li><strong>Capital.</strong> Charlton Aria’s trust account held approximately $93.5 million as of September 25, 2026. The cash available at closing will depend on redemptions by Charlton Aria shareholders.</li>"
            "<li><strong>Timing.</strong> The transaction is expected to close in the first half of 2027 subject to approval by Charlton Aria shareholders, an extension of Charlton Aria’s business combination deadline and other customary closing conditions.</li>"
            "</ul>",
            "KQC Quantum, Inc. (“KQC Parent”), the Delaware parent company of Korea Quantum Computing Co., Ltd. (“KQC” or the “Company”), which helps enterprises adopt quantum computing and quantum-safe security, and Charlton Aria Acquisition Corporation (Nasdaq: CHAR) (“Charlton Aria”), a publicly traded special purpose acquisition company, today announced that they have entered into a definitive business combination agreement (the “Business Combination Agreement”).",
            "Upon completion of the proposed transaction (the “Business Combination”), Charlton Aria will become a wholly owned subsidiary of KQC Parent, with shares of common stock of the combined company expected to trade on The Nasdaq Stock Market under the ticker symbol “KQC.”",
            "The Business Combination is expected to give KQC access to the U.S. public capital markets to fund its next stage of commercialization: engineering Qubiteer and its quantum-safe security platform into repeatable products, building the teams that turn customer pilots and proofs of concept into deployments, and completing product security certifications.",
            "<strong>Putting Quantum Technology to Work for Enterprises</strong>",
            "KQC was founded in Busan in 2021 on the view that enterprises adopt quantum technology not because of hardware milestones alone, but when a real business problem can be expressed in a form a computer can solve, run on the right resource, and delivered in a way that fits their systems and security requirements. KQC does not build quantum processors. It focuses on the work between hardware and industry — problem definition, mathematical modeling, solver selection, execution and integration — and on protecting enterprise systems as quantum computing advances.",
            "<em>Qubiteer: AI-driven hybrid quantum computing</em>",
            "Currently in development with a demo launched in June 2026, Qubiteer lets a user describe a business problem and its constraints. AI builds and checks the corresponding mathematical model, Qubiteer compares classical, quantum and hybrid solvers for the workload, and results are presented against the business objective. Because the platform selects the approach that fits each problem, customers can benefit from today’s classical and hybrid methods while gaining a path to quantum hardware as it improves. Initial application areas include industrial optimization and scheduling.",
            "<em>Quantum computing services and multi-vendor access</em>",
            "KQC provides applied research, modeling and quantum computing access to enterprise and research customers. As an example, it works with D-Wave’s quantum annealing systems through D-Wave’s Leap quantum cloud service. Since 2022, KQC has carried out projects across materials, transportation and pharmaceutical research, including the search for high-performance cathode materials for secondary batteries with POSCO Holdings, which combined quantum optimization with first-principles calculations, and train and crew scheduling optimization for Busan’s urban rail network with Busan Transportation Corporation under a national R&amp;D program supported by Korea’s Ministry of Science and ICT. KQC researchers have also co-authored peer-reviewed research applying quantum annealing to real-world data.",
            "<em>Quantum-safe security</em>",
            "Organizations need to replace the public-key cryptography that protects today’s systems before large-scale quantum computers can break it, and because sensitive data can be captured now and decrypted later, that transition has already begun. The U.S. National Institute of Standards and Technology finalized its first three post-quantum cryptography standards in August 2024. KQC helps enterprises plan and carry out this migration. Through partnerships, KQC supplies and integrates post-quantum hardware security modules and key and secrets management. It is also developing its own products for hardware-based authentication and embedded key protection, as well as QuantumSpan, a platform designed to help enterprises inventory their cryptographic assets and manage migration across their existing security infrastructure. KQC has completed paid post-quantum security proofs of concept with Industrial Bank of Korea (IBK) and LS ITC.",
            "<strong>Commercialization and Growth Strategy</strong>",
            "KQC grows through repeatable customer outcomes. In quantum computing, it starts with a defined customer problem, demonstrates value against a classical baseline, and then expands Qubiteer usage by reusing validated models across related workloads. In security, it starts with a priority system, validates compatibility in a paid pilot, deploys the selected products, and extends coverage and support over time, with QuantumSpan designed to turn migration projects into platform subscriptions.",
            "KQC operates in a market shaped by national policy: Korea has adopted a national quantum strategy and a dedicated law to promote quantum science, technology and industry. KQC is also building partner channels outside Korea, beginning in Southeast Asia with a memorandum of understanding with GEM announced in September 2026.",
            "Following completion of the Business Combination, KQC expects to use the proceeds for product engineering for Qubiteer, QuantumSpan and its security products; customer delivery and industry-solution teams; completing security certifications, including KCMVP; public-company readiness; and working capital and general corporate purposes.",
            "<strong>Management Commentary</strong>",
            "Ji Hoon Kweon, Chairman of KQC, said: “Today’s agreement is an important step for KQC. When we founded the company in 2021, we believed enterprises would adopt quantum technology not because of hardware milestones, but when someone could take a real business problem, connect it to the right computing and security tools, and deliver a result they could use. That is the work we have been doing with Korean industrial and financial customers, and Qubiteer and our security products are designed to make it repeatable. A Nasdaq listing gives us the capital and the visibility to bring this model to more customers, in Korea and beyond, and we are excited to continue accelerating customer adoption.”",
            "Jung Min Lee, Chairman and Chief Executive Officer of Charlton Aria, said: “We looked for a company with real customer engagements, products in the market and a clear use for public capital. KQC has built its business around what enterprises can use today: software that makes hybrid quantum computing practical, and security products for a migration that is already under way. We believe this transaction gives KQC the resources for its next stage of growth.”",
            "<strong>Transaction Overview</strong>",
            "The Business Combination Agreement has been approved by the boards of directors of KQC and Charlton Aria. Under the agreement, a newly formed Cayman Islands subsidiary of KQC Parent (“Merger Sub”) will merge with and into Charlton Aria, with Charlton Aria surviving as a wholly owned subsidiary of KQC Parent. Charlton Aria shareholders will receive one share of KQC common stock for each Class A ordinary share they hold, and holders of Charlton Aria rights will receive one-eighth of one share of KQC common stock for each right.",
            "The transaction values KQC at a pre-money equity value of approximately $80 million, at $11.00 per share. The transaction implies a pro forma equity value of approximately $215 million, based on the assumptions set out in the investor presentation.",
            "Charlton Aria’s trust account held approximately $93.5 million as of September 25, 2026. The cash available to the combined company at closing will depend on the level of redemptions by Charlton Aria shareholders, including in connection with the extension meeting described below. The Business Combination Agreement includes a minimum cash condition of $30 million.",
            "The cash available at closing is expected to be used for the purposes described above, to pay transaction expenses, and for working capital and general corporate purposes.",
            "Existing KQC shareholders will roll 100% of their equity into the combined company and are expected to own approximately 37% of the combined company at closing assuming no redemptions by Charlton Aria shareholders, and approximately 47% assuming a 50% redemption scenario.",
            "The Business Combination is expected to close during the first half of 2027, subject to approval by Charlton Aria shareholders, the registration statement on Form S-4 being declared effective by the U.S. Securities and Exchange Commission (“SEC”), approval of KQC’s common stock for listing on Nasdaq, satisfaction of the minimum cash condition, and other customary closing conditions.",
            "Charlton Aria must complete its initial business combination by October 25, 2026 unless its shareholders approve an extension. Charlton Aria intends to call an extraordinary general meeting of its shareholders to approve an extension of that date to allow time to complete the Business Combination. Details will be set out in a proxy statement to be filed with the SEC.",
            "Additional information about the proposed transaction, including a copy of the Business Combination Agreement, will be provided in Charlton Aria’s Current Report on Form 8-K to be filed with the SEC and available at <a href=\"https://www.sec.gov\" target=\"_blank\" rel=\"noopener noreferrer\">www.sec.gov</a>. KQC intends to file with the SEC a registration statement on Form S-4, which will include a proxy statement of Charlton Aria and a prospectus of KQC relating to the Business Combination.",
            "<strong>Advisors</strong>",
            "Baker McKenzie &amp; KL Partners Joint Venture Law Firm is serving as legal counsel to KQC. Shinhan Accounting Corporation, a member firm of the RSM International network, has been engaged as KQC’s independent auditor.",
            "Pillsbury Winthrop Shaw Pittman LLP is serving as legal counsel to Charlton Aria.",
            "Maples Group is serving as Cayman Islands counsel.",
            "<strong>About KQC</strong>",
            "KQC Quantum Inc. is the Delaware parent company of Korea Quantum Computing Co., Ltd. (“KQC”), which was founded in 2021 and is headquartered in Busan, South Korea, with an office in Seoul. KQC helps enterprises put quantum computing and quantum-safe security to work. Its Qubiteer platform uses AI to turn business problems into models that can be solved with classical, quantum or hybrid methods; KQC provides access to multiple quantum technologies, including systems from D-Wave; and it supplies and integrates post-quantum cryptography products for financial, industrial and public-sector customers. For more information, visit www.kqcquantum.com.",
            "<strong>About Charlton Aria Acquisition Corporation</strong>",
            "Charlton Aria Acquisition Corporation (Nasdaq: CHAR) is a blank check company incorporated in the Cayman Islands as an exempted company with limited liability for the purpose of effecting a merger, share exchange, asset acquisition, share purchase, recapitalization, reorganization or similar business combination with one or more businesses or entities.",
            "<strong>Important Information About the Proposed Transaction and Where to Find It</strong>",
            "In connection with the Business Combination, KQC intends to file a registration statement on Form S-4 with the U.S. Securities and Exchange Commission (the “SEC”). The registration statement will include a proxy statement of CHAR and a prospectus of KQC. In connection with the Extension, CHAR intends to file a proxy statement with the SEC. After they have been filed and, where applicable, declared effective, the definitive proxy statements will be mailed to CHAR’s shareholders as of the applicable record dates. SHAREHOLDERS OF CHAR AND OTHER INTERESTED PERSONS ARE URGED TO READ THESE DOCUMENTS, ANY AMENDMENTS TO THEM AND ANY OTHER RELEVANT DOCUMENTS FILED WITH THE SEC CAREFULLY AND IN THEIR ENTIRETY WHEN THEY BECOME AVAILABLE, BECAUSE THEY WILL CONTAIN IMPORTANT INFORMATION ABOUT CHAR, KQC, THE BUSINESS COMBINATION AND THE EXTENSION. These documents, once available, can be obtained free of charge at the SEC’s website, or by request to Charlton Aria Acquisition Corporation, 221 W 9th St #848, Wilmington, DE 19801.",
            "<strong>No Offer or Solicitation</strong>",
            "This communication is for informational purposes only. It does not constitute an offer to sell, or the solicitation of an offer to buy, any securities, or a solicitation of any vote or approval, in any jurisdiction. No securities shall be offered or sold in any jurisdiction in which such offer, solicitation or sale would be unlawful before registration or qualification under the securities laws of that jurisdiction. No offer of securities shall be made except by means of a prospectus meeting the requirements of Section 10 of the Securities Act of 1933, as amended. Full disclosure available at: www.kqcquantum.com.",
            "<strong>Participants in Solicitation</strong>",
            "CHAR, KQC and their respective directors and executive officers may be deemed participants in the solicitation of proxies from CHAR’s shareholders in connection with the Business Combination and the Extension. Information about CHAR’s directors and executive officers and their interests in CHAR is set out in CHAR’s filings with the SEC. Additional information about the interests of those participants will be included in the proxy statement/prospectus and the Extension proxy statement when available.",
            "<strong>Forward-Looking Statements</strong>",
            "This communication contains “forward-looking statements” within the meaning of the U.S. federal securities laws. These include statements about the proposed business combination (the “Business Combination”) between Charlton Aria Acquisition Corporation (“CHAR”) and KQC Quantum, Inc. (“KQC”), the expected timing of the Business Combination, the proposed extension of CHAR’s deadline to complete a business combination (the “Extension”), the anticipated benefits of the Business Combination, and KQC’s business strategy, products, customer projects, commercial milestones and future operations. Forward-looking statements can generally be identified by words such as “believe,” “expect,” “intend,” “plan,” “anticipate,” “may,” “will,” “should,” “could,” “would,” “potential,” “seek,” “target,” “aim” and similar expressions. These statements are based on current expectations and assumptions and are subject to risks and uncertainties, many of which are outside the parties’ control. Actual results may differ materially.",
            "Factors that could cause actual results to differ include, among others:",
            "<ul>"
            "<li>the risk that the Business Combination is not completed on time or at all;</li>"
            "<li>failure to obtain the approval of CHAR’s shareholders for the Business Combination or the Extension;</li>"
            "<li>the level of redemptions by CHAR’s public shareholders and the amount of cash available at closing;</li>"
            "<li>failure to satisfy the minimum cash condition or any other closing condition;</li>"
            "<li>failure to obtain or maintain the listing of the combined company’s securities on Nasdaq;</li>"
            "<li>KQC’s ability to commercialize its products and convert pilots and proofs of concept into production deployments and recurring revenue;</li>"
            "<li>the early stage of development of the quantum computing and post-quantum security markets;</li>"
            "<li>competition, technological change and reliance on third-party hardware and partners;</li>"
            "<li>regulatory matters in the Republic of Korea and the United States;</li>"
            "<li>the costs of the Business Combination and of operating as a public company; and</li>"
            "<li>the other risks to be described in the registration statement on Form S-4 and CHAR’s filings with the SEC.</li>"
            "</ul>",
            "Forward-looking statements speak only as of the date they are made. Except as required by law, neither CHAR nor KQC undertakes any obligation to update or revise them.",
            "<strong>Contacts</strong>",
            "<span class=\"mono\" style=\"font-size:.9rem\">Charlton Aria Acquisition Corporation<br>Paul Strickland, Chief Financial Officer<br><a href=\"mailto:paul@charltonaria.com\">paul@charltonaria.com</a></span>",
            "<span class=\"mono\" style=\"font-size:.9rem\">KQC Investor Relations<br>Chris Mammone<br>Managing Director, The Blueshirt Group<br><a href=\"mailto:ir@kqcquantum.com\">ir@kqcquantum.com</a></span>",
            "<span class=\"mono\" style=\"font-size:.9rem\">KQC Media Relations (U.S.)<br>Joon Young Kim, Chief Executive Officer<br>Jeehun Hwang, Senior Technical Advisor<br><a href=\"mailto:press@kqcquantum.com\">press@kqcquantum.com</a></span>",
        ],
    },
    {
        "slug": "qubiteer-launch-2026",
        "date": "2026-06-30",
        "type": "release",
        "featured": True,
        "headline": "KQC Launches KQC Qubiteer, a Quantum-AI Hybrid Optimization Platform",
        "sub": "Natural-language interface lets enterprises pose optimization problems without quantum expertise; an AI agent handles modeling, solver selection and execution.",
        "excerpt": "KQC announced the official launch of KQC Qubiteer, a quantum-AI hybrid platform that turns natural-language problem statements into executed quantum optimization workloads.",
        "location": "Busan, Republic of Korea",
        "source_name": "MoneyToday / The Electronic Times",
        "source_url": "https://www.etnews.com/20260630000013",
        "tags": ["Quantum Computing", "Product"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) today announced the official launch of <strong>KQC Qubiteer</strong>, a quantum-AI hybrid platform designed so that the people who own an optimization problem can use quantum methods on it themselves, without being quantum specialists.",
            "With Qubiteer, a user describes an optimization problem in natural language. An AI agent then performs the mathematical modeling that previously had to be done by hand, defining variables, objective functions and constraints, selects an appropriate solver and executes the computation. The platform analyzes the scale of the problem, the density of its constraints and the structure of its variables to recommend the most efficient solution method automatically.",
            "Qubiteer is built on a common architecture that is independent of any single industry. Initial target domains include manufacturing, logistics, finance and biotechnology, with applications such as materials design, production optimization, scheduling and portfolio optimization.",
            "“Qubiteer is a platform for extending quantum optimization beyond a small circle of experts to anyone with a real problem to solve,” said John J. Y. Kim, Ph.D., Chief Executive Officer of KQC. <em>(Translated from Korean-language coverage.)</em>",
            "The launch follows KQC's ISO/IEC 27001 certification in March 2026 and a series of post-quantum cryptography proofs of concept with financial and industrial partners, and it extends the company's strategy of delivering quantum, security and AI infrastructure as practical, enterprise-ready services.",
        ],
    },
    {
        "slug": "ls-itc-pqc-poc-2026",
        "date": "2026-06-04",
        "type": "release",
        "headline": "KQC and LS ITC Complete Post-Quantum Cryptography Proof of Concept for Industrial Infrastructure",
        "sub": "PQC-based authentication, centralized secret management and automated certificate lifecycle validated across LS Group systems.",
        "excerpt": "KQC and LS ITC, the IT services arm of LS Group, completed a proof of concept validating post-quantum cryptography across authentication, access and operational management systems.",
        "location": "Busan, Republic of Korea",
        "source_name": "MoneyToday / Boannews",
        "source_url": "https://www.mt.co.kr/industry/2026/06/04/2026060409530962952",
        "tags": ["Quantum Security", "Partnership"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) and LS ITC, the IT services subsidiary of LS Group, have completed a proof of concept (PoC) applying post-quantum cryptography (PQC) to industrial infrastructure. The engagement addressed two converging threats to operational technology: AI-agent-driven intrusion and the future ability of quantum computers to break today's public-key cryptography.",
            "The PoC validated PQC across three layers of LS Group's environment. For user authentication, PQC-based FIDO authentication keys strengthened login security while remaining safe against quantum attack. For server-to-server communication, a centralized secret-management architecture was tested for authentication and control across distributed industrial systems. For certificate management, the partners validated automated issuance and renewal of SSL/TLS certificates, a capability that becomes essential as certificate validity periods shorten.",
            "Both organizations confirmed meaningful results in operational applicability and efficiency. LS ITC said it would review implementation of the technology for key systems and pursue a sustainable security advantage for the quantum era.",
            "“This PoC demonstrated the industrial viability of PQC technology,” said John J. Y. Kim, Ph.D., Chief Executive Officer of KQC, adding that KQC would continue to support the transition to quantum-safe security across industry sectors. <em>(Translated from Korean-language coverage.)</em>",
        ],
    },
    {
        "slug": "digital-daily-pqc-native-interview-2026",
        "date": "2026-05-27",
        "type": "media",
        "headline": "In the News: KQC CTO Stephen Oh Says PQC-Native Hardware Is the Answer to the Post-Quantum Transition",
        "sub": "Digital Daily interview with KQC Vice President and CTO Stephen Oh, Ph.D.",
        "excerpt": "In an interview with Digital Daily, KQC Vice President and CTO Stephen Oh argued that only one to two years of practical preparation time remain before post-quantum cryptography becomes mandatory, and made the case for hardware architected for quantum resistance from the start.",
        "location": "Seoul, Republic of Korea",
        "source_name": "Digital Daily",
        "source_url": "https://www.ddaily.co.kr/page/view/2026052716082283402",
        "tags": ["Quantum Security", "Media"],
        "body": [
            "In a May 27, 2026 interview with Digital Daily, Stephen Oh, Ph.D., Vice President and Chief Technology Officer of Korea Quantum Computing Co., Ltd. (KQC), set out the company's view of the post-quantum timeline and its approach to securing critical systems.",
            "Dr. Oh argued that with regulators targeting mandatory post-quantum cryptography (PQC) adoption around 2030, organizations have only one to two years of practical preparation time. He noted that more than 99% of global digital infrastructure, from HTTPS and mobile networks to VPNs, digital signatures and blockchains, still depends on RSA and elliptic-curve algorithms that quantum computers are expected to break.",
            "Rather than layering PQC firmware onto legacy RSA-era equipment, Dr. Oh advocated “PQC-native” hardware that is architected for quantum resistance from the manufacturing stage, preventing key exposure through memory scraping or process-injection attacks that can compromise software-only approaches. He described a four-stage migration path: inventory of cryptographic assets, centralized key management, deployment of hardware-based security, and strong user authentication for HSM access.",
            "The interview highlighted KQC's product line, including the Crypto4A QxHSM&trade; post-quantum hardware security module and KQC QuKey Bio biometric authentication, and the company's proofs of concept with financial and industrial partners. The views summarized here are Dr. Oh's as reported; readers should consult the original article.",
        ],
    },
    {
        "slug": "excellent-technology-award-2026",
        "date": "2026-04-16",
        "type": "release",
        "headline": "KQC Receives the Excellent Technology Award at the 2026 Korea Excellent Enterprise Awards",
        "sub": "Recognized in the quantum computing category at the 12th annual awards organized by MoneyToday.",
        "excerpt": "KQC was named an Excellent Technology company in the quantum computing category at the 12th Korea Excellent Enterprise Awards, held April 16, 2026 at the Korea Press Center in Seoul.",
        "location": "Seoul, Republic of Korea",
        "source_name": "MoneyToday",
        "source_url": "https://www.mt.co.kr/industry/2026/04/16/2026041612523010217",
        "tags": ["Company", "Award"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) received the Excellent Technology Award in the quantum computing category at the 2026 Korea Excellent Enterprise Awards (대한민국 우수기업대상), the 12th edition of the awards organized by MoneyToday. The ceremony took place on April 16, 2026 at the Korea Press Center in Jung-gu, Seoul, where Chief Executive Officer John J. Y. Kim, Ph.D., accepted the award.",
            "The award recognizes KQC's work in quantum computing commercialization research and infrastructure operations. The company describes itself as a deep-tech firm advancing digital transformation across industries and building the security ecosystem of the future through quantum and related technologies.",
            "“As Korea's quantum computing service and research hub, we are advancing the practical application of quantum computing, quantum security and AI technologies,” the company said. <em>(Translated from Korean-language coverage.)</em>",
        ],
    },
    {
        "slug": "iso-27001-certification-2026",
        "date": "2026-03-13",
        "type": "release",
        "headline": "KQC Earns the First ISO/IEC 27001 Certification in Korea's Quantum Computing Industry",
        "sub": "Certification scope covers the company's entire operation: quantum algorithm development, PQC design, QxHSM key-management infrastructure and AI GPUaaS.",
        "excerpt": "KQC obtained ISO/IEC 27001 certification on March 12, 2026, the first in Korea's quantum computing industry, with a scope that spans all three of its business lines.",
        "location": "Busan, Republic of Korea",
        "source_name": "Quantum Times / Today Energy",
        "source_url": "https://www.todayenergy.kr/news/articleView.html?idxno=295122",
        "tags": ["Company", "Certification"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) announced that it obtained ISO/IEC 27001 certification on March 12, 2026, becoming the first company in Korea's quantum computing industry to achieve the international standard for information security management systems.",
            "ISO/IEC 27001 requires an organization to operate and continuously improve more than one hundred controls covering security policy, risk assessment, access control and cryptography. KQC placed its entire operation within the certification scope: quantum algorithm development, the design and implementation of post-quantum cryptography (PQC), the key-management infrastructure behind its QxHSM&trade; platform and its AI GPU-as-a-Service business. The company describes the approach as “security by design.”",
            "“We will continue to raise our security standards through regular internal audits and management reviews, and use this foundation of trust to expand our global technology partnerships,” said John J. Y. Kim, Ph.D., Chief Executive Officer of KQC. <em>(Translated from Korean-language coverage.)</em>",
            "The certification matters for KQC's customers in defense, finance and other regulated sectors, where high security standards are a precondition for adopting quantum technology. KQC also reiterated its plan to open a KQC Quantum Computing Center housing physical quantum computers in Busan's Centum district by 2030, and cited its participation in the U.S.-based Quantum Economic Development Consortium (QED-C).",
        ],
    },
    {
        "slug": "ibk-pqc-poc-2025",
        "date": "2025-12-09",
        "type": "release",
        "headline": "KQC Validates Post-Quantum Cryptography with IBK Industrial Bank in Successful Proof of Concept",
        "sub": "NIST-standard PQC algorithms tested end-to-end on the QxHSM™ platform in a banking environment.",
        "excerpt": "KQC and IBK Industrial Bank completed a proof of concept validating NIST-standard post-quantum cryptography, testing key generation, storage, signing and encapsulation on KQC's QxHSM platform.",
        "location": "Busan, Republic of Korea",
        "source_name": "The Electronic Times",
        "source_url": "https://www.etnews.com/20251209000100",
        "tags": ["Quantum Security", "Financial Services"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) and IBK Industrial Bank have successfully completed a proof of concept (PoC) for post-quantum cryptography (PQC) in a banking environment. The PoC was based on the quantum-resistant standard algorithms designated by the U.S. National Institute of Standards and Technology (NIST) and evaluated compatibility, security and computational performance.",
            "Using KQC's QxHSM&trade; quantum-resistant hardware security module, IBK tested the complete cryptographic workflow: key generation, storage, signing and encapsulation. The bank analyzed how the larger key, signature and certificate sizes introduced by PQC would affect the performance of live financial systems, confirming that a practical migration path exists.",
            "“This demonstrates our technological capability to respond proactively to the approaching quantum security threat,” said John J. Y. Kim, Ph.D., Chief Executive Officer of KQC, who added that KQC would support the build-out of Korea's quantum-security ecosystem as advanced economies move to mandate PQC adoption. <em>(Translated from Korean-language coverage.)</em>",
            "The companies aim to advance quantum-safe infrastructure across the Korean financial sector and, more broadly, across industry.",
        ],
    },
    {
        "slug": "quantum-ai-mou-2025",
        "date": "2025-11-20",
        "type": "release",
        "headline": "KQC and Quantum AI Sign MOU to Offer AI Services on KQC H200 Infrastructure",
        "sub": "Quantum AI's proprietary language models and multimodal engine to run on KQC's NVIDIA H200 GPUaaS infrastructure.",
        "excerpt": "KQC signed a memorandum of understanding with Quantum AI to combine KQC's H200 GPU-as-a-Service infrastructure with Quantum AI's proprietary LLMs and multimodal AI for regulated industries.",
        "location": "Seoul, Republic of Korea",
        "source_name": "The Electronic Times / VentureSquare",
        "source_url": "https://www.venturesquare.net/1015228",
        "tags": ["AI Infrastructure", "Partnership"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) and Quantum AI Inc. have signed a memorandum of understanding to develop differentiated, high-value AI services. The agreement was signed by John J. Y. Kim, Ph.D., Chief Executive Officer of KQC, and Choi Seong-jip, Chief Executive Officer of Quantum AI.",
            "Under the MOU, Quantum AI's proprietary language models, multimodal AI capabilities and its Data2Vec natural-language processing engine will be trained, optimized and served on KQC's GPU-as-a-Service platform, which is built on NVIDIA H200 GPUs. The partners will focus on model training and optimization and on real-time data processing for regulated industries such as finance, healthcare and law.",
            "Dr. Kim noted that KQC's infrastructure is optimized for compute-intensive workloads, including large language models and generative AI, while Mr. Choi said the partnership would allow both companies to present new innovations and help lead the future AI ecosystem. <em>(Translated from Korean-language coverage.)</em>",
            "Next steps include joint planning of new AI service models, deployment of advanced natural-language processing with accuracy superior to conventional robotic process automation, and faster delivery of customized high-performance services to customers.",
        ],
    },
    {
        "slug": "ksbi-bioinformatics-mou-2025",
        "date": "2025-10-15",
        "type": "release",
        "headline": "KQC Expands Quantum Computing into Life Sciences through Partnership with the Korean Society of Bioinformatics",
        "sub": "First academic-level cooperation in Korea to integrate quantum computing into bioinformatics research.",
        "excerpt": "KQC signed an MOU with the Korean Society of Bioinformatics (KSBI) at BIOINFO 2025 to apply quantum computing to drug development, genomic analysis and protein-structure prediction.",
        "location": "Suwon, Republic of Korea",
        "source_name": "ITDaily / EBN",
        "source_url": "https://www.ebn.co.kr/news/articleView.html?idxno=1682211",
        "tags": ["Quantum Computing", "Life Sciences"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) signed a memorandum of understanding with the Korean Society of Bioinformatics (KSBI) on October 14, 2025, during the BIOINFO 2025 conference at the Suwon Convention Center. The agreement was signed by KSBI President Ryu Seong-ho and KQC Chairman Jay J. H. Kweon.",
            "The partnership is the first academic-level cooperation in Korea to integrate quantum computing into bioinformatics research. It aims to apply quantum computational capacity to problems that remain intractable for classical methods, including drug development, genomic analysis and protein-structure prediction.",
            "Specifically, the MOU targets acceleration of large-scale molecular simulation and drug-protein interaction analysis by combining KQC's quantum algorithms with KSBI's priority initiatives in AI-driven and digital bioinformatics.",
            "The agreement builds on KQC's existing life-science collaborations, including quantum drug-discovery work with Hanlim Pharmaceutical and research partnerships with Dankook University Hospital, Baobab AiBio, PharmCAD and Quantum Intelligence.",
        ],
    },
    {
        "slug": "crypto4a-partnership-2025",
        "date": "2025-07-23",
        "type": "release",
        "headline": "KQC and Crypto4A Form Strategic Partnership to Commercialize Korea's First PQC-Based Security Solutions",
        "sub": "Partners to build a post-quantum HSM platform on Crypto4A's QxHSM™ and combine international PQC standards with Korea's KpqC algorithms.",
        "excerpt": "KQC and Canada's Crypto4A formed a strategic partnership to commercialize post-quantum cryptography security solutions in Korea, building a PQC-HSM platform on Crypto4A's QxHSM for finance, the public sector and industrial control.",
        "location": "Busan, Republic of Korea",
        "source_name": "ZDNet Korea / The Electronic Times",
        "source_url": "https://www.etnews.com/20250723000230",
        "tags": ["Quantum Security", "Partnership"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) and Crypto4A, a developer of quantum-safe hardware security solutions headquartered in Canada, have formed a strategic partnership to commercialize post-quantum cryptography (PQC) security solutions in Korea. The partnership brings together KQC Chairman Jay J. H. Kweon and Crypto4A Chief Executive Officer Bruno Couillard.",
            "The companies will develop technology that combines international-standard PQC algorithms with Korea's own quantum-resistant cryptography standard (KpqC), and will build a PQC hardware security module (PQC-HSM) platform based on Crypto4A's QxHSM&trade;. The partners describe it as Korea's first commercial PQC-HSM platform, targeting financial services, the public sector and industrial control systems.",
            "“We will secure leadership in PQC-HSM and quantum security solutions across Asia and lead the development of the technologies needed for the quantum computing era,” said Chairman Kweon. <em>(Condensed and translated from Korean-language coverage.)</em>",
            "The partnership set the foundation for KQC's quantum security business line, which has since delivered proofs of concept with IBK Industrial Bank and LS ITC and expanded into the KQC QuHSM&trade; and KQC QuKey Bio product family.",
        ],
    },
    {
        "slug": "kiost-marine-science-mou-2025",
        "date": "2025-07-10",
        "type": "release",
        "headline": "KQC and KIOST Sign MOU to Advance Quantum Computing Applications in Marine Science",
        "sub": "Quantum algorithms for marine numerical modeling and AI-based prediction of environmental and ecosystem change.",
        "excerpt": "KQC and the Korea Institute of Ocean Science and Technology signed an MOU at KIOST headquarters in Busan to develop quantum algorithms for predicting change in marine environments and ecosystems.",
        "location": "Busan, Republic of Korea",
        "source_name": "ZDNet Korea",
        "source_url": "https://zdnet.co.kr/view/?no=20250710160445",
        "tags": ["Quantum Computing", "Research"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) and the Korea Institute of Ocean Science and Technology (KIOST) signed a memorandum of understanding on July 10, 2025 at KIOST headquarters in Busan. The agreement was signed by KIOST President Lee Hee-seung and KQC Chairman Jay J. H. Kweon.",
            "The partnership focuses on applying quantum computing to marine research: developing quantum algorithms for marine numerical modeling and for AI-based prediction of environmental and ecosystem change, and planning applied research on ocean-pollution monitoring, climate-change response and marine-resource management.",
            "President Lee described the initiative as a pivotal opportunity to enhance the research capability needed to analyze and predict complex marine phenomena, including high-resolution long-term simulation and advanced pollution-dispersion forecasting. <em>(Translated from Korean-language coverage.)</em>",
            "The two organizations will collaborate on quantum-enhanced technologies that improve ocean prediction accuracy and on practical applications in marine environmental assessment and management.",
        ],
    },
    {
        "slug": "h200-gpu-farm-launch-2025",
        "date": "2025-07-03",
        "type": "release",
        "headline": "KQC Launches AI GPU Farm and GPU-as-a-Service Built on NVIDIA H200",
        "sub": "High-performance GPUaaS for LLM and multimodal workloads, co-located at Digital Edge's SEL2 data center.",
        "excerpt": "KQC officially launched its AI GPU Farm and GPU-as-a-Service offering built on NVIDIA H200 GPUs, delivering dedicated physical-server performance with pay-as-you-go pricing for big tech, AI startups, research institutes and HPC centers.",
        "location": "Busan, Republic of Korea",
        "source_name": "ZDNet Korea",
        "source_url": "https://zdnet.co.kr/view/?no=20250703101837",
        "tags": ["AI Infrastructure", "Product"],
        "body": [
            "Korea Quantum Computing Co., Ltd. (KQC) has officially launched the KQC AI GPU Farm and its GPU-as-a-Service (GPUaaS) offering, built on NVIDIA H200 GPUs based on the Hopper architecture and co-located at Digital Edge's SEL2 data center.",
            "The H200 SXM5 platform offers substantially more memory capacity and bandwidth than the previous-generation H100, with an embedded Transformer Engine for large-language-model training and inference. KQC's service provides dedicated physical-server-level performance, flexible resource allocation for LLM and multimodal AI applications, GPU virtualization for concurrent users, and integration with the NVIDIA AI Enterprise software stack. Customers can adjust compute, storage and network resources elastically under pay-as-you-go pricing.",
            "“Demand for the GPU Farm spans big tech, AI startups, compute-intensive industries, national research institutions and HPC centers,” said John J. Y. Kim, Ph.D., Chief Executive Officer of KQC. <em>(Translated from Korean-language coverage.)</em>",
            "The launch followed a June 2025 memorandum of understanding with ITCEN Group to expand deployment of the service. Over the longer term, KQC plans to integrate the GPU Farm with its quantum computing infrastructure to offer hybrid quantum-classical cloud services.",
        ],
    },
    {
        "slug": "ibm-watsonx-quantum-system-two-2024",
        "date": "2024-01-29",
        "type": "release",
        "headline": "Korea Quantum Computing and IBM Collaborate to Bring IBM watsonx and Quantum Computing to Korea",
        "sub": "KQC to deploy an IBM Quantum System Two in Busan by 2028 and offer IBM watsonx and AI infrastructure to its clients.",
        "excerpt": "IBM and KQC announced an expanded collaboration under which KQC plans to deploy an IBM Quantum System Two at its Busan facility by 2028 and provide IBM watsonx and AI infrastructure to clients across Korea.",
        "location": "Busan, Republic of Korea",
        "source_name": "IBM Newsroom / PR Newswire",
        "source_url": "https://newsroom.ibm.com/2024-01-29-Korea-Quantum-Computing-and-IBM-Collaborate-to-Bring-IBM-watsonx-and-Quantum-Computing-to-Korea",
        "tags": ["Quantum Computing", "IBM"],
        "body": [
            "IBM and Korea Quantum Computing Co., Ltd. (KQC) announced an expanded collaboration to bring IBM's AI and quantum computing capabilities to Korea. KQC, an IBM Quantum Innovation Center since 2022, plans to deploy an IBM Quantum System Two at its facility in Busan by 2028.",
            "As part of the collaboration, KQC clients gain access to IBM watsonx to train, tune and deploy enterprise AI models. KQC also plans to invest in AI infrastructure featuring advanced GPUs and IBM's Artificial Intelligence Unit (AIU), managed in a cloud-native environment on Red Hat OpenShift.",
            "“Our robust hardware computing resources and core software in quantum and AI are poised to catalyze industry utilization and ecosystem development,” said Ji Hoon (Jay) Kweon, Chairman of KQC. Dr. Joon Young (John) Kim, Chief Executive Officer of KQC, added that the company is actively building quantum research collaborations with leading Korean companies in the financial, bio-healthcare and pharmaceutical industries. Darío Gil, IBM Senior Vice President and Director of Research, said KQC clients would be able to train, fine-tune and deploy advanced AI models using IBM watsonx.",
            "KQC's existing research collaborations at the time included Dankook University Hospital, Hanlim Pharmaceutical and DNeuro, spanning quantum applications in healthcare, drug discovery and financial modeling.",
        ],
    },
    {
        "slug": "listing-announcement-template",
        "date": "2026-10-01",
        "type": "draft",
        "headline": "[DRAFT TEMPLATE] KQC Quantum Inc. Announces [Transaction] and Plans to Trade on [Exchange] under the Symbol “[TICKER]”",
        "sub": "[One-sentence summary of the transaction, valuation and expected timing.]",
        "excerpt": "[Template for the listing announcement. Hidden from the public site until the draft flag is removed in tools/content.py.]",
        "location": "[City], [Country]",
        "source_name": "Company release",
        "source_url": "",
        "tags": ["Investors", "Draft"],
        "body": [
            "KQC Quantum Inc. (“KQC” or the “Company”), the parent of Korea Quantum Computing Co., Ltd., today announced [description of the transaction: e.g., that it has entered into a definitive agreement with [Counterparty] / completed a [reverse merger / business combination / direct listing / initial public offering]]. Upon [closing / effectiveness], the combined company's [common stock] is expected to trade on [Exchange] under the ticker symbol “[TICKER]”.",
            "[Paragraph on strategic rationale: access to capital for the KQC Quantum Computing Center in Busan, expansion of the PQC hardware line and the H200 GPU cloud, and U.S. investor access to a Korean quantum infrastructure platform.]",
            "[Paragraph on transaction terms: valuation, consideration, expected proceeds, use of proceeds, expected timing, and conditions to closing including shareholder and regulatory approvals.]",
            "“[Quote from John J. Y. Kim, Ph.D., Chief Executive Officer.]”",
            "“[Quote from Jay J. H. Kweon, Chairman.]”",
            "[Advisors: [Financial advisor] is acting as financial advisor and [Law firm] as legal counsel to KQC. [Auditor] serves as the Company's independent registered public accounting firm.]",
            "<strong>Important information and where to find it.</strong> [Insert the required legend regarding the registration statement / proxy statement / prospectus, participants in the solicitation, and no-offer language, as advised by securities counsel.]",
        ],
    },
]

# Partner logos shown in the home-page carousel. This mirrors the partner wall KQC publishes on
# kqchub.com (same organizations, same order) plus IBM. Logo files live in
# assets/images/partners/<slug>.(svg|png); a partner without a file falls back to a text wordmark.
# To add one, drop in a logo file and append an entry here.
PARTNERS = [
    {"name": "IBM", "slug": "ibm", "domain": "ibm.com"},
    {"name": "Crypto4A", "slug": "crypto4a", "domain": "crypto4a.com"},
    {"name": "D-Wave", "slug": "d-wave", "domain": "dwavequantum.com"},
    {"name": "ITCEN Global", "slug": "itcen", "domain": "itcen.com"},
    {"name": "KIOST", "slug": "kiost", "domain": "kiost.ac.kr"},
    {"name": "Pusan National University", "slug": "pusan-national-university", "domain": "pusan.ac.kr"},
    {"name": "Sunchon National University", "slug": "sunchon-national-university", "domain": "scnu.ac.kr"},
    {"name": "Hanlim Pharm", "slug": "hanlim", "domain": "hanlim.com"},
    {"name": "CLOIT", "slug": "cloit", "domain": "cloit.com"},
    {"name": "DGIST", "slug": "dgist", "domain": "dgist.ac.kr"},
    {"name": "KAIST", "slug": "kaist", "domain": "kaist.ac.kr"},
    {"name": "Myongji University", "slug": "myongji-university", "domain": "mju.ac.kr"},
    {"name": "Busan Transportation Corporation", "slug": "busan-transportation", "domain": "humetro.busan.kr"},
    {"name": "Seoul National University", "slug": "seoul-national-university", "domain": "snu.ac.kr"},
    {"name": "D.BtoE", "slug": "dbtoe", "domain": "dbtoe.com"},
    {"name": "Quantum AI", "slug": "quantum-ai", "domain": "quantumai.co.kr"},
    {"name": "cocktail.io", "slug": "cocktail-io", "domain": "cocktail.io"},
]

# Investor FAQ
FAQ = [
    ("Is KQC Quantum Inc. publicly traded?",
     "Listing details, including the exchange, ticker symbol and the name of the listed issuer, will be published on this page when they become available. Until then, all market-data fields on this site are placeholders."),
    ("Where is the company incorporated and headquartered?",
     "KQC Quantum Inc. is the company that intends to list; its jurisdiction of incorporation will be published here with the listing details. It conducts its business through Korea Quantum Computing Co., Ltd. (한국퀀텀컴퓨팅㈜), incorporated in the Republic of Korea and headquartered in Busan, with an office in Seoul."),
    ("When was KQC founded?",
     "The operating company, Korea Quantum Computing Co., Ltd., was incorporated on December 28, 2021 and joined the IBM Quantum Network as a hub in April 2022. The date of incorporation of KQC Quantum Inc. will be published with the listing details."),
    ("What does KQC do?",
     "KQC operates three business lines: quantum computing (access to IBM quantum systems, algorithm R&amp;D, education and consulting), quantum security (post-quantum cryptography hardware including the Crypto4A QxHSM&trade;, KQC QuHSM&trade; and KQC QuKey Bio) and AI infrastructure (an NVIDIA H200-based GPU cloud, KQC GPUaaS)."),
    ("When does the fiscal year end?",
     "[December 31, to be confirmed in the company's first periodic report.]"),
    ("Who is the transfer agent?",
     "[Transfer agent name and contact details to be published at listing.]"),
    ("Who is the independent auditor?",
     "[Independent registered public accounting firm to be published at listing.]"),
    ("How can I receive investor updates?",
     "Use the email-alert form on the Investor Relations page. Until the alert system is connected, requests are routed to the IR mailbox."),
    ("How do I contact Investor Relations?",
     "Email ir@kqcquantum.com, or call the Busan headquarters at +82-51-791-0825."),
]

# Investment thesis pillars for the IR overview
THESIS = [
    {"n": "01", "title": "Korea's commercial quantum hub",
     "text": "A hub of the IBM Quantum Network since 2022 and an IBM Quantum Innovation Center, with a plan to install an IBM Quantum System Two in Busan. KQC sells quantum computing access and algorithm R&amp;D, and its Qubiteer platform lets customers run quantum optimization from a plain-language description of the problem."},
    {"n": "02", "title": "Post-quantum security hardware",
     "text": "A PQC-native product line built with Crypto4A: QxHSM&trade;, QuHSM&trade; and QuKey Bio. Proofs of concept completed with IBK Industrial Bank and LS ITC ahead of the expected 2030 regulatory deadline for post-quantum migration."},
    {"n": "03", "title": "AI infrastructure with recurring revenue",
     "text": "KQC GPUaaS on NVIDIA H200 SXM5, live since July 2025 at Digital Edge SEL2, with pay-as-you-go pricing and partners including ITCEN Group and Quantum AI. The GPU business produces revenue today and is designed to run alongside the quantum platform as it scales."},
    {"n": "04", "title": "Certified, and working with public institutions",
     "text": "ISO/IEC 27001 certified across all business lines, venture-certified, and working with Busan Metropolitan City, ETRI, POSCO Holdings, KT and KIOST. The team is 27 people, nine of them Ph.D.s, as of 2025."},
]

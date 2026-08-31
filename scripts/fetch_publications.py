#!/usr/bin/env python3
"""
PRISM Group — 논문 목록 생성기

세 개의 출처를 합쳐 논문 목록을 만들고, index.html 에 정적 HTML로 써 넣습니다.

  1) data/pmids.txt                     시드. 손으로 관리하며 항상 포함됩니다.
  2) PubMed  <ORCID>[auid]              ORCID를 붙여 낸 논문
  3) PubMed  "Kim, Yoo Hyung"[Full Author Name] + 소속 검증
                                        공저자 논문처럼 ORCID가 안 붙은 것까지 회수

3번은 저자 이름만으로는 동명이인 위험이 있으므로, efetch 로 해당 저자 항목의
**소속(affiliation)** 을 직접 확인해 AFFILIATIONS 패턴과 일치할 때만 자동 편입합니다.
소속 정보가 아예 없는 오래된 논문은 자동 편입하지 않고 '검토 필요'로 보고합니다.

제외:
  - data/pmids_excluded.txt 에 적힌 PMID
  - PublicationType 이 정정/철회(Published Erratum, Retraction 등)인 항목

출력:
    data/publications.json    기계가 읽는 목록
    data/candidates.json      검토가 필요한 후보 (있을 때만)
    index.html                PUBLICATIONS / PUBCOUNT 마커 사이를 교체

사용법:
    python3 scripts/fetch_publications.py
    python3 scripts/fetch_publications.py --check              # 파일을 쓰지 않고 차이만 보고
    python3 scripts/fetch_publications.py --accept 12345678    # 후보를 시드에 편입
    python3 scripts/fetch_publications.py --reject 12345678    # 후보를 제외 목록에 등록

환경변수 NCBI_API_KEY 를 넣으면 NCBI 속도 제한이 완화됩니다(없어도 동작).
"""
import hashlib, html, json, os, re, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

ORCID    = "0000-0002-5923-4915"
FULLNAME = "Kim, Yoo Hyung"          # PubMed [Full Author Name] 검색어
SURNAME  = "Kim"
FORENAME_RE = re.compile(r"^Yoo\s*Hyung$|^Yoo\s*H$|^Y\.?\s*H\.?$", re.I)

# 저자의 소속이 이 중 하나와 맞으면 본인 논문으로 인정
AFFILIATIONS = [
    r"Seoul National University",
    r"Korea Advanced Institute of Science",
    r"\bKAIST\b",
    r"Chungnam National University",
    r"Institute for Basic Science",
]
AFF_RE = re.compile("|".join(AFFILIATIONS), re.I)

# 정정/철회 등 목록에서 빼야 할 문헌 종류
SKIP_TYPES = {"Published Erratum", "Retraction of Publication", "Retracted Publication",
              "Comment", "Expression of Concern"}

# PubMed 쪽 저자명이 잘못 색인된 논문의 수동 보정
AUTHOR_OVERRIDE = {
    "26877926": "Kim YJ, <strong>Kim YH</strong>, Kim KD, <em>et al.</em>",
}

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED     = os.path.join(ROOT, "data", "pmids.txt")
EXCLUDE  = os.path.join(ROOT, "data", "pmids_excluded.txt")
OUT      = os.path.join(ROOT, "data", "publications.json")
CAND     = os.path.join(ROOT, "data", "candidates.json")
PAGE     = os.path.join(ROOT, "index.html")
EUTILS   = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
APIKEY   = os.environ.get("NCBI_API_KEY", "")

PUB_START,   PUB_END   = "<!-- PUBLICATIONS:START -->", "<!-- PUBLICATIONS:END -->"
COUNT_START, COUNT_END = "<!-- PUBCOUNT:START -->",     "<!-- PUBCOUNT:END -->"
# 프리즘 분광 — 그래파이트 바탕에서 바이올렛 → 슬레이트 → 블루 → 틸 순으로 순환
SWATCH = ["--h1:#33305e;--h2:#6d5cf0", "--h1:#232a3d;--h2:#5f7fd8",
          "--h1:#1f5560;--h2:#3fb8b0", "--h1:#14161c;--h2:#453a9c"]

# 페이지에 바로 보여줄 최근 논문 수. 나머지는 '더 보기'로 접힙니다.
VISIBLE = 5


# ---------------------------------------------------------------- HTTP
def _fetch(url, as_json=True):
    req = urllib.request.Request(url, headers={"User-Agent": "cell-identity-lab/1.0"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                raw = r.read()
            return json.loads(raw.decode("utf-8")) if as_json else raw
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def _key():
    return "&api_key=" + APIKEY if APIKEY else ""


def _pause():
    time.sleep(0.12 if APIKEY else 0.36)


def esearch(term):
    url = "%s/esearch.fcgi?db=pubmed&retmode=json&retmax=1000&term=%s%s" % (
        EUTILS, urllib.parse.quote(term), _key())
    ids = _fetch(url)["esearchresult"].get("idlist", [])
    _pause()
    return ids


def efetch(pmids):
    """efetch XML — 소속·문헌종류까지 포함한 전체 레코드."""
    recs = {}
    for i in range(0, len(pmids), 100):
        chunk = pmids[i:i + 100]
        url = "%s/efetch.fcgi?db=pubmed&retmode=xml&id=%s%s" % (EUTILS, ",".join(chunk), _key())
        root = ET.fromstring(_fetch(url, as_json=False))
        for art in root.findall(".//PubmedArticle"):
            pid = art.findtext(".//MedlineCitation/PMID")
            if pid:
                recs[pid] = art
        _pause()
    return recs


# ---------------------------------------------------------------- 목록 파일
def read_list(path):
    if not os.path.exists(path):
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if line.isdigit():
                out.append(line)
    return out


def append_list(path, pmids, note):
    header_needed = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("# 검토 후 제외한 PMID 목록. 한 줄에 하나, '#'는 주석.\n\n")
        for p in pmids:
            f.write("%s   # %s (%s)\n" % (p, note, time.strftime("%Y-%m-%d")))


# ---------------------------------------------------------------- 레코드 파싱
def _authors(art):
    out = []
    for a in art.findall(".//Article/AuthorList/Author"):
        last = a.findtext("LastName") or a.findtext("CollectiveName") or ""
        fore = a.findtext("ForeName") or ""
        init = a.findtext("Initials") or ""
        affs = [e.text or "" for e in a.findall("AffiliationInfo/Affiliation")]
        out.append({"last": last, "fore": fore, "init": init, "affs": affs})
    return out


def is_me(a):
    return a["last"] == SURNAME and bool(FORENAME_RE.match(a["fore"].strip()))


def affiliation_ok(art):
    """본인으로 보이는 저자 항목의 소속이 알려진 기관과 맞는지."""
    mine = [a for a in _authors(art) if is_me(a)]
    if not mine:
        return None                      # 이름이 안 잡힘 → 판단 불가
    has_aff = any(a["affs"] for a in mine)
    if not has_aff:
        return None                      # 소속 정보 없음 → 판단 불가
    for a in mine:
        for aff in a["affs"]:
            if AFF_RE.search(aff):
                return True
    return False


def fmt_authors(art, pmid):
    if pmid in AUTHOR_OVERRIDE:
        return AUTHOR_OVERRIDE[pmid]
    auth = _authors(art)
    if not auth:
        return ""
    names = [("%s %s" % (a["last"], a["init"])).strip() for a in auth]
    marked = ["<strong>%s</strong>" % n if is_me(a) else n for n, a in zip(names, auth)]
    me = next((i for i, a in enumerate(auth) if is_me(a)), None)
    if me is None:
        return ", ".join(marked[:3]) + (", <em>et al.</em>" if len(marked) > 3 else "")
    if me < 3:
        head = marked[:max(3, me + 1)]
        return ", ".join(head) + (", <em>et al.</em>" if len(marked) > len(head) else "")
    return ", ".join(marked[:3]) + ", … " + marked[me] + (
        ", <em>et al.</em>" if me < len(marked) - 1 else "")


def _year(art):
    for path in (".//Article/Journal/JournalIssue/PubDate/Year",
                 ".//Article/ArticleDate/Year"):
        y = art.findtext(path)
        if y:
            return y
    md = art.findtext(".//Article/Journal/JournalIssue/PubDate/MedlineDate") or ""
    m = re.search(r"\d{4}", md)
    return m.group(0) if m else ""


def _title(art):
    el = art.find(".//Article/ArticleTitle")
    if el is None:
        return ""
    return html.unescape("".join(el.itertext())).strip().rstrip(".")


def _ids(art):
    out = {}
    for aid in art.findall(".//PubmedData/ArticleIdList/ArticleId"):
        out[aid.get("IdType")] = (aid.text or "").strip()
    return out


def pubtypes(art):
    return {(e.text or "").strip() for e in art.findall(".//Article/PublicationTypeList/PublicationType")}


def build(art, pmid):
    ids = _ids(art)
    return {
        "pmid": pmid,
        "doi": ids.get("doi", ""),
        "pmc": ids.get("pmc", ""),
        "title": _title(art),
        "journal": art.findtext(".//Article/Journal/ISOAbbreviation") or
                   art.findtext(".//Article/Journal/Title") or "",
        "year": _year(art),
        "authors": fmt_authors(art, pmid),
    }


# ---------------------------------------------------------------- 렌더링
def render_cards(pubs):
    """최근 VISIBLE 편은 바로 보이고, 나머지는 pcard--extra 로 접어 둡니다."""
    out = ['    <div class="pubs" id="pubsList">']
    for i, p in enumerate(pubs):
        extra = " pcard--extra" if i >= VISIBLE else ""
        t = html.escape(p["title"], quote=True)
        links = ['<a class="pill" href="https://pubmed.ncbi.nlm.nih.gov/%s/" target="_blank" '
                 'rel="noopener"><svg class="ic"><use href="#i-file"/></svg>PubMed</a>' % p["pmid"]]
        if p["doi"]:
            links.append('<a class="pill" href="https://doi.org/%s" target="_blank" rel="noopener">'
                         '<svg class="ic"><use href="#i-link"/></svg>DOI</a>' % p["doi"])
        if p["pmc"]:
            links.append('<a class="pill" href="https://www.ncbi.nlm.nih.gov/pmc/articles/%s/" '
                         'target="_blank" rel="noopener"><svg class="ic"><use href="#i-quote"/></svg>'
                         'Full text</a>' % p["pmc"])
        out.append(
            '      <article class="pcard%s">\n'
            '        <div class="pcard__thumb" style="%s">%s</div>\n'
            '        <div class="pcard__body">\n'
            '          <h3 class="pcard__title" data-en="%s" data-ko="%s">%s</h3>\n'
            '          <p class="pcard__authors">%s</p>\n'
            '          <p class="pcard__venue"><span class="tag tag--journal">%s</span>'
            '<span class="tag">%s</span></p>\n'
            '          <div class="pcard__actions">\n            %s\n          </div>\n'
            '        </div>\n'
            '      </article>' % (
                extra, SWATCH[i % 4], p["year"], t, t, t, p["authors"],
                html.escape(p["journal"]), p["year"], "\n            ".join(links)))

    out.append('    </div>')

    hidden = len(pubs) - VISIBLE
    if hidden > 0:
        out.append(
            '    <button class="list-toggle" id="pubsToggle" type="button" aria-expanded="false">\n'
            '      <span class="list-toggle__more" data-en="Show %d more papers" '
            'data-ko="논문 %d편 더 보기">Show %d more papers</span>\n'
            '      <span class="list-toggle__less" data-en="Show fewer" '
            'data-ko="접기">Show fewer</span>\n'
            '    </button>' % (hidden, hidden, hidden))
    return "\n".join(out)


def stamp_assets(page):
    """css/js 참조에 내용 해시를 붙여 브라우저 캐시가 옛 파일을 쓰지 못하게 합니다."""
    for attr, rel in (("href", "css/style.css"), ("src", "js/main.js")):
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        digest = hashlib.md5(open(path, "rb").read()).hexdigest()[:8]
        page = re.sub(r'%s="%s(\?v=[0-9a-f]+)?"' % (attr, re.escape(rel)),
                      '%s="%s?v=%s"' % (attr, rel, digest), page)
    return page


def splice(text, start, end, body, label):
    i, j = text.find(start), text.find(end)
    if i < 0 or j < 0 or j < i:
        sys.exit("index.html 에서 %s 마커를 찾지 못했습니다." % label)
    return text[:i + len(start)] + "\n" + body + "\n" + text[j:]


# ---------------------------------------------------------------- 메인
def main():
    argv = sys.argv[1:]
    check = "--check" in argv

    for flag, path, note in (("--accept", SEED, "검토 후 편입"),
                             ("--reject", EXCLUDE, "검토 후 제외")):
        if flag in argv:
            ids = [a for a in argv[argv.index(flag) + 1:] if a.isdigit()]
            if not ids:
                sys.exit("%s 뒤에 PMID를 지정하세요." % flag)
            append_list(path, ids, note)
            print("%s → %s 에 추가: %s" % (flag, os.path.relpath(path, ROOT), ", ".join(ids)))
            print("이어서 인자 없이 다시 실행하면 목록이 갱신됩니다.")
            return 0

    seed     = read_list(SEED)
    excluded = set(read_list(EXCLUDE))
    print("시드 목록            : %d편" % len(seed))
    print("제외 목록            : %d편" % len(excluded))

    try:
        by_orcid = esearch("%s[auid]" % ORCID)
        print("ORCID 검색           : %d편" % len(by_orcid))
    except Exception as e:
        by_orcid = []
        print("ORCID 검색 실패      : %s" % e)

    try:
        by_name = esearch('"%s"[Full Author Name]' % FULLNAME)
        print("이름 검색            : %d편  (\"%s\"[Full Author Name])" % (len(by_name), FULLNAME))
    except Exception as e:
        by_name = []
        print("이름 검색 실패       : %s" % e)

    known = set(seed)
    discovered = [p for p in dict.fromkeys(by_orcid + by_name)
                  if p not in known and p not in excluded]

    # 모든 후보의 전체 레코드를 받아 소속·문헌종류를 검증
    targets = [p for p in dict.fromkeys(seed + discovered) if p not in excluded]
    recs = efetch(targets)
    missing = [p for p in targets if p not in recs]
    if missing:
        print("\n! PubMed 레코드 조회 실패: %s" % ", ".join(missing))

    accepted, candidates, skipped = list(seed), [], []
    for pid in discovered:
        art = recs.get(pid)
        if art is None:
            continue
        bad = pubtypes(art) & SKIP_TYPES
        if bad:
            skipped.append((pid, ", ".join(sorted(bad))))
            continue
        verdict = affiliation_ok(art)
        info = build(art, pid)
        info["source"] = "ORCID" if pid in by_orcid else "이름 검색"
        if verdict is True:
            accepted.append(pid)
            info["verdict"] = "소속 확인됨 — 자동 편입"
            candidates.append(info)
        else:
            info["verdict"] = ("소속 불일치 — 검토 필요" if verdict is False
                               else "소속 정보 없음 — 검토 필요")
            candidates.append(info)

    auto = [c for c in candidates if c["verdict"].endswith("자동 편입")]
    review = [c for c in candidates if not c["verdict"].endswith("자동 편입")]

    if skipped:
        print("\n정정/철회 공고 제외   : %s" % ", ".join("%s (%s)" % s for s in skipped))
    if auto:
        print("\n★ 새 논문 자동 편입 (%d편) — 소속 확인됨" % len(auto))
        for c in auto:
            print("   %s  %s  %s  [%s]" % (c["pmid"], c["year"], c["title"][:62], c["source"]))
        print("   → 확정하려면 data/pmids.txt 에 PMID를 추가하세요:")
        print("     python3 scripts/fetch_publications.py --accept %s" % " ".join(c["pmid"] for c in auto))
    if review:
        print("\n? 검토 필요 (%d편) — 자동 편입하지 않았습니다" % len(review))
        for c in review:
            print("   %s  %s  %s\n      %s" % (c["pmid"], c["year"], c["title"][:62], c["verdict"]))
        print("   → --accept <PMID> 로 편입, --reject <PMID> 로 영구 제외")

    orphan = [p for p in seed if p not in by_orcid and p not in by_name]
    if orphan:
        print("\n※ 자동 검색으로는 안 잡히는 시드 논문 %d편 (시드 목록이 지켜주고 있음)" % len(orphan))
        print("   %s" % ", ".join(orphan))

    pubs = [build(recs[p], p) for p in accepted if p in recs]
    pubs.sort(key=lambda p: (p["year"], p["pmid"]), reverse=True)

    no_author = [p["pmid"] for p in pubs if "<strong>" not in p["authors"]]
    if no_author:
        print("\n! 저자 강조 실패 (PubMed 색인 확인 필요): %s" % ", ".join(no_author))

    print("\n최종 논문 수         : %d편" % len(pubs))
    if check:
        print("(--check: 파일을 쓰지 않았습니다)")
        return 1 if (auto or review) else 0

    payload = {"orcid": ORCID, "generated": time.strftime("%Y-%m-%d"),
               "source": "NCBI PubMed E-utilities",
               "queries": ["%s[auid]" % ORCID, '"%s"[Full Author Name]' % FULLNAME],
               "count": len(pubs), "publications": pubs}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if candidates:
        with open(CAND, "w", encoding="utf-8") as f:
            json.dump({"generated": time.strftime("%Y-%m-%d"), "candidates": candidates},
                      f, ensure_ascii=False, indent=2)
            f.write("\n")
    elif os.path.exists(CAND):
        os.remove(CAND)

    page = open(PAGE, encoding="utf-8").read()
    page = splice(page, PUB_START, PUB_END, render_cards(pubs), "PUBLICATIONS")
    sub = ('         <p class="shead__sub"\n'
           '            data-en="%d peer-reviewed papers · PubMed, auto-updated monthly"\n'
           '            data-ko="동료심사 논문 %d편 · PubMed 기준, 매월 자동 갱신">\n'
           '            %d peer-reviewed papers · PubMed, auto-updated monthly</p>'
           % (len(pubs), len(pubs), len(pubs)))
    page = splice(page, COUNT_START, COUNT_END, sub, "PUBCOUNT")
    page = stamp_assets(page)
    open(PAGE, "w", encoding="utf-8").write(page)

    print("생성                 : data/publications.json, index.html"
          + (", data/candidates.json" if candidates else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())

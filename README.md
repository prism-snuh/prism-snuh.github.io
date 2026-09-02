# PRISM Group — Homepage

**PRISM Group** — Plasticity, RNA, Identity, Senescence and Modulation.
Laboratory of Thyroid ImmunoMetabolism in SNUH (LTIMS) 소속 연구그룹 (PI: 김유형)의 홈페이지.
정적 사이트(HTML/CSS/JS)로, GitHub Pages에 그대로 배포할 수 있습니다.

> 이 저장소를 Claude(Cowork·Claude Code)로 관리할 때의 규칙은 **`CLAUDE.md`** 에 있습니다.

## 구성

```
labpage/
├── index.html                      # 단일 페이지 (Research / News / Publications / Team / Join)
├── css/style.css                   # 바이올렛 테마 (변수명은 --teal-*/--emerald 이지만 값은 바이올렛)
├── js/main.js                      # 언어 토글(EN/한) · 모바일 메뉴 · 연도
├── assets/                         # 이미지 등 (프로필 사진 넣는 곳)
├── data/
│   ├── pmids.txt                   # 논문 시드 목록 (손으로 관리)
│   ├── pmids_excluded.txt          # 검토 후 제외한 PMID (동명이인 등)
│   ├── publications.json           # 생성된 논문 데이터
│   └── candidates.json             # 검토가 필요한 후보 (있을 때만 생성)
├── scripts/
│   └── fetch_publications.py       # PubMed에서 논문을 받아 index.html에 써 넣는 생성기
└── .github/workflows/
    └── publications.yml            # 매월 1일 자동 갱신
```

## 로컬에서 미리보기

```bash
cd labpage
python3 -m http.server 8000
# 브라우저에서 http://localhost:8000 열기
```

## GitHub Pages 배포

1. GitHub에서 새 저장소 생성 (예: `prism-group` 또는 `<username>.github.io`).
2. 이 폴더를 push:
   ```bash
   cd labpage
   git init
   git add .
   git commit -m "PRISM Group homepage"
   git branch -M main
   git remote add origin https://github.com/<username>/<repo>.git
   git push -u origin main
   ```
3. 저장소 **Settings → Pages → Source**에서 `main` 브랜치 `/ (root)` 선택 후 저장.
4. 몇 분 뒤 `https://<username>.github.io/<repo>/` 에서 확인.

> `<username>.github.io` 이름의 저장소로 만들면 `https://<username>.github.io/` 로 바로 열립니다.

## 디자인 메모

- 색은 바이올렛 계열(`--emerald: #6d5cf0`)입니다. 변수 **이름**은 초기 틸 테마의 것이 남아 있으니 값만 보고 판단하세요.
- greenelab lab-website-template의 컴포넌트 감각(태그 pill, 가로형 논문 카드 + PubMed/DOI/Full text 버튼,
  원형 포트레이트 + 소셜 아이콘, 아이콘 섹션 헤더, 풀블리드 히어로 배너)을 반영했습니다.
- 폰트는 greenelab 시그니처인 **Atkinson Hyperlegible**(+ 한글 Noto Sans KR).
- 아이콘은 외부 CDN 없이 `index.html` 상단의 인라인 SVG 스프라이트(`<symbol id="i-...">`)를 `<use>`로 참조합니다. (오프라인·GitHub Pages에서 안전)

## 콘텐츠 교체 가이드

- **실제 논문**: `<div class="pubs">`의 `.pcard` 항목 교체. `.pcard__thumb`의 `--h1/--h2`로 썸네일 색을 바꾸거나, 이미지로 대체하려면 `background`를 `url(assets/...)`로 지정.
- **구성원**: `<section id="team">`의 `.mcard` 교체, 사진은 `assets/`에 넣고 `.mcard__portrait`에 `background-image` 지정. 소셜 링크는 `.soc`의 `href` 수정.
- **소식**: `<ul class="news">` 항목 추가/수정.
- **태그**: `<span class="tag">…</span>` (역할 강조는 `tag--role`, 저널은 `tag--journal`).
- **이중 언어**: 각 요소의 `data-en` / `data-ko` 속성을 함께 수정하면 토글에 반영됩니다.
- **색상**: `css/style.css` 상단 `:root` 변수(`--teal-700`, `--emerald` 등)만 바꾸면 전체 테마가 바뀝니다.

## 현재 콘텐츠 상태

| 섹션 | 상태 |
|---|---|
| Research (4갈래) | 실제 연구 주제 |
| Publications | **실제 논문 32편.** biosketch를 PubMed와 전수 대조해 확정했습니다. `scripts/fetch_publications.py`가 자동 생성하며, PubMed·DOI·PMC 링크가 모두 실제 URL입니다. |
| News | 실제 수상 소식 4건입니다. |
| Team | PI 사진은 실물, 대학원생 5명은 **연구 주제를 그린 SVG 아바타**(`assets/avatar-*.svg`)입니다. |
| 소셜 링크 | ORCID만 연결합니다. **Google Scholar는 의도적으로 넣지 않습니다**(논문을 온전히 수집하지 못해 사용하지 않음). |

## 사진 올리기

1. 사진 파일을 `assets/` 폴더에 넣습니다. 예) `assets/2026-09-workshop.jpg`
2. `index.html` 의 `<!-- 여기부터 사진 목록 -->` 아래에 아래 블록을 붙여넣습니다.

```html
<figure class="photo">
  <img src="assets/2026-09-workshop.jpg" alt="2026 연구실 워크숍" loading="lazy">
  <figcaption>2026 연구실 워크숍</figcaption>
</figure>
```

- 사진이 하나라도 있으면 "아직 등록된 사진이 없습니다" 안내가 자동으로 사라집니다.
- **사진을 클릭하면 원본 크기로 크게 열립니다.** 바깥을 누르거나 `Esc` 로 닫고, 좌우 화살표(또는 `←` `→` 키)로 넘깁니다.
  이 기능은 `js/main.js` 가 알아서 붙이므로 사진을 추가할 때 따로 할 일은 없습니다.
- 사진은 **4:3 으로 잘려** 표시됩니다. 원본 비율은 유지되지 않습니다.
- 긴 변 **1600px 이하**를 권합니다. 원본 사진을 그대로 올리면 페이지가 느려집니다.
- `alt` 에는 사진 설명을 넣어 주세요. 화면에 보이지는 않지만 접근성과 검색에 쓰입니다.
- GitHub 웹에서도 `assets/` 폴더 → **Add file → Upload files** 로 사진을 올릴 수 있습니다.

## 목록 접기

| 섹션 | 기본 노출 | 방식 |
|---|---|---|
| Publications | 5편 | 생성기가 HTML에 직접 표시 (`VISIBLE` 상수) |
| News | 5건 | `js/main.js` 가 자동 처리 |

News는 손으로 편집하는 영역이라 **`<li>` 를 추가하기만 하면 됩니다.**
6건이 넘는 순간 JS가 알아서 나머지를 감추고 "N건 더 보기" 버튼을 만들어 붙입니다.
5건 이하면 버튼은 나타나지 않습니다. 클래스를 직접 붙일 필요가 없습니다.

## 칼럼 쓰기

`index.html` 의 `<section id="column">` 안, `<!-- 여기부터 글 목록 -->` 바로 아래에
아래 블록을 붙여넣고 내용만 바꾸면 됩니다. **최신 글이 맨 위**입니다.

```html
<article class="col">
  <time class="col__date">2026 · 09</time>
  <h3 class="col__title">제목</h3>
  <p>첫 문단.</p>
  <p>둘째 문단.</p>
</article>
```

- 문단마다 `<p>…</p>` 로 감쌉니다. 빈 줄만으로는 문단이 나뉘지 않습니다.
- **이 섹션은 `data-en` / `data-ko` 없이 써도 됩니다.** 두 속성이 없으면 언어를 바꿔도
  쓴 그대로 보입니다. 영문·한글을 따로 두고 싶을 때만 추가하세요.
- 링크는 `<a href="https://…">텍스트</a>`, 강조는 `<strong>텍스트</strong>`.
- 글이 많이 쌓이면 논문 목록처럼 접기를 넣을 수 있습니다.

GitHub 웹 편집기(저장소 → `index.html` → 연필 아이콘 → Commit)로 바로 수정할 수 있고,
커밋하면 GitHub Pages에 1분 내 반영됩니다. 이 영역은 논문 자동 갱신이 건드리지 않습니다.

## Code 섹션

등록된 코드가 하나도 없으면 Code 섹션과 상단 메뉴의 Code 링크가 **자동으로 숨겨집니다.**
`<!-- 여기부터 코드 목록 -->` 아래에 첫 `pcard` 블록을 넣는 순간 다시 나타납니다. 손댈 것이 없습니다.
항상 보이게 하려면 `js/main.js` 의 `initHideEmptySections()` 안 배열에서 `code` 줄을 지우세요.

## 논문 목록 관리

논문 목록은 **index.html을 직접 수정하지 않습니다.** `scripts/fetch_publications.py`가
`<!-- PUBLICATIONS:START -->` ~ `<!-- PUBLICATIONS:END -->` 사이를 통째로 교체합니다.

### 표시 방식

최근 **5편**만 바로 보이고 나머지는 "Show N more papers" 버튼으로 접힙니다.
편수는 `scripts/fetch_publications.py` 상단의 `VISIBLE` 상수와 `js/main.js` 의 `initCollapse()` 안 `limit` 을 **함께** 바꿉니다.
접힌 카드도 HTML에는 그대로 들어 있어 검색엔진에는 전부 노출됩니다.

### 세 개의 출처

| 출처 | 쿼리 | 성격 |
|---|---|---|
| 시드 | `data/pmids.txt` | 손으로 관리. 항상 포함 |
| ORCID | `0000-0002-5923-4915[auid]` | ORCID를 붙여 낸 논문 |
| 이름 + 소속 | `"Kim, Yoo Hyung"[Full Author Name]` | 공저자 논문처럼 ORCID가 안 붙은 것까지 회수 |

**왜 세 개인가.** 공저자 논문은 교신저자가 제출하면서 공저자 ORCID를 넣지 않는 경우가 많아,
ORCID만으로는 구조적으로 누락이 생깁니다. 실제로 이름 검색이 biosketch에도 없던 논문
(Pituitary 2022, PMID 36322283)을 찾아냈습니다.

반대로 이름 검색만 쓰면 동명이인이 섞입니다. `Kim YH[Author]`로 검색하면 1,385건이 나옵니다.
그래서 **전체 이름 필드**(`[Full Author Name]`)로 좁힌 뒤, efetch로 **해당 저자 항목의 소속을 직접 확인**해
아래 기관과 일치할 때만 자동 편입합니다.

```
Seoul National University · KAIST · Chungnam National University · Institute for Basic Science
```

소속이 확인되지 않으면 자동 편입하지 않고 `data/candidates.json`에 '검토 필요'로 남깁니다.

### 자동 제외

- `data/pmids_excluded.txt` 에 등록된 PMID
- `PublicationType` 이 `Published Erratum` · `Retraction` · `Comment` 등인 문헌
  (제목이 아니라 문헌 종류로 판정하므로 "Corrigendum to…" 같은 변형도 정확히 걸러집니다)

### 자동 갱신

`.github/workflows/publications.yml`이 **매월 1일** 실행돼 목록을 갱신하고, 바뀐 게 있으면 자동 커밋합니다.
Actions 탭의 **Run workflow** 로 즉시 실행할 수도 있습니다.
소속이 확인된 새 논문은 사람 손 없이 편입되고, 확인이 안 된 후보만 경고로 올라옵니다.
저장소 Settings → Secrets 에 `NCBI_API_KEY` 를 넣으면 NCBI 속도 제한이 완화됩니다(없어도 동작).

### 수동 실행

```bash
python3 scripts/fetch_publications.py                     # 갱신 후 파일 쓰기
python3 scripts/fetch_publications.py --check             # 차이만 확인, 파일은 그대로
python3 scripts/fetch_publications.py --accept 12345678   # 후보를 시드에 편입
python3 scripts/fetch_publications.py --reject 12345678   # 후보를 영구 제외
```

### ORCID 백필 (권장)

현재 32편 중 **7편만** ORCID에 연결돼 있습니다. 이름+소속 검색이 보완하고는 있지만,
ORCID를 채워두면 더 견고해집니다. [orcid.org](https://orcid.org) → **Add works → Search & link → Europe PMC**.
대조할 PMID는 `data/pmids.txt` 에 있습니다.

### 알려진 데이터 이슈

- **자동 검색으로 안 잡히는 논문 3편** — PMID `28869715`, `27346188`, `26877926`. 오래된 논문이라
  PubMed에 전체 이름이 아니라 약어(`Kim Yoo H`, `Kim Y H`)로만 색인돼 있어 `[Full Author Name]` 검색에 걸리지 않습니다.
  `data/pmids.txt` 시드가 이 논문들을 지켜주고 있으므로 목록에서 빠지지는 않습니다.
- PMID `26877926` (Kidney Res Clin Pract 2013)은 PubMed 쪽 저자명이 `Hyung Kim, Yoo`로 성/이름이 뒤집혀
  색인돼 있습니다. `AUTHOR_OVERRIDE`로 표시를 보정했습니다.
  목록에서 빼시려면 `data/pmids.txt` 에서 해당 줄만 지우고 스크립트를 다시 실행하면 됩니다.

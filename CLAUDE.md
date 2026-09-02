# CLAUDE.md — PRISM Group 홈페이지 관리 규칙

이 저장소를 다루는 모든 세션(Cowork 채팅방, Claude Code)이 따르는 규칙입니다.
사람이 읽어도 되지만, 1차 독자는 Claude입니다.

- **저장소**: `prism-snuh/prism-snuh.github.io` (GitHub Pages, `main` 브랜치 `/` 루트)
- **공개 주소**: https://prism-snuh.github.io/
- **구조**: 빌드 없는 정적 사이트. `index.html` 단일 페이지 + `css/style.css` + `js/main.js`
- **PI**: 김유형 (Yoo Hyung Kim) · ORCID `0000-0002-5923-4915`
- 사용법·설계 배경은 `README.md`. 이 문서는 **작업 규칙**만 다룹니다.

---

## 1. 절대 하지 말 것

1. **`<!-- PUBLICATIONS:START -->` ~ `<!-- PUBLICATIONS:END -->` 사이를 손으로 고치지 않는다.**
   `<!-- PUBCOUNT:START -->` ~ `END` 구간도 같다.
   두 구간은 `scripts/fetch_publications.py`가 통째로 덮어쓴다. 손댄 내용은 다음 실행에서 사라진다.
   논문을 넣고 빼려면 `data/pmids.txt` / `data/pmids_excluded.txt` 를 고치고 스크립트를 돌린다.
2. **`.docx`, `~$*`, `*_v1.*`, `NEXT_STEPS.md`, `.claude/` 를 커밋하지 않는다.**
   `.gitignore` 에 이미 들어 있다. biosketch에는 연구비 금액과 percent effort가 들어 있어 **공개 시 사고**다.
   `git add -A` 앞에 `git status` 로 무엇이 올라가는지 항상 눈으로 확인한다.
3. **구성원·사진은 본인 공개 동의를 받은 것만 올린다.** 동의 여부가 불확실하면 올리지 말고 물어본다.
4. **연락처 이메일을 평문으로 쓰지 않는다.** 현재 표기: `yhkimmd.ndokim at gmail dot com` (스팸 수집 회피).
5. 사용자가 명시적으로 요청하지 않은 디자인 변경(색·폰트·레이아웃)을 임의로 하지 않는다.

## 2. 섹션별 편집 지점

| 섹션 | id | 어디를 고치나 | 비고 |
|---|---|---|---|
| Research | `#research` | `index.html` 직접 | 4갈래 연구 주제 |
| News | `#news` | `<ul id="newsList">` 안에 `<li class="news__item">` **맨 위**에 추가 | 6건 넘으면 JS가 자동으로 접고 "N건 더 보기" 생성 |
| Publications | `#publications` | **손대지 않음** — `data/pmids.txt` + 스크립트 | 아래 4장 |
| Team | `#team` | PI는 `<article class="pi">`, 나머지는 `<div class="grid grid--team">` 안 `.mcard` | |
| Column | `#column` | `<!-- 여기부터 글 목록 -->` 아래에 `<article class="col">` **맨 위**에 추가 | 최신 글이 위 |
| Photos | `#photos` | `<!-- 여기부터 사진 목록 -->` 아래에 `<figure class="photo">` | 아래 5장 |
| Code | `#code` | `<!-- 여기부터 코드 목록 -->` 아래에 `<article class="pcard">` | 비면 자동 숨김, 아래 6장 |
| Join / Footer | `#join` | `index.html` 직접 | |

각 섹션 바로 위 HTML 주석에 복사용 블록이 들어 있다. **새 블록은 그 주석을 복사해서 만든다.**

## 3. 이중언어 규칙

- 화면에 보이는 문자열은 `data-en` / `data-ko` 를 **둘 다** 넣고, 요소 안 텍스트에는 **영문**을 쓴다.
  `js/main.js`가 언어 스위치에 따라 `innerHTML`을 통째로 갈아끼운다.
- **기본 언어는 영어.** 방문자가 한국어를 고른 경우에만 `localStorage`에 기억된다.
- **Column 섹션은 예외** — 두 속성 없이 한 언어로만 써도 된다. 그러면 언어를 바꿔도 쓴 그대로 보인다.
- 두 속성 중 하나만 넣으면 안 된다. 스위치가 그 요소를 건너뛰어 언어가 섞인다.
- 사람 이름 영문 표기는 **기존 표기를 그대로 따른다** (예: `Yoo Hyung Kim`, `Kyu Ri Kim`). 임의로 로마자화하지 않는다.

## 4. 논문 목록 (Publications)

### 파이프라인
`data/pmids.txt` (시드·손으로 관리) + PubMed ORCID 검색 + 이름·소속 검색
→ `scripts/fetch_publications.py` → `data/publications.json` + `index.html`의 PUBLICATIONS 구간

`Published Erratum` · `Retraction` · `Comment` 는 **문헌 종류로** 자동 제외된다(제목이 아니라).

### ⚠ 네트워크 제약 (중요)
`eutils.ncbi.nlm.nih.gov` 는 **Cowork 세션의 로컬 맥 셸에서도, 클라우드 컨테이너에서도 차단**되어 있다
(`Tunnel connection failed: 403 Forbidden`). 즉 **이 채팅방에서는 스크립트를 실행할 수 없다.**

실행 경로는 셋뿐이다.

| 경로 | 방법 |
|---|---|
| 자동 (기본) | `.github/workflows/publications.yml` — **매월 1일** 실행, 변경 시 자동 커밋 |
| 즉시 실행 | GitHub → Actions 탭 → `publications` → **Run workflow** |
| 교수님 로컬 | 맥 터미널에서 `python3 scripts/fetch_publications.py` |

**채팅방에서 "새 논문 있는지 확인"을 요청받으면**, 스크립트 대신 PubMed MCP 도구로 확인한다.

1. `search_articles("0000-0002-5923-4915[auid]")`
2. `search_articles("\"Kim, Yoo Hyung\"[Full Author Name]")`
3. 두 결과의 합집합에서 `data/pmids.txt` 에 없는 PMID를 추린다
4. 각 후보를 `get_article_metadata` 로 열어 **`article_types` 에 `Published Erratum` 등이 있으면 제외**,
   **저자 항목의 소속**이 아래와 맞는지 확인한다(동명이인 방지)
   ```
   Seoul National University · KAIST · Chungnam National University · Institute for Basic Science
   ```
5. 진짜 새 논문이면 `data/pmids.txt` 에 추가하고 커밋 → 다음 workflow 실행 때 페이지에 반영된다.
   반영을 앞당기려면 Actions에서 Run workflow.

### 알려진 이슈 (반복 확인 불필요)
- PMID `28869715`, `27346188`, `26877926` 은 PubMed에 약어명으로만 색인돼 자동 검색에 안 잡힌다.
  `data/pmids.txt` 시드가 지키고 있으므로 **목록에서 빠지지 않는다.** 매번 다시 조사하지 말 것.
- PMID `26877926` 은 저자명이 `Hyung Kim, Yoo` 로 뒤집혀 색인돼 있어 `AUTHOR_OVERRIDE` 로 보정 중.
- ORCID에 연결된 논문은 32편 중 7편. 나머지는 이름+소속 검색이 회수한다.
  교수님이 ORCID를 백필하면 더 견고해진다(orcid.org → Add works → Search & link → Europe PMC).

## 4-1. 소셜 링크 방침

- **Google Scholar 링크는 넣지 않는다.** 교수님 논문을 온전히 수집하지 못해 쓰지 않으신다.
  "소셜 링크가 ORCID뿐"인 것은 미완성이 아니라 의도된 상태다. 다시 제안하지 말 것.
- 현재 연결된 것은 **ORCID(`0000-0002-5923-4915`)** 하나이며, PI 카드와 푸터 두 곳에 있다.
- PI 사진은 `assets/pi-yoo-hyung-kim.jpg` (416×416 정사각, 104px 원형으로 표시).
- **구성원(대학원생)은 실제 사진을 올리지 않는다.** 대신 연구 주제를 그린 SVG 아바타를 쓴다.
  `assets/avatar-<slug>.svg` — 류한국 RNA 가닥 · 남석준 혈관 분지 · 김규리 미토콘드리아 ·
  최동화 폐 · 조민정 세포. 200×200 viewBox 정사각이며 원형 처리는 CSS가 한다.
  새 구성원은 기존 SVG를 복사해 `motif` 도형과 색(`hue`/`soft`)만 바꾸면 된다.

## 5. 사진

- 파일은 `assets/` 에. 이름은 `YYYY-MM-설명.jpg` 형식 (예: `2026-08-kta-award-pi.jpg`).
- **긴 변 1600px 이하**로 줄여서 올린다. 원본을 그대로 올리면 페이지가 느려진다.
- 화면에는 **4:3 으로 잘려** 보인다. 인물이 가장자리에 있으면 잘린다.
- `alt` 는 영문 서술(접근성·검색용), `figcaption` 은 `data-en`/`data-ko` 둘 다.
- 사진이 하나라도 있으면 "등록된 사진이 없습니다" 안내는 JS가 자동으로 지운다.
- 클릭하면 원본을 크게 보여 주는 라이트박스가 `js/main.js` 의 `initLightbox()` 에 있다.
  마크업은 JS가 만들어 붙이므로 `index.html` 에는 없다. 사진을 추가할 때 손댈 것이 없다.
  캡션의 `data-en`/`data-ko` 를 그대로 물려받으므로 언어 스위치가 확대 화면에도 적용된다.

## 6. Code 섹션

- 항목이 하나도 없으면 `js/main.js`의 `initHideEmptySections()` 가 **섹션 본문과 상단 메뉴의 Code 링크를 함께 감춘다.**
  첫 `.pcard` 를 넣는 순간 자동으로 다시 나타난다. 손댈 것이 없다.
- 항상 보이게 하려면 `initHideEmptySections()` 안 배열에서 `{ sectionId: "code", ... }` 줄만 지운다.
- 저널이 영구 식별자를 요구하면 GitHub 주소만으로는 반려된다. Zenodo에 저장소를 연결해 릴리스 DOI를 받는다.

## 7. JS·CSS를 고쳤을 때

`index.html` 마지막 줄의 캐시 버스터를 **반드시** 새 해시로 바꾼다. 안 바꾸면 방문자 브라우저에 옛 JS가 남는다.

```bash
NEW=$(python3 -c "import hashlib;print(hashlib.md5(open('js/main.js','rb').read()).hexdigest()[:8])")
python3 - "$NEW" <<'PY'
import io,re,sys
s=io.open('index.html',encoding='utf-8').read()
io.open('index.html','w',encoding='utf-8').write(
    re.sub(r'js/main\.js\?v=[0-9a-f]*', 'js/main.js?v=%s'%sys.argv[1], s, count=1))
PY
```

## 8. 작업 절차

1. 무엇을 바꿀지 **먼저 사용자에게 한 줄로 보고**하고 진행한다.
2. 파일 수정 (device_bash로 로컬 맥에서 직접. 스테이징하지 않는다)
3. 미리보기 — `cd labpage && python3 -m http.server 8000` → http://localhost:8000
4. `git status` 로 올라갈 파일 확인 → `git diff` 로 내용 확인
5. 커밋 (`git commit`) — **여기까지가 채팅방에서 가능한 범위**
6. **`git push` 는 교수님이 맥 터미널에서 직접 실행한다.** 아래 9장 참고
7. 1분쯤 뒤 https://prism-snuh.github.io/ 에서 반영 확인

> **논문 목록은 예외.** `data/publications.json` 과 `index.html` 의 PUBLICATIONS 구간은
> GitHub Actions가 GitHub 서버에서 직접 커밋하고 push한다 (`permissions: contents: write`).
> 사람의 push가 전혀 필요 없다. 위 절차는 **손으로 고치는 영역**(소식·구성원·사진·칼럼·코드·설정)에만 적용된다.

### 커밋 메시지

한국어 한 줄, 접두어를 붙인다. 본문은 필요할 때만.

| 접두어 | 쓰는 때 | 예 |
|---|---|---|
| `content:` | 소식·구성원·사진·칼럼 등 내용 | `content: 사진 3장 등록` |
| `feat:` | 새 섹션·새 기능 | `feat: 코드 섹션 추가` |
| `fix:` | 버그·오표기 수정 | `fix: 학회명 정정` |
| `chore:` | 설정·문서·정리 | `chore: 연락처 이메일 변경` |
| `docs:` | README·CLAUDE.md | `docs: 관리 규칙 문서 추가` |

`data/publications.json` 만 바뀐 커밋은 workflow가 자동으로 만든다. 사람이 흉내내지 않는다.

## 9. 작업 기기 — MacBook Air 전용

이 저장소는 **MacBook Air 한 대에서만** 다룬다. Cowork 세션도 Air에 연결해서 쓴다.

폴더가 Google Drive 안에 있어(`~/Library/CloudStorage/GoogleDrive-.../claude/code/project/labpage`)
여러 기기에서 같은 `.git` 을 건드리면 Drive 동기화가 반쪽만 내려온 상태에서 저장소가 깨진다.
실제로 MacBook Pro에서 `git push` 하다 `src refspec refs/heads/main does not match any`
(로컬에 main 브랜치가 없음 = `.git/refs/heads/main` 이 클라우드 자리표시자 상태)가 났다.

- **다른 맥에서는 이 폴더의 git 명령을 실행하지 않는다.**
- Drive 스트리밍 탓에 파일 읽기가 `Resource deadlock avoided` 로 실패할 수 있다(예: `NEXT_STEPS.md`).
  그때는 파일 내용을 교수님께 직접 여쭙는다.

## 10. 이 채팅방(Cowork)의 제약

- **`git push` 를 할 수 없다.** `device_bash` 는 맥 위의 격리된 리눅스 VM이라 macOS 키체인의
  GitHub 자격증명에 접근하지 못한다 (`could not read Username for 'https://github.com'`).
  이것은 **이 채팅방에서 손으로 고친 변경분에만** 해당한다. GitHub Actions는 GitHub 서버에서 도므로
  네트워크도 자격증명도 문제가 없고, 논문 갱신은 봇이 알아서 커밋·push한다.
  커밋까지만 하고, 교수님께 아래 한 줄을 안내한다.
  ```bash
  cd ~/Library/CloudStorage/GoogleDrive-yoohyungk@gmail.com/My\ Drive/claude/code/project/labpage && git push
  ```
- **`git` 작업 전에 `rm -f .git/index.lock` 이 필요할 수 있다.** 마운트에 기본적으로 삭제 권한이 없어
  앞선 세션이 남긴 잠금 파일이 지워지지 않는다. 삭제 권한은 `device_request_delete_permission` 로 받는다.
- 로컬 맥 셸(`device_bash`)은 **`github.com` 읽기(fetch/ls-remote)는 되고 `eutils.ncbi.nlm.nih.gov` 는 막혀 있다.**
- Google Drive 마운트 특성상 일부 파일 읽기가 `Resource deadlock avoided` 로 실패할 수 있다
  (실제로 `NEXT_STEPS.md` 가 그렇다). 그 파일은 교수님께 직접 확인을 요청한다.
- 파일은 로컬 맥에서 직접 고친다. 컨테이너로 스테이징하는 것은 이미지를 눈으로 봐야 할 때 정도다.

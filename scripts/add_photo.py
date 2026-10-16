#!/usr/bin/env python3
"""사진을 Photos 섹션에 추가합니다.

하는 일
  1. 긴 변 1600px 이하로 줄이고 JPEG로 저장합니다 (원본은 건드리지 않음).
     위치정보(GPS) 등 사진 정보(EXIF)는 지웁니다. HEIC(아이폰)도 받습니다.
  2. assets/YYYY-MM-<이름>.jpg 로 저장합니다. 같은 이름이 있으면 -2, -3 을 붙입니다.
  3. index.html 의 "여기부터 사진 목록" 바로 아래(맨 위)에 figure 블록을 넣습니다.
     여러 장이면 입력한 순서대로 위에서부터 놓입니다.
  4. --commit 을 주면 git add + git commit 까지 합니다. push 는 직접 하세요.

예
  python3 scripts/add_photo.py ~/Downloads/IMG_1234.jpg ~/Downloads/IMG_1235.HEIC \\
      --date 2026-10 --name ksmcb-poster \\
      --en "Poster session — Korean Society for Molecular and Cellular Biology, 2026" \\
      --ko "2026 한국분자·세포생물학회 포스터 발표" --commit

  --dry-run 을 주면 아무것도 바꾸지 않고 무엇을 할지만 보여 줍니다.

필요한 것: Pillow (conda base 에 기본 포함). 없으면 macOS 의 sips 로 줄이되,
그 경우 EXIF 가 남을 수 있어 경고를 띄웁니다.
"""
import argparse
import html
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, "assets")
INDEX = os.path.join(ROOT, "index.html")
ANCHOR = "      <!-- 여기부터 사진 목록 -->\n"
MAX_SIDE = 1600

try:
    from PIL import Image, ImageOps
    HAVE_PIL = True
except ImportError:
    HAVE_PIL = False


def heic_to_jpeg(src, tmpdir):
    """HEIC 는 Pillow 가 못 여는 경우가 많아 macOS sips 로 먼저 JPEG 변환."""
    out = os.path.join(tmpdir, os.path.splitext(os.path.basename(src))[0] + ".jpg")
    subprocess.run(["sips", "-s", "format", "jpeg", src, "--out", out],
                   check=True, stdout=subprocess.DEVNULL)
    return out


def resize(src, dst):
    """긴 변 MAX_SIDE 이하 JPEG 로 저장. (w, h) 반환."""
    with tempfile.TemporaryDirectory() as tmp:
        if src.lower().endswith((".heic", ".heif")):
            src = heic_to_jpeg(src, tmp)
        if HAVE_PIL:
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
            im.save(dst, "JPEG", quality=85, optimize=True, progressive=True)  # exif 미포함
            return im.size
        if shutil.which("sips"):
            print("  ! Pillow 가 없어 sips 로 줄입니다. 사진 정보(EXIF, 위치 포함)가 남을 수 있습니다.")
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85",
                            "-Z", str(MAX_SIDE), src, "--out", dst],
                           check=True, stdout=subprocess.DEVNULL)
            return None
        sys.exit("Pillow 도 sips 도 없습니다. `pip install pillow` 후 다시 실행하세요.")


def unique_name(base):
    """assets/ 에 같은 이름이 있으면 -2, -3 ... 을 붙임."""
    name, n = base, 2
    while os.path.exists(os.path.join(ASSETS, name + ".jpg")):
        name = f"{base}-{n}"
        n += 1
    return name + ".jpg"


def figure_block(filename, alt, en, ko):
    a, e, k = (html.escape(s, quote=True) for s in (alt, en, ko))
    return (
        "\n"
        '      <figure class="photo">\n'
        f'        <img src="assets/{filename}" loading="lazy"\n'
        f'             alt="{a}">\n'
        f'        <figcaption data-en="{e}"\n'
        f'                    data-ko="{k}">{e}</figcaption>\n'
        "      </figure>\n"
    )


def main():
    p = argparse.ArgumentParser(description="Photos 섹션에 사진 추가")
    p.add_argument("photos", nargs="+", help="사진 파일 (jpg, png, heic ...)")
    p.add_argument("--date", required=True, help="촬영 연-월, 예: 2026-10")
    p.add_argument("--name", required=True, help="파일 이름 설명(영문 소문자·하이픈), 예: ksmcb-poster")
    p.add_argument("--en", required=True, help="영문 캡션")
    p.add_argument("--ko", required=True, help="한국어 캡션")
    p.add_argument("--alt", help="영문 사진 설명(접근성). 생략하면 영문 캡션을 씀")
    p.add_argument("--commit", action="store_true", help="git add + commit 까지")
    p.add_argument("--yes", action="store_true", help="공개 동의 확인 질문 건너뛰기")
    p.add_argument("--dry-run", action="store_true", help="바꾸지 않고 계획만 출력")
    a = p.parse_args()

    if not re.fullmatch(r"20\d\d-(0[1-9]|1[0-2])", a.date):
        sys.exit("--date 는 2026-10 같은 형식이어야 합니다.")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.name):
        sys.exit("--name 은 영문 소문자·숫자·하이픈만 씁니다. 예: ksmcb-poster")
    for f in a.photos:
        if not os.path.isfile(f):
            sys.exit(f"파일이 없습니다: {f}")

    s = io.open(INDEX, encoding="utf-8").read()
    if s.count(ANCHOR) != 1:
        sys.exit("index.html 에서 '여기부터 사진 목록' 주석을 찾지 못했습니다.")

    base = f"{a.date}-{a.name}"
    multi = len(a.photos) > 1
    plan, taken = [], set()
    for i, src in enumerate(a.photos, 1):
        stem = f"{base}-{i}" if multi else base
        fn = unique_name(stem)
        while fn in taken:  # 같은 실행 안에서 겹침 방지
            stem += "-x"
            fn = unique_name(stem)
        taken.add(fn)
        plan.append((src, fn))

    print("추가할 사진:")
    for src, fn in plan:
        print(f"  {os.path.basename(src)}  →  assets/{fn}")
    print(f"  캡션(en): {a.en}\n  캡션(ko): {a.ko}")
    if a.dry_run:
        print("(--dry-run: 아무것도 바꾸지 않았습니다)")
        return

    if not a.yes:
        ans = input("사람이 나온 사진이면 본인들의 공개 동의를 받았나요? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            sys.exit("중단했습니다. 동의를 확인한 뒤 다시 실행하세요.")

    os.makedirs(ASSETS, exist_ok=True)
    blocks = ""
    for src, fn in plan:
        size = resize(src, os.path.join(ASSETS, fn))
        print(f"  저장: assets/{fn}" + (f"  ({size[0]}×{size[1]})" if size else ""))
        blocks += figure_block(fn, a.alt or a.en, a.en, a.ko)

    s = s.replace(ANCHOR, ANCHOR + blocks, 1)
    io.open(INDEX, "w", encoding="utf-8").write(s)
    print("index.html 에 추가했습니다. 미리보기: python3 scripts/serve.py")

    if a.commit:
        files = ["index.html"] + [os.path.join("assets", fn) for _, fn in plan]
        subprocess.run(["git", "-C", ROOT, "add", "--"] + files, check=True)
        n = len(plan)
        msg = f"content: 사진 {n}장 추가 — {a.ko}" if n > 1 else f"content: 사진 추가 — {a.ko}"
        subprocess.run(["git", "-C", ROOT, "commit", "-q", "-m", msg], check=True)
        print(f"커밋했습니다: {msg}\n이제 `git push` 하세요.")
    else:
        print("확인 후: git add index.html assets/ && git commit -m 'content: 사진 추가' && git push")


if __name__ == "__main__":
    main()

/* ============================================================
   PRISM Group — interactions: language toggle + mobile nav
   ============================================================ */
(function () {
  "use strict";

  var STORAGE_KEY = "prism-lang";

  /* ---------- Language toggle ---------- */
  function applyLang(lang) {
    var isKo = lang === "ko";
    document.documentElement.lang = isKo ? "ko" : "en";
    document.body.classList.toggle("lang-ko", isKo);
    document.body.classList.toggle("lang-en", !isKo);

    // Swap text content for every bilingual element
    var nodes = document.querySelectorAll("[data-en][data-ko]");
    for (var i = 0; i < nodes.length; i++) {
      var el = nodes[i];
      var val = isKo ? el.getAttribute("data-ko") : el.getAttribute("data-en");
      if (val !== null) el.innerHTML = val;
    }

    // Update the switch UI
    var opts = document.querySelectorAll(".lang-switch__opt");
    for (var j = 0; j < opts.length; j++) {
      opts[j].classList.toggle("is-active", opts[j].getAttribute("data-lang") === lang);
    }
  }

  function initLang() {
    var saved = null;
    try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) {}
    // 기본은 항상 영어. 방문자가 스위치로 한국어를 고른 경우에만 그 선택을 기억합니다.
    applyLang(saved === "ko" ? "ko" : "en");

    var sw = document.getElementById("langSwitch");
    if (sw) {
      sw.addEventListener("click", function () {
        var next = document.body.classList.contains("lang-ko") ? "en" : "ko";
        applyLang(next);
        try { localStorage.setItem(STORAGE_KEY, next); } catch (e) {}
      });
    }
  }

  /* ---------- Mobile nav ---------- */
  function initNav() {
    var toggle = document.getElementById("navToggle");
    var links = document.getElementById("navLinks");
    if (!toggle || !links) return;

    toggle.addEventListener("click", function () {
      links.classList.toggle("is-open");
    });

    // Close menu after tapping a link
    var anchors = links.querySelectorAll("a");
    for (var i = 0; i < anchors.length; i++) {
      anchors[i].addEventListener("click", function () {
        links.classList.remove("is-open");
      });
    }
  }

  /* ---------- Collapse long lists (publications / news) ---------- */
  /* 목록이 limit 보다 길면 나머지를 감추고 토글 버튼을 붙입니다.
     버튼이 이미 있으면(논문 — 생성기가 만들어 둠) 그것을 그대로 씁니다.
     없으면(소식 — 손으로 편집) 새로 만들어 목록 뒤에 넣습니다. */
  function setupCollapse(o) {
    var list = document.getElementById(o.listId);
    if (!list) return;

    var items = list.querySelectorAll(o.itemSelector);
    var hidden = items.length - o.limit;
    var btn = document.getElementById(o.btnId);

    if (hidden <= 0) {
      if (btn && btn.parentNode) btn.parentNode.removeChild(btn);
      return;
    }

    for (var i = o.limit; i < items.length; i++) {
      items[i].classList.add(o.extraClass);
    }

    if (!btn) {
      btn = document.createElement("button");
      btn.id = o.btnId;
      btn.type = "button";
      btn.className = "list-toggle";
      btn.innerHTML =
        '<span class="list-toggle__more" data-en="' + o.moreEn.replace("{n}", hidden) +
        '" data-ko="' + o.moreKo.replace("{n}", hidden) + '">' +
        o.moreEn.replace("{n}", hidden) + "</span>" +
        '<span class="list-toggle__less" data-en="Show fewer" data-ko="접기">Show fewer</span>';
      list.insertAdjacentElement("afterend", btn);
    }

    btn.setAttribute("aria-expanded", "false");
    btn.addEventListener("click", function () {
      var open = list.classList.toggle("is-expanded");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
      // 접을 때는 목록 상단으로 되돌려 스크롤 위치를 잃지 않게 함
      if (!open) {
        var top = list.getBoundingClientRect().top + window.pageYOffset - 90;
        window.scrollTo({ top: top, behavior: "smooth" });
      }
    });
  }

  function initCollapse() {
    setupCollapse({
      listId: "pubsList", itemSelector: ".pcard", limit: 5,
      extraClass: "pcard--extra", btnId: "pubsToggle",
      moreEn: "Show {n} more papers", moreKo: "논문 {n}편 더 보기"
    });
    setupCollapse({
      listId: "newsList", itemSelector: ".news__item", limit: 5,
      extraClass: "news__item--extra", btnId: "newsToggle",
      moreEn: "Show {n} more", moreKo: "{n}건 더 보기"
    });
  }

  /* ---------- Empty states: 항목이 생기면 안내 문구를 치움 ---------- */
  function initEmptyStates() {
    [
      { listId: "photoGrid", emptyId: "photoEmpty", itemSelector: ".photo" },
      { listId: "newsList", emptyId: "newsEmpty", itemSelector: ".news__item" },
      { listId: "codeList", emptyId: "codeEmpty", itemSelector: ".pcard" }
    ].forEach(function (o) {
      var list = document.getElementById(o.listId);
      var empty = document.getElementById(o.emptyId);
      if (!list || !empty) return;
      if (list.querySelector(o.itemSelector)) empty.parentNode.removeChild(empty);
    });
  }

  /* ---------- 사진 확대 (라이트박스) ---------- */
  /* 사진을 클릭하면 원본을 크게 보여 줍니다.
     · 닫기: 바깥 클릭 · Esc · 오른쪽 위 X
     · 넘기기: 좌우 화살표 버튼 · 키보드 ← →
     사진을 추가할 때 따로 손댈 것은 없습니다. figure 블록만 넣으면 자동으로 잡힙니다. */
  function initLightbox() {
    var figs = [].slice.call(document.querySelectorAll("#photoGrid .photo"));
    if (!figs.length) return;

    var SVG = {
      close: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>',
      prev:  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg>',
      next:  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg>'
    };

    var box = document.createElement("div");
    box.className = "lb";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Photo viewer");
    box.innerHTML =
      '<button class="lb__btn lb__close" type="button" aria-label="Close">' + SVG.close + "</button>" +
      '<button class="lb__btn lb__prev" type="button" aria-label="Previous photo">' + SVG.prev + "</button>" +
      '<button class="lb__btn lb__next" type="button" aria-label="Next photo">' + SVG.next + "</button>" +
      '<img class="lb__img" alt="">' +
      '<p class="lb__cap"></p>' +
      '<p class="lb__count"></p>';
    document.body.appendChild(box);

    var img     = box.querySelector(".lb__img");
    var capEl   = box.querySelector(".lb__cap");
    var countEl = box.querySelector(".lb__count");
    var btnClose = box.querySelector(".lb__close");
    var btnPrev  = box.querySelector(".lb__prev");
    var btnNext  = box.querySelector(".lb__next");
    var idx = 0;
    var lastFocus = null;

    // 사진이 하나뿐이면 좌우 버튼은 의미가 없습니다.
    if (figs.length < 2) {
      btnPrev.style.display = "none";
      btnNext.style.display = "none";
    }

    function show(i) {
      idx = (i + figs.length) % figs.length;
      var fig = figs[idx];
      var src = fig.querySelector("img");
      var cap = fig.querySelector("figcaption");

      img.setAttribute("src", src.getAttribute("src"));
      img.setAttribute("alt", src.getAttribute("alt") || "");

      // 캡션의 data-en / data-ko 를 그대로 물려받아, 언어 스위치가 라이트박스에도 먹게 합니다.
      capEl.removeAttribute("data-en");
      capEl.removeAttribute("data-ko");
      if (cap) {
        var en = cap.getAttribute("data-en");
        var ko = cap.getAttribute("data-ko");
        if (en !== null && ko !== null) {
          capEl.setAttribute("data-en", en);
          capEl.setAttribute("data-ko", ko);
        }
        capEl.innerHTML = cap.innerHTML;
      } else {
        capEl.textContent = "";
      }

      countEl.textContent = figs.length > 1 ? (idx + 1) + " / " + figs.length : "";
    }

    function open(i) {
      lastFocus = document.activeElement;
      show(i);
      box.classList.add("is-open");
      document.body.classList.add("lb-open");
      btnClose.focus();
    }

    function close() {
      box.classList.remove("is-open");
      document.body.classList.remove("lb-open");
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }

    function isOpen() { return box.classList.contains("is-open"); }

    figs.forEach(function (fig, i) {
      var cap = fig.querySelector("figcaption");
      fig.setAttribute("tabindex", "0");
      fig.setAttribute("role", "button");
      fig.setAttribute("aria-label", (cap ? cap.textContent.trim() + " — " : "") + "Enlarge");
      fig.addEventListener("click", function () { open(i); });
      fig.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " " || e.key === "Spacebar") {
          e.preventDefault();
          open(i);
        }
      });
    });

    btnClose.addEventListener("click", close);
    btnPrev.addEventListener("click", function (e) { e.stopPropagation(); show(idx - 1); });
    btnNext.addEventListener("click", function (e) { e.stopPropagation(); show(idx + 1); });
    // 사진·버튼이 아닌 배경을 눌렀을 때만 닫습니다.
    box.addEventListener("click", function (e) { if (e.target === box) close(); });

    document.addEventListener("keydown", function (e) {
      if (!isOpen()) return;
      if (e.key === "Escape") { close(); }
      else if (e.key === "ArrowLeft" && figs.length > 1) { show(idx - 1); }
      else if (e.key === "ArrowRight" && figs.length > 1) { show(idx + 1); }
    });

    // 열려 있는 동안 초점이 뒤 페이지로 새어 나가지 않게 합니다.
    document.addEventListener("focusin", function (e) {
      if (isOpen() && !box.contains(e.target)) btnClose.focus();
    });
  }

  /* ---------- 비어 있는 섹션 감추기 ---------- */
  /* 항목이 하나도 없는 섹션은 본문과 상단 메뉴 링크를 함께 감춥니다.
     첫 항목을 넣는 순간 자동으로 다시 나타납니다. 손댈 것이 없습니다.
     다시 항상 보이게 하려면 아래 배열에서 해당 줄만 지우면 됩니다. */
  function initHideEmptySections() {
    [
      { sectionId: "code", itemSelector: ".pcard" }
    ].forEach(function (o) {
      var sec = document.getElementById(o.sectionId);
      if (!sec || sec.querySelector(o.itemSelector)) return;
      sec.style.display = "none";
      var link = document.querySelector('.nav__links a[href="#' + o.sectionId + '"]');
      if (link) link.style.display = "none";
    });
  }

  /* ---------- Footer year ---------- */
  function initYear() {
    var y = document.getElementById("year");
    if (y) y.textContent = new Date().getFullYear();
  }

  document.addEventListener("DOMContentLoaded", function () {
    // initLang() 은 마지막에 — 위에서 새로 만든 버튼까지 언어가 적용되도록
    initNav();
    initCollapse();
    initEmptyStates();
    initHideEmptySections();
    initLightbox();
    initLang();
    initYear();
  });
})();

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
    initLang();
    initYear();
  });
})();

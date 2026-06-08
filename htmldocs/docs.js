/* ============================================================
   finvizfinance docs — interactive chrome
   Injects topbar, theme toggle, copy buttons, right-hand TOC,
   scroll-spy, sidebar filter, and mobile menu.
   ============================================================ */
(function () {
  "use strict";

  /* ---------- Theme ---------- */
  var THEME_KEY = "fvf-theme";
  function getStoredTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }
  function systemTheme() {
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function applyTheme(t) {
    document.documentElement.setAttribute("data-theme", t);
    var btn = document.getElementById("themeToggle");
    if (btn) btn.innerHTML = t === "dark" ? SUN : MOON;
  }
  // Set early (also done inline in <head> to avoid flash, but safe here too)
  applyTheme(getStoredTheme() || systemTheme());

  /* ---------- Icons ---------- */
  var SUN  = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
  var MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>';
  var MENU = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg>';
  var GH   = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 .5C5.7.5.5 5.7.5 12c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.2.8-.5v-2c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.3-1.7-1.3-1.7-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.7 1.3 3.4 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17.3 4.8 18.3 5.1 18.3 5.1c.6 1.6.2 2.8.1 3.1.8.8 1.2 1.8 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.3c0 .3.2.6.8.5 4.6-1.5 7.9-5.8 7.9-10.9C23.5 5.7 18.3.5 12 .5z"/></svg>';
  var SEARCH = '<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>';
  var COPY = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h10"/></svg>';
  var CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>';

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var layout = document.querySelector(".layout");
    var sidebar = document.querySelector(".sidebar");
    var content = document.querySelector(".content");

    /* ---------- Top bar ---------- */
    var ver = (sidebar && sidebar.querySelector(".brand .ver")) ;
    var verText = ver ? ver.textContent.replace("API Reference · ", "") : "v1.3.0";
    var topbar = document.createElement("header");
    topbar.className = "topbar";
    topbar.innerHTML =
      '<button class="tb-btn tb-hamburger" id="menuToggle" aria-label="Menu">' + MENU + '</button>' +
      '<a class="tb-brand" href="index.html">' +
        '<span class="tb-logo">finviz<span class="dot">finance</span></span>' +
        '<span class="tb-ver">' + verText + '</span>' +
      '</a>' +
      '<div class="tb-spacer"></div>' +
      '<label class="tb-search" for="navFilter">' + SEARCH +
        '<input id="navFilter" type="text" placeholder="Filter…" autocomplete="off" spellcheck="false">' +
        '<kbd>/</kbd>' +
      '</label>' +
      '<button class="tb-btn" id="themeToggle" aria-label="Toggle theme"></button>' +
      '<a class="tb-btn" href="https://github.com/lit26/finvizfinance" target="_blank" rel="noopener" aria-label="GitHub">' + GH + '</a>';
    document.body.insertBefore(topbar, document.body.firstChild);
    applyTheme(document.documentElement.getAttribute("data-theme"));

    document.getElementById("themeToggle").addEventListener("click", function () {
      var next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(next);
      try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
    });

    /* ---------- Mobile menu ---------- */
    var scrim = document.createElement("div");
    scrim.className = "scrim";
    document.body.appendChild(scrim);
    function closeMenu() { sidebar && sidebar.classList.remove("open"); scrim.classList.remove("show"); }
    var menuBtn = document.getElementById("menuToggle");
    if (menuBtn) menuBtn.addEventListener("click", function () {
      sidebar.classList.toggle("open"); scrim.classList.toggle("show");
    });
    scrim.addEventListener("click", closeMenu);
    if (sidebar) sidebar.addEventListener("click", function (e) {
      if (e.target.closest("a")) closeMenu();
    });

    /* ---------- Sidebar filter ---------- */
    var filter = document.getElementById("navFilter");
    if (filter && sidebar) {
      filter.addEventListener("input", function () {
        var q = filter.value.trim().toLowerCase();
        sidebar.querySelectorAll(".nav-group").forEach(function (group) {
          var any = false;
          group.querySelectorAll("a").forEach(function (a) {
            var match = a.textContent.toLowerCase().indexOf(q) !== -1;
            a.classList.toggle("search-hidden", q && !match);
            if (match) any = true;
          });
          group.classList.toggle("search-hidden", q && !any);
        });
      });
      document.addEventListener("keydown", function (e) {
        if (e.key === "/" && document.activeElement !== filter &&
            !/input|textarea/i.test(document.activeElement.tagName)) {
          e.preventDefault(); filter.focus();
        }
        if (e.key === "Escape") { filter.value = ""; filter.dispatchEvent(new Event("input")); filter.blur(); }
      });
    }

    /* ---------- Copy buttons on code blocks ---------- */
    content && content.querySelectorAll("pre").forEach(function (pre) {
      var wrap = document.createElement("div");
      wrap.className = "code-block";
      var head = document.createElement("div");
      head.className = "code-head";
      head.innerHTML = '<span class="code-lang">python</span>' +
        '<button class="copy-btn" type="button">' + COPY + '<span>Copy</span></button>';
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(head);
      wrap.appendChild(pre);
      var btn = head.querySelector(".copy-btn");
      btn.addEventListener("click", function () {
        var text = pre.innerText;
        navigator.clipboard.writeText(text).then(function () {
          btn.classList.add("copied");
          btn.innerHTML = CHECK + '<span>Copied</span>';
          setTimeout(function () {
            btn.classList.remove("copied");
            btn.innerHTML = COPY + '<span>Copy</span>';
          }, 1600);
        });
      });
    });

    /* ---------- Heading anchors ---------- */
    function slug(t) { return t.toLowerCase().replace(/[^\w]+/g, "-").replace(/^-+|-+$/g, ""); }
    content && content.querySelectorAll("h2, h3").forEach(function (h) {
      if (!h.id) h.id = slug(h.textContent);
      var a = document.createElement("a");
      a.className = "anchor-link"; a.href = "#" + h.id; a.textContent = "#";
      a.setAttribute("aria-hidden", "true");
      h.appendChild(a);
    });

    /* ---------- Right-hand TOC + scroll-spy ---------- */
    var heads = content ? Array.prototype.slice.call(content.querySelectorAll("h2, h3")) : [];
    if (heads.length > 2 && layout) {
      var rail = document.createElement("nav");
      rail.className = "toc-rail";
      var inner = '<div class="toc-title">On this page</div>';
      heads.forEach(function (h) {
        var label = h.textContent.replace(/#$/, "").trim();
        inner += '<a href="#' + h.id + '" class="' + (h.tagName === "H3" ? "toc-h3" : "") + '" data-id="' + h.id + '">' + label + '</a>';
      });
      rail.innerHTML = inner;
      layout.appendChild(rail);

      var links = {};
      rail.querySelectorAll("a").forEach(function (a) { links[a.getAttribute("data-id")] = a; });
      var current = null;
      var spy = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) {
            if (current) current.classList.remove("active");
            current = links[e.target.id];
            if (current) current.classList.add("active");
          }
        });
      }, { rootMargin: "-80px 0px -70% 0px", threshold: 0 });
      heads.forEach(function (h) { spy.observe(h); });
    }
  });
})();

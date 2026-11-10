/* ==========================================================================
   site.js: navigation, reveal-on-scroll, counters, spotlight cards,
   marquee, timeline progress, press lists, forms, preview banner.
   No dependencies. Everything fails visible: if anything throws, content
   is still shown.
   ========================================================================== */
(function () {
  'use strict';

  var CFG = window.KQC_CONFIG || {};
  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var root = document.documentElement;
  var depth = (document.body.getAttribute('data-depth') || '');   // '' or '../'

  function $(sel, ctx) { return (ctx || document).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
  function on(el, ev, fn, opts) { if (el) el.addEventListener(ev, fn, opts || false); }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  /* ------------------------------------------------------------------ */
  /* Header + navigation                                                 */
  /* ------------------------------------------------------------------ */
  function initNav() {
    var header = $('.site-header');
    var toggle = $('.menu-toggle');
    var mobile = $('.mobile-menu');
    var dropdowns = $$('.dropdown');

    function sync() {
      if (!header) return;
      header.classList.toggle('scrolled', window.scrollY > 24);
    }
    sync();
    on(window, 'scroll', sync, { passive: true });

    function closeAll(except) {
      dropdowns.forEach(function (d) { if (d !== except) { d.classList.remove('open'); var b = $('.nav-item', d); if (b) b.setAttribute('aria-expanded', 'false'); } });
    }
    dropdowns.forEach(function (d) {
      var trigger = $('.nav-item', d);
      if (!trigger) return;
      trigger.setAttribute('aria-haspopup', 'true');
      trigger.setAttribute('aria-expanded', 'false');
      on(trigger, 'click', function (e) {
        e.preventDefault();
        var open = d.classList.contains('open');
        closeAll(d);
        d.classList.toggle('open', !open);
        trigger.setAttribute('aria-expanded', String(!open));
      });
    });
    on(document, 'click', function (e) { if (!e.target.closest('.dropdown')) closeAll(); });
    on(document, 'keydown', function (e) {
      if (e.key === 'Escape') {
        closeAll();
        if (mobile && mobile.classList.contains('open')) setMobile(false);
      }
    });

    function setMobile(open) {
      if (!mobile || !toggle) return;
      mobile.classList.toggle('open', open);
      mobile.setAttribute('aria-hidden', String(!open));
      toggle.setAttribute('aria-expanded', String(open));
      toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
      document.body.style.overflow = open ? 'hidden' : '';
    }
    if (toggle && mobile) {
      $$('.mobile-group a', mobile).forEach(function (a, i) { a.style.setProperty('--i', i); });
      on(toggle, 'click', function () { setMobile(!mobile.classList.contains('open')); });
      $$('a', mobile).forEach(function (a) { on(a, 'click', function () { setMobile(false); }); });
      on(window, 'resize', function () { if (window.innerWidth > 1080) setMobile(false); });
    }

    // Mark the current page in the nav
    var path = location.pathname.split('/').pop() || 'index.html';
    $$('.nav-main a.nav-item, .dropdown-menu a').forEach(function (a) {
      var href = (a.getAttribute('href') || '').split('#')[0].split('/').pop();
      if (href && href === path) {
        a.classList.add('active');
        var dd = a.closest('.dropdown'); if (dd) { var t = $('.nav-item', dd); if (t) t.classList.add('active'); }
      }
    });
  }

  /* ------------------------------------------------------------------ */
  /* Reveal on scroll (fail visible)                                      */
  /* ------------------------------------------------------------------ */
  function initReveal() {
    var targets = $$('.reveal, [data-stagger]');
    $$('[data-stagger]').forEach(function (g) { $$(':scope > *', g).forEach(function (c, i) { c.style.setProperty('--i', i); }); });
    if (!targets.length) return;
    function show(el) { el.classList.add('in-view'); }
    if (reduceMotion || !('IntersectionObserver' in window)) { targets.forEach(show); return; }
    try {
      var io = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (en) { if (en.isIntersecting) { show(en.target); obs.unobserve(en.target); } });
      }, { threshold: 0, rootMargin: '0px 0px -8% 0px' });
      targets.forEach(function (el) { io.observe(el); });
    } catch (e) { targets.forEach(show); }
    // safety net: nothing stays hidden
    setTimeout(function () {
      targets.forEach(function (el) { if (!el.classList.contains('in-view') && el.getBoundingClientRect().top < window.innerHeight * 1.5) show(el); });
    }, 2500);
    setTimeout(function () { targets.forEach(show); }, 9000);
  }

  /* ------------------------------------------------------------------ */
  /* Count-up numbers: <span data-count="27" data-suffix="+">27+</span>   */
  /* ------------------------------------------------------------------ */
  function initCounters() {
    var els = $$('[data-count]');
    if (!els.length) return;
    function run(el) {
      var target = parseFloat(el.getAttribute('data-count')) || 0;
      var suffix = el.getAttribute('data-suffix') || '';
      var prefix = el.getAttribute('data-prefix') || '';
      var decimals = parseInt(el.getAttribute('data-decimals') || '0', 10);
      var plain = el.hasAttribute('data-plain');
      var dur = 1400, t0 = performance.now();
      function fmt(n) { return plain ? n.toFixed(decimals) : n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals }); }
      function frame(now) {
        var p = Math.min((now - t0) / dur, 1);
        var e = 1 - Math.pow(1 - p, 3);
        el.textContent = prefix + fmt(target * e) + suffix;
        if (p < 1) requestAnimationFrame(frame); else el.textContent = prefix + fmt(target) + suffix;
      }
      requestAnimationFrame(frame);
    }
    if (reduceMotion || !('IntersectionObserver' in window)) return; // static text already in markup
    var io = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (en) { if (en.isIntersecting) { run(en.target); obs.unobserve(en.target); } });
    }, { threshold: 0.4 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ------------------------------------------------------------------ */
  /* Spotlight cards: cursor-following highlight                          */
  /* ------------------------------------------------------------------ */
  function initSpotlight() {
    var cards = $$('.spot');
    if (!cards.length || !window.matchMedia('(hover: hover)').matches) return;
    cards.forEach(function (card) {
      on(card, 'pointermove', function (e) {
        var r = card.getBoundingClientRect();
        card.style.setProperty('--mx', ((e.clientX - r.left) / r.width * 100).toFixed(2) + '%');
        card.style.setProperty('--my', ((e.clientY - r.top) / r.height * 100).toFixed(2) + '%');
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Hero parallax on the qubit visual                                    */
  /* ------------------------------------------------------------------ */
  function initParallax() {
    var el = $('[data-parallax]');
    if (!el || reduceMotion || !window.matchMedia('(hover: hover)').matches) return;
    var hero = el.closest('.hero') || document.body;
    var rx = 0, ry = 0, tx = 0, ty = 0, raf = 0;
    function tick() {
      rx += (tx - rx) * 0.06; ry += (ty - ry) * 0.06;
      el.style.transform = 'rotateY(' + rx.toFixed(2) + 'deg) rotateX(' + (-ry).toFixed(2) + 'deg)';
      if (Math.abs(tx - rx) > 0.05 || Math.abs(ty - ry) > 0.05) raf = requestAnimationFrame(tick); else raf = 0;
    }
    on(hero, 'pointermove', function (e) {
      var r = hero.getBoundingClientRect();
      tx = ((e.clientX - r.left) / r.width - 0.5) * 16;
      ty = ((e.clientY - r.top) / r.height - 0.5) * 16;
      if (!raf) raf = requestAnimationFrame(tick);
    });
    on(hero, 'pointerleave', function () { tx = 0; ty = 0; if (!raf) raf = requestAnimationFrame(tick); });
  }

  /* ------------------------------------------------------------------ */
  /* Marquee tape: duplicate content until wide enough, set duration      */
  /* ------------------------------------------------------------------ */
  function initMarquee() {
    var tracks = $$('.tape-track');
    if (!tracks.length) return;
    tracks.forEach(function (track) {
      if (!track.dataset.base) track.dataset.base = track.innerHTML;
      function build() {
        var base = track.dataset.base;
        var container = track.parentElement;
        track.innerHTML = '<div class="tape-group">' + base + '</div>';
        var g = $('.tape-group', track);
        var guard = 0;
        while (g.scrollWidth < container.clientWidth + 80 && guard++ < 10) g.insertAdjacentHTML('beforeend', base);
        var html = g.innerHTML;
        track.innerHTML = '<div class="tape-group">' + html + '</div><div class="tape-group" aria-hidden="true">' + html + '</div>';
        var w = $('.tape-group', track).scrollWidth;
        var pxPerSec = parseFloat(track.getAttribute('data-speed')) || 48;
        track.style.setProperty('--tape-duration', Math.max(18, w / pxPerSec).toFixed(1) + 's');
      }
      build();
      var t; on(window, 'resize', function () { clearTimeout(t); t = setTimeout(build, 150); });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Timeline: rail fill + light up items as they pass the viewport       */
  /* ------------------------------------------------------------------ */
  function initTimeline() {
    var tl = $('.timeline');
    if (!tl) return;
    var rail = $('.rail', tl);
    var items = $$('.tl-item', tl);
    function update() {
      var r = tl.getBoundingClientRect();
      var mid = window.innerHeight * 0.55;
      var fill = Math.max(0, Math.min(1, (mid - r.top) / r.height));
      if (rail) rail.style.setProperty('--fill', (fill * 100).toFixed(2) + '%');
      items.forEach(function (it) { it.classList.toggle('lit', it.getBoundingClientRect().top < mid); });
    }
    update();
    on(window, 'scroll', update, { passive: true });
    on(window, 'resize', update);
  }

  /* ------------------------------------------------------------------ */
  /* Press lists (data from press-data.js)                                */
  /* ------------------------------------------------------------------ */
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  function fmtDate(iso, short) {
    var p = iso.split('-'); var m = MONTHS[parseInt(p[1], 10) - 1] || '';
    return (short ? m.slice(0, 3) : m) + ' ' + parseInt(p[2], 10) + ', ' + p[0];
  }
  function pressUrl(p) { return p.url ? p.url : depth + 'press/' + p.slug + '.html'; }
  function pressAttrs(p) { return p.url ? ' target="_blank" rel="noopener noreferrer"' : ''; }
  function typeLabel(t) { return t === 'media' ? 'In the News' : t === 'draft' ? 'Draft' : 'Press Release'; }

  function getPress() {
    var showDrafts = CFG.showDrafts || /[?&]drafts=1/.test(location.search);
    return (window.KQC_PRESS || []).filter(function (p) { return showDrafts || p.type !== 'draft'; })
      .sort(function (a, b) { return a.date < b.date ? 1 : -1; });
  }

  function cardHTML(p, i) {
    var latest = i === 0;
    return '<article class="press-card' + (latest ? ' featured' : '') + '">' +
      '<div class="meta-row">' + (latest ? '<span class="badge-latest">Latest</span>' : '') + '<span class="date">' + fmtDate(p.date, true) + '</span><span class="tag">' + esc(typeLabel(p.type)) + '</span></div>' +
      '<h3><a href="' + pressUrl(p) + '"' + pressAttrs(p) + '>' + esc(p.headline) + '</a></h3>' +
      '<p>' + esc(p.excerpt) + '</p>' +
      '<div class="foot"><span class="link">Read <span class="arr">→</span></span><span class="tag" style="color:var(--faint)">' + esc(p.tags[0] || '') + '</span></div>' +
      '</article>';
  }
  function rowHTML(p) {
    return '<article class="press-row">' +
      '<div class="date">' + fmtDate(p.date, true) + '<small>' + esc(typeLabel(p.type)) + (p.source_name ? ' · ' + esc(p.source_name) : '') + '</small></div>' +
      '<div><h3><a href="' + pressUrl(p) + '"' + pressAttrs(p) + '>' + esc(p.headline) + '</a></h3><p>' + esc(p.excerpt) + '</p>' +
      '<div class="tags">' + p.tags.map(function (t) { return '<span class="chip">' + esc(t) + '</span>'; }).join('') + '</div></div>' +
      '<span class="go">Read →</span></article>';
  }

  function initPress() {
    var list = getPress();
    var preview = $('#press-preview');
    if (preview) preview.innerHTML = list.slice(0, parseInt(preview.getAttribute('data-limit') || '3', 10)).map(cardHTML).join('') || '<div class="empty">No releases yet.</div>';

    var ir = $('#press-ir');
    if (ir) ir.innerHTML = list.slice(0, parseInt(ir.getAttribute('data-limit') || '5', 10)).map(rowHTML).join('') || '<div class="empty">No releases yet.</div>';

    var full = $('#press-list');
    if (full) {
      var filters = $('#press-filters');
      var years = []; list.forEach(function (p) { var y = p.date.slice(0, 4); if (years.indexOf(y) < 0) years.push(y); });
      var state = { type: 'all', year: 'all' };
      function render() {
        var out = list.filter(function (p) { return (state.type === 'all' || p.type === state.type) && (state.year === 'all' || p.date.slice(0, 4) === state.year); });
        full.innerHTML = out.map(rowHTML).join('') || '<div class="empty">No items match this filter.</div>';
        var count = $('#press-count'); if (count) count.textContent = out.length + ' item' + (out.length === 1 ? '' : 's');
      }
      if (filters) {
        filters.innerHTML =
          '<button class="filter-btn active" data-type="all">All</button>' +
          '<button class="filter-btn" data-type="release">Press releases</button>' +
          '<button class="filter-btn" data-type="media">In the news</button>' +
          '<span class="spacer"></span>' +
          '<button class="filter-btn active" data-year="all">All years</button>' +
          years.map(function (y) { return '<button class="filter-btn" data-year="' + y + '">' + y + '</button>'; }).join('');
        on(filters, 'click', function (e) {
          var b = e.target.closest('.filter-btn'); if (!b) return;
          if (b.hasAttribute('data-type')) { state.type = b.getAttribute('data-type'); $$('[data-type]', filters).forEach(function (x) { x.classList.toggle('active', x === b); }); }
          if (b.hasAttribute('data-year')) { state.year = b.getAttribute('data-year'); $$('[data-year]', filters).forEach(function (x) { x.classList.toggle('active', x === b); }); }
          render();
        });
      }
      render();
    }

    // "More news" on article pages: neighbours of the current slug
    var more = $('#press-more');
    if (more) {
      var cur = more.getAttribute('data-current');
      var others = list.filter(function (p) { return p.slug !== cur; }).slice(0, 3);
      more.innerHTML = others.map(function (p, i) { return cardHTML(p, -1); }).join('');
    }
  }

  /* ------------------------------------------------------------------ */
  /* Forms: progressive mailto fallback when no endpoint is configured    */
  /* ------------------------------------------------------------------ */
  function initForms() {
    var alerts = $('#alerts-form');
    if (alerts) {
      on(alerts, 'submit', function (e) {
        var email = $('input[type=email]', alerts);
        if (CFG.alertsEndpoint) return; // let the browser post to the endpoint
        e.preventDefault();
        var subject = encodeURIComponent('Investor email alerts sign-up');
        var body = encodeURIComponent('Please add ' + (email ? email.value : '') + ' to the KQC investor alert list.');
        location.href = 'mailto:' + (CFG.irEmail || 'support@kqchub.com') + '?subject=' + subject + '&body=' + body;
        var ok = $('.form-ok', alerts.parentElement); if (ok) ok.hidden = false;
      });
    }
    var contact = $('#contact-form');
    if (contact) {
      on(contact, 'submit', function (e) {
        if (CFG.contactEndpoint) return;
        e.preventDefault();
        var v = function (n) { var el = contact.elements[n]; return el ? el.value : ''; };
        var subject = encodeURIComponent('[' + v('inquiry') + '] ' + v('name') + (v('org') ? ' · ' + v('org') : ''));
        var body = encodeURIComponent(v('message') + '\n\n--\n' + v('name') + '\n' + v('email') + (v('org') ? '\n' + v('org') : ''));
        var cc = (CFG.contactCc && CFG.contactCc.length) ? '&cc=' + encodeURIComponent(CFG.contactCc.join(',')) : '';
        location.href = 'mailto:' + (CFG.irEmail || 'support@kqchub.com') + '?subject=' + subject + cc + '&body=' + body;
      });
    }
  }

  /* ------------------------------------------------------------------ */
  /* Preview banner on non-production hosts                               */
  /* ------------------------------------------------------------------ */
  function initPreviewBanner() {
    var bar = $('.preview-bar');
    if (!bar) return;
    var prod = (CFG.productionHosts || []).indexOf(location.hostname) >= 0;
    var dismissed = false;
    try { dismissed = sessionStorage.getItem('kqc-preview-dismissed') === '1'; } catch (e) {}
    if (CFG.hidePreviewBanner || prod || dismissed) return;
    bar.hidden = false;
    on($('button', bar), 'click', function () { bar.hidden = true; try { sessionStorage.setItem('kqc-preview-dismissed', '1'); } catch (e) {} });
  }

  /* ------------------------------------------------------------------ */
  /* Misc: external links, current year                                   */
  /* ------------------------------------------------------------------ */
  function initMisc() {
    $$('a[href^="http"]').forEach(function (a) {
      if (a.hostname !== location.hostname) { a.setAttribute('target', '_blank'); a.setAttribute('rel', 'noopener noreferrer'); }
    });
    $$('[data-current-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
  }

  function init() {
    var steps = [initNav, initReveal, initCounters, initSpotlight, initParallax, initMarquee, initTimeline, initPress, initForms, initPreviewBanner, initMisc];
    steps.forEach(function (fn) { try { fn(); } catch (e) { if (window.console) console.warn('[kqc] ' + fn.name + ' failed:', e); } });
    root.classList.add('js-ready');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true }); else init();
})();

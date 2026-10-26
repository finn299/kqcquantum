/* ==========================================================================
   field.js: "quantum field" hero background.
   Particles drift in a slow Keplerian disc around a focal point (the qubit
   visual) and link to near neighbours with faint lines, so the hero reads as
   an entangled lattice. Blue/cyan tints. DPR capped at 2, paused when the
   hero is off-screen or the tab is hidden, static frame under reduced motion.
   ========================================================================== */
(function () {
  'use strict';
  var canvas = document.getElementById('qfield');
  if (!canvas) return;
  var ctx = canvas.getContext('2d', { alpha: true });
  if (!ctx) return;

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W = 0, H = 0, dpr = 1, raf = 0, running = false;
  var particles = [];
  var focus = { x: 0, y: 0 };
  var LINK = 120;           // link distance (css px)
  var pointer = { x: -9999, y: -9999, active: false };

  function resize() {
    var r = canvas.getBoundingClientRect();
    W = Math.max(1, r.width); H = Math.max(1, r.height);
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(W * dpr); canvas.height = Math.floor(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    // focal point sits under the qubit visual on wide screens, centre on narrow
    focus.x = W > 1080 ? W * 0.72 : W * 0.5;
    focus.y = W > 1080 ? H * 0.5 : H * 0.28;
    seed();
  }

  function seed() {
    var count = Math.round(Math.min(150, Math.max(50, (W * H) / 12000)));
    particles = new Array(count).fill(0).map(function () {
      var angle = Math.random() * Math.PI * 2;
      var radius = 60 + Math.pow(Math.random(), 0.7) * Math.max(W, H) * 0.62;
      var cyan = Math.random() < 0.18;
      return {
        angle: angle,
        radius: radius,
        speed: (0.05 + Math.random() * 0.1) / Math.sqrt(radius / 60),   // slower further out
        size: 0.6 + Math.random() * 1.5,
        alpha: 0.18 + Math.random() * 0.55,
        wob: Math.random() * Math.PI * 2,
        wobAmp: 4 + Math.random() * 14,
        cyan: cyan,
        x: 0, y: 0
      };
    });
  }

  function step(t) {
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];
      p.angle += p.speed * 0.012;
      var wob = Math.sin(t * 0.0004 + p.wob) * p.wobAmp;
      var r = p.radius + wob;
      p.x = focus.x + Math.cos(p.angle) * r;
      p.y = focus.y + Math.sin(p.angle) * r * 0.46;   // flatten to a disc
      // gentle attraction to pointer
      if (pointer.active) {
        var dx = pointer.x - p.x, dy = pointer.y - p.y, d2 = dx * dx + dy * dy;
        if (d2 < 220 * 220) { var f = (1 - Math.sqrt(d2) / 220) * 14; p.x += dx / Math.sqrt(d2 + 1) * f; p.y += dy / Math.sqrt(d2 + 1) * f; }
      }
    }
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    // links via a coarse grid to keep it O(n)
    var cell = LINK, grid = {};
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];
      var key = Math.floor(p.x / cell) + ',' + Math.floor(p.y / cell);
      (grid[key] = grid[key] || []).push(i);
    }
    ctx.lineWidth = 1;
    for (var j = 0; j < particles.length; j++) {
      var a = particles[j];
      var gx = Math.floor(a.x / cell), gy = Math.floor(a.y / cell);
      for (var ox = -1; ox <= 1; ox++) for (var oy = -1; oy <= 1; oy++) {
        var bucket = grid[(gx + ox) + ',' + (gy + oy)];
        if (!bucket) continue;
        for (var k = 0; k < bucket.length; k++) {
          var idx = bucket[k]; if (idx <= j) continue;
          var b = particles[idx];
          var dx = a.x - b.x, dy = a.y - b.y, d = Math.sqrt(dx * dx + dy * dy);
          if (d < LINK) {
            var al = (1 - d / LINK) * 0.16;
            ctx.strokeStyle = 'rgba(122,160,255,' + al.toFixed(3) + ')';
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
          }
        }
      }
    }
    for (var n = 0; n < particles.length; n++) {
      var q = particles[n];
      ctx.beginPath();
      ctx.arc(q.x, q.y, q.size, 0, Math.PI * 2);
      ctx.fillStyle = q.cyan ? 'rgba(42,210,201,' + q.alpha.toFixed(3) + ')' : 'rgba(153,184,255,' + q.alpha.toFixed(3) + ')';
      ctx.fill();
      if (q.size > 1.7) { // soft glow on the larger ones
        ctx.beginPath(); ctx.arc(q.x, q.y, q.size * 3, 0, Math.PI * 2);
        ctx.fillStyle = q.cyan ? 'rgba(42,210,201,0.06)' : 'rgba(59,116,255,0.07)'; ctx.fill();
      }
    }
  }

  function loop(t) {
    if (!running) return;
    step(t || 0); draw();
    raf = requestAnimationFrame(loop);
  }
  function start() { if (running || reduce) return; running = true; raf = requestAnimationFrame(loop); }
  function stop() { running = false; if (raf) cancelAnimationFrame(raf); raf = 0; }

  resize();
  if (reduce) { step(0); draw(); }
  else {
    start();
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { en[0].isIntersecting ? start() : stop(); }, { threshold: 0.02 }).observe(canvas);
    }
    document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
    var hero = canvas.parentElement;
    hero.addEventListener('pointermove', function (e) { var r = canvas.getBoundingClientRect(); pointer.x = e.clientX - r.left; pointer.y = e.clientY - r.top; pointer.active = true; });
    hero.addEventListener('pointerleave', function () { pointer.active = false; });
  }
  var rt; window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(function () { resize(); if (reduce) { step(0); draw(); } }, 120); });
})();

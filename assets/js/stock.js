/* ==========================================================================
   stock.js: placeholder chart for the Stock Information page.
   Draws an empty, gridded price chart with a slow scanning beam. No market
   data is fabricated. When a quote vendor is connected, replace this file
   (or feed real series into drawSeries()).
   ========================================================================== */
(function () {
  'use strict';
  var canvas = document.getElementById('stock-chart');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var W = 0, H = 0, dpr = 1, raf = 0, t0 = performance.now();

  function resize() {
    var r = canvas.getBoundingClientRect();
    W = r.width; H = r.height; dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(W * dpr); canvas.height = Math.floor(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function frame(now) {
    ctx.clearRect(0, 0, W, H);
    var padL = 56, padR = 20, padT = 20, padB = 34;
    var x0 = padL, x1 = W - padR, y0 = padT, y1 = H - padB;
    // grid
    ctx.strokeStyle = 'rgba(153,184,255,0.08)'; ctx.lineWidth = 1;
    ctx.font = '11px "JetBrains Mono", ui-monospace, monospace';
    ctx.fillStyle = 'rgba(133,147,187,0.7)'; ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
    var rows = 5;
    for (var i = 0; i <= rows; i++) {
      var y = y0 + (y1 - y0) * i / rows;
      ctx.beginPath(); ctx.moveTo(x0, y); ctx.lineTo(x1, y); ctx.stroke();
      ctx.fillText('·', x0 - 12, y);
    }
    ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    var cols = Math.max(4, Math.floor((x1 - x0) / 110));
    for (var c = 0; c <= cols; c++) {
      var x = x0 + (x1 - x0) * c / cols;
      ctx.beginPath(); ctx.moveTo(x, y0); ctx.lineTo(x, y1); ctx.stroke();
      ctx.fillText('·', x, y1 + 10);
    }
    // axes
    ctx.strokeStyle = 'rgba(153,184,255,0.22)';
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0, y1); ctx.lineTo(x1, y1); ctx.stroke();
    // baseline dotted "awaiting data" line
    ctx.setLineDash([3, 6]); ctx.strokeStyle = 'rgba(59,116,255,0.45)';
    var ym = (y0 + y1) / 2;
    ctx.beginPath(); ctx.moveTo(x0, ym); ctx.lineTo(x1, ym); ctx.stroke(); ctx.setLineDash([]);
    // scanning beam
    if (!reduce) {
      var p = ((now - t0) % 5200) / 5200;
      var bx = x0 + (x1 - x0) * p;
      var g = ctx.createLinearGradient(bx - 90, 0, bx + 10, 0);
      g.addColorStop(0, 'rgba(59,116,255,0)'); g.addColorStop(1, 'rgba(59,116,255,0.18)');
      ctx.fillStyle = g; ctx.fillRect(bx - 90, y0, 100, y1 - y0);
      ctx.strokeStyle = 'rgba(42,210,201,0.7)'; ctx.beginPath(); ctx.moveTo(bx, y0); ctx.lineTo(bx, y1); ctx.stroke();
      ctx.fillStyle = 'rgba(42,210,201,1)'; ctx.beginPath(); ctx.arc(bx, ym, 3, 0, Math.PI * 2); ctx.fill();
      raf = requestAnimationFrame(frame);
    }
  }

  resize(); frame(performance.now());
  window.addEventListener('resize', function () { resize(); if (reduce) frame(performance.now()); });
  document.addEventListener('visibilitychange', function () { if (document.hidden) cancelAnimationFrame(raf); else if (!reduce) raf = requestAnimationFrame(frame); });
})();

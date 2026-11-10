/* Visit counting for kqcquantum.com (JP, Oct 20 2026): page views, document downloads and webcast clicks are
   sent to a Google Apps Script web app owned by the IR team, which writes them to a Google Sheet. No cookies and
   no third-party tracker: a random visitor id is kept in this browser's localStorage so repeat visits can be told
   apart, and nothing identifying is collected (no IP address, no name, no email).
   Counts only on the production hosts and only when KQC_CONFIG.analyticsEndpoint is set. */
(function () {
  var CFG = window.KQC_CONFIG || {};
  var URL_ = CFG.analyticsEndpoint;
  var host = location.hostname.replace(/^www\./, '');
  var prod = (CFG.productionHosts || []).some(function (h) { return h.replace(/^www\./, '') === host; });
  if (!URL_ || !prod || navigator.webdriver || /bot|crawl|spider|slurp|preview|headless/i.test(navigator.userAgent)) return;
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl) return;

  function rid() { return Math.random().toString(36).slice(2, 10) + Date.now().toString(36).slice(-4); }
  function kept(store, key) {
    try { var v = store.getItem(key); if (!v) { v = rid(); store.setItem(key, v); return [v, true]; } return [v, false]; }
    catch (e) { return [rid(), true]; }
  }
  var visitor = kept(window.localStorage, 'kqc_vid'), session = kept(window.sessionStorage, 'kqc_sid');
  var w = window.innerWidth || 0;
  var device = /iPad|Tablet/i.test(navigator.userAgent) || (w >= 600 && w < 1024 && 'ontouchstart' in window) ? 'tablet' : (w < 600 ? 'mobile' : 'desktop');
  var tz = ''; try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
  var ref = '';
  try { if (document.referrer && new URL(document.referrer).hostname.replace(/^www\./, '') !== host) ref = new URL(document.referrer).hostname; } catch (e) {}
  var q = new URLSearchParams(location.search);

  function send(type, target) {
    var data = {
      type: type, path: location.pathname || '/', title: document.title.slice(0, 120), target: target || '',
      ref: ref, utm: q.get('utm_source') || '', visitor: visitor[0], newVisitor: visitor[1], session: session[0],
      newSession: session[1], device: device, tz: tz, lang: (navigator.language || '').slice(0, 10)
    };
    var body = JSON.stringify(data);
    try {
      if (navigator.sendBeacon && navigator.sendBeacon(URL_, new Blob([body], { type: 'text/plain' }))) return;
    } catch (e) {}
    try { fetch(URL_, { method: 'POST', mode: 'no-cors', keepalive: true, body: body, headers: { 'Content-Type': 'text/plain' } }); } catch (e) {}
  }

  send('pageview');
  visitor[1] = false; session[1] = false;

  // documents (the presentation, the transcript) and the webcast link, counted when clicked
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (/\.pdf($|\?)/i.test(href)) send('download', href.split('/').pop().split('?')[0]);
    else if (/netroadshow\.com/i.test(href)) send('webcast', 'NetRoadshow');
    else if (/businesswire\.com/i.test(href)) send('outbound', 'Business Wire');
    else if (/sec\.gov/i.test(href)) send('outbound', 'SEC EDGAR');
  }, true);
})();

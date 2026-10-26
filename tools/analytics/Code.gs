/**
 * KQC Quantum investor site: visit log (JP, Oct 20 2026).
 *
 * Bound to the Google Sheet "KQC Quantum IR site visits". The website sends each page view, document download
 * and webcast click here (assets/js/analytics.js); each one becomes a row on the Visits tab, and the Summary tab
 * adds them up. No IP addresses, names or emails are received or stored.
 *
 * Setup, once: Extensions > Apps Script, paste this file, run setup() and allow access, then
 * Deploy > New deployment > Web app, Execute as: Me, Who has access: Anyone. Put the /exec URL in
 * assets/js/config.js as analyticsEndpoint.
 */

var VISITS = 'Visits';
var SUMMARY = 'Summary';
var HEADERS = ['Time (PT)', 'Type', 'Page', 'Title', 'Target', 'Referrer', 'Campaign', 'Visitor', 'New visitor',
               'Session', 'New session', 'Device', 'Time zone', 'Language'];
var TYPES = { pageview: 1, download: 1, webcast: 1, outbound: 1 };

function doPost(e) {
  var d;
  try { d = JSON.parse((e && e.postData && e.postData.contents) || '{}'); } catch (err) { return out_('bad'); }
  if (!d || !TYPES[d.type]) return out_('bad');
  var clip = function (v, n) { return String(v == null ? '' : v).replace(/[\r\n\t]/g, ' ').slice(0, n); };
  var row = [new Date(), d.type, clip(d.path, 200), clip(d.title, 120), clip(d.target, 120), clip(d.ref, 120),
             clip(d.utm, 60), clip(d.visitor, 24), d.newVisitor ? 'yes' : '', clip(d.session, 24),
             d.newSession ? 'yes' : '', clip(d.device, 10), clip(d.tz, 40), clip(d.lang, 10)];
  var lock = LockService.getScriptLock();
  lock.waitLock(5000);
  try {
    var sh = SpreadsheetApp.getActive().getSheetByName(VISITS) || setup();
    sh.appendRow(row);
  } finally {
    lock.releaseLock();
  }
  return out_('ok');
}

function doGet() { return out_('KQC visit log is running'); }

function out_(s) { return ContentService.createTextOutput(s).setMimeType(ContentService.MimeType.TEXT); }

/** Builds the Visits and Summary tabs. Safe to run again: it only adds what is missing and rewrites the Summary. */
function setup() {
  var ss = SpreadsheetApp.getActive();
  ss.setSpreadsheetTimeZone('America/Los_Angeles');
  var v = ss.getSheetByName(VISITS) || ss.insertSheet(VISITS);
  if (v.getLastRow() === 0) v.appendRow(HEADERS);
  v.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold').setBackground('#0b1530').setFontColor('#ffffff');
  v.setFrozenRows(1);
  v.getRange('A:A').setNumberFormat('yyyy-mm-dd hh:mm');
  v.setColumnWidth(1, 140); v.setColumnWidth(3, 260); v.setColumnWidth(4, 260);

  var s = ss.getSheetByName(SUMMARY) || ss.insertSheet(SUMMARY, 0);
  s.clear();
  var V = VISITS + '!';
  var rows = [
    ['KQC Quantum investor site, kqcquantum.com', ''],
    ['Counted from the day tracking went live. Updates as visits arrive.', ''],
    ['', ''],
    ['Totals', ''],
    ['Page views', '=COUNTIF(' + V + 'B2:B,"pageview")'],
    ['Unique visitors', '=IF(B5=0,0,COUNTUNIQUE(FILTER(' + V + 'H2:H,' + V + 'B2:B="pageview")))'],
    ['Visits (sessions)', '=COUNTIFS(' + V + 'B2:B,"pageview",' + V + 'K2:K,"yes")'],
    ['Document downloads', '=COUNTIF(' + V + 'B2:B,"download")'],
    ['Webcast clicks', '=COUNTIF(' + V + 'B2:B,"webcast")'],
    ['Page views, last 7 days', '=COUNTIFS(' + V + 'B2:B,"pageview",' + V + 'A2:A,">="&(TODAY()-6))'],
    ['Unique visitors, last 7 days', '=IF(B10=0,0,COUNTUNIQUE(FILTER(' + V + 'H2:H,' + V + 'B2:B="pageview",' + V + 'A2:A>=TODAY()-6)))']
  ];
  s.getRange(1, 1, rows.length, 2).setValues(rows);
  s.getRange('A1').setFontSize(14).setFontWeight('bold');
  s.getRange('A2').setFontColor('#66787f');
  s.getRange('A4').setFontWeight('bold');

  // tables, side by side from column D
  var tables = [
    ['D', 'By day', '=QUERY({ARRAYFORMULA(IF(' + V + 'A2:A="",,TO_DATE(INT(' + V + 'A2:A)))),' + V + 'B2:B,' + V + 'H2:H},"select Col1, count(Col2) where Col2=\'pageview\' group by Col1 order by Col1 desc label Col1 \'Day\', count(Col2) \'Page views\'",0)'],
    ['G', 'Top pages', '=QUERY(' + V + 'A2:N,"select C, count(B) where B=\'pageview\' group by C order by count(B) desc label C \'Page\', count(B) \'Views\'",0)'],
    ['J', 'Where visitors came from', '=QUERY(' + V + 'A2:N,"select F, count(B) where B=\'pageview\' and K=\'yes\' and F<>\'\' group by F order by count(B) desc label F \'Referrer\', count(B) \'Visits\'",0)'],
    ['M', 'Downloads and webcast', '=QUERY(' + V + 'A2:N,"select B, E, count(B) where B=\'download\' or B=\'webcast\' or B=\'outbound\' group by B, E order by count(B) desc label B \'Type\', E \'What\', count(B) \'Clicks\'",0)'],
    ['Q', 'Device', '=QUERY(' + V + 'A2:N,"select L, count(B) where B=\'pageview\' group by L order by count(B) desc label L \'Device\', count(B) \'Views\'",0)'],
    ['T', 'Visitor time zone (rough location)', '=QUERY(' + V + 'A2:N,"select M, count(B) where B=\'pageview\' and K=\'yes\' group by M order by count(B) desc label M \'Time zone\', count(B) \'Visits\'",0)']
  ];
  tables.forEach(function (t) {
    s.getRange(t[0] + '4').setValue(t[1]).setFontWeight('bold');
    s.getRange(t[0] + '5').setFormula(t[2]);
  });
  s.getRange('E5:E').setNumberFormat('0');
  s.getRange('D5:D').setNumberFormat('yyyy-mm-dd');
  s.setColumnWidth(1, 220); s.setColumnWidth(7, 220); s.setColumnWidth(10, 180); s.setColumnWidth(13, 120); s.setColumnWidth(14, 220); s.setColumnWidth(20, 200);
  s.setFrozenRows(2);
  var blank = ss.getSheetByName('Sheet1');
  if (blank && blank.getLastRow() === 0 && ss.getSheets().length > 2) ss.deleteSheet(blank);
  return v;
}

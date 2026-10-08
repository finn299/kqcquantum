/* Site configuration. Edit here, no build step needed for these values. */
window.KQC_CONFIG = {
  // Hostnames considered "production". On any other host (localhost, preview
  // deploys, GitHub Pages) a slim preview banner is shown at the bottom of the page.
  productionHosts: ['kqcquantum.com', 'www.kqcquantum.com'],

  // Set to true to hide the preview banner everywhere (e.g. once the site is approved).
  hidePreviewBanner: false,

  // Show draft press releases (type: "draft") in lists. Also togglable with ?drafts=1
  showDrafts: false,

  // Email-alert form endpoint. Leave empty to fall back to a mailto: handoff.
  alertsEndpoint: '',

  // Contact form endpoint (e.g. Formspree / your backend). Leave empty for mailto: fallback.
  contactEndpoint: '',

  // Mailboxes used by the mailto: fallbacks.
  irEmail: 'ir@kqcquantum.com',

  // Contact-page messages also go to the Blueshirt Group IR team (cc), per Blueshirt, Sep 29 2026.
  contactCc: ['cmammone@blueshirtgroup.com', 'spencer@blueshirtgroup.com', 'hilary@blueshirtgroup.com']
};

/* Cookie-consent banner handler */

(function () {
  const banner = document.getElementById('cookie-banner');
  const acceptBtn = document.getElementById('accept-cookies');
  const declineBtn = document.getElementById('decline-cookies');
  if (!banner) return;

  const consent = localStorage.getItem('cookieConsent');
  if (!consent) {
    banner.classList.remove('hidden');
  }

  const hideBanner = () => banner.classList.add('hidden');

  if (acceptBtn) {
    acceptBtn.addEventListener('click', () => {
      localStorage.setItem('cookieConsent', 'accepted');
      hideBanner();
    });
  }

  if (declineBtn) {
    declineBtn.addEventListener('click', () => {
      localStorage.setItem('cookieConsent', 'declined');
      hideBanner();
    });
  }
})();

// Site analytics.
//
// Cloudflare Web Analytics is cookieless, so it loads for everyone. Google
// Analytics sets cookies, so under UK law it only loads after the visitor clicks
// "Accept" on the banner. The choice is kept in localStorage; any element with
// data-cookie-settings reopens the banner so people can change their mind.
// Storage throws in private mode and when site data is blocked, so every access
// is guarded and the page works normally without it.
(function () {
  var GA_ID = 'G-ZXJW77W4R3';
  var CF_TOKEN = '58c78e07f40943419402248013a44a66'; // Cloudflare Web Analytics token for ainofluff.co.uk
  var KEY = 'ainofluff_analytics';

  function getChoice() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setChoice(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  if (CF_TOKEN) {
    var cf = document.createElement('script');
    cf.defer = true;
    cf.src = 'https://static.cloudflareinsights.com/beacon.min.js';
    cf.setAttribute('data-cf-beacon', JSON.stringify({ token: CF_TOKEN }));
    document.head.appendChild(cf);
  }

  var gaLoaded = false;
  function loadGA() {
    window['ga-disable-' + GA_ID] = false;
    if (gaLoaded) return;
    gaLoaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', GA_ID);
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_ID;
    document.head.appendChild(s);
  }

  function stopGA() {
    window['ga-disable-' + GA_ID] = true;
    var host = location.hostname;
    var domains = ['', host, '.' + host, '.' + host.replace(/^www\./, '')];
    document.cookie.split(';').forEach(function (c) {
      var name = c.split('=')[0].trim();
      if (name === '_ga' || name.indexOf('_ga_') === 0) {
        domains.forEach(function (d) {
          document.cookie = name + '=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/' + (d ? '; domain=' + d : '');
        });
      }
    });
  }

  var banner = null;
  function showBanner() {
    if (banner) { banner.style.display = 'block'; return; }
    banner = document.createElement('div');
    banner.setAttribute('role', 'region');
    banner.setAttribute('aria-label', 'Cookie choice');
    banner.style.cssText = 'position:fixed;left:16px;right:16px;bottom:16px;z-index:9999;max-width:520px;margin:0 auto;' +
      'background:#0F1117;color:#F5F5F0;border-radius:14px;padding:16px 18px;box-shadow:0 10px 30px rgba(0,0,0,.25);' +
      "font:15px/1.45 'Inter',system-ui,sans-serif";
    banner.innerHTML =
      '<p style="margin:0 0 12px;color:#F5F5F0;font-size:15px;line-height:1.45">Can ainofluff use Google Analytics cookies to count visits and see which pages ' +
      'are useful? It\'s optional, and the site works the same if you say no. ' +
      '<a href="/privacy.html#cookies" style="color:inherit;text-decoration:underline">Privacy policy</a></p>' +
      '<div style="display:flex;gap:10px;flex-wrap:wrap">' +
      '<button type="button" data-choice="granted">Accept</button>' +
      '<button type="button" data-choice="denied">Reject</button></div>';
    Array.prototype.forEach.call(banner.querySelectorAll('button'), function (b) {
      b.style.cssText = 'flex:1;min-width:120px;padding:9px 14px;border-radius:10px;border:1px solid #F5F5F0;' +
        'background:transparent;color:#F5F5F0;font:inherit;font-weight:600;cursor:pointer';
      b.addEventListener('click', function () {
        var v = b.getAttribute('data-choice');
        setChoice(v);
        if (v === 'granted') loadGA(); else stopGA();
        banner.style.display = 'none';
      });
    });
    document.body.appendChild(banner);
  }

  function init() {
    var choice = getChoice();
    if (choice === 'granted') loadGA();
    else if (choice !== 'denied') showBanner();
    document.addEventListener('click', function (e) {
      var t = e.target.closest && e.target.closest('[data-cookie-settings]');
      if (t) { e.preventDefault(); showBanner(); }
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();

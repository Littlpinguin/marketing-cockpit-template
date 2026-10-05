/* ==========================================================================
   offer.js · state of the offer, computed in the browser (optional engine)
   --------------------------------------------------------------------------
   The static HTML always shows the OPEN state. The real state (waiting list,
   closed) and the days left are computed here, from ONE configuration that
   the assembler writes at the top of the page:

     window.LANDING_CONFIG.offer = {
       state: "open" | "waitlist" | "closed",   // decided by a human
       closes_at: "2027-03-31T23:59:00+02:00",  // real closing date, or null
       after_close: "waitlist" | "closed"        // state once the date is past
     }

   Contract (attributes read in the markup):
     html[data-offer-state]            written: open | waitlist | closed
     [data-offer-show="open waitlist"] shown only in the listed states (the
                                       HTML marks non-open variants hidden)
     [data-offer-countdown]            text replaced by the days left, from
                                       data-many ("Clôture dans {n} jours"),
                                       data-one ("Clôture demain") and
                                       data-zero ("Clôture ce soir"). Without
                                       JavaScript the static text (a date)
                                       stays. Counted in days, never seconds.
     [data-offer-text-<state>]         textContent in that state
     [data-offer-href-<state>]         href in that state
     [data-offer-action-<state>]       form action in that state
     [data-offer-disabled-<state>]     disabled in that state
   Event: "landing:offer" on document (detail: { state, days }).
   ========================================================================== */
(function () {
  'use strict';
  if (window.__landingOffer) return;
  window.__landingOffer = true;

  var config = (window.LANDING_CONFIG && window.LANDING_CONFIG.offer) || {};
  var DAY = 86400000;

  function startOfDay(d) { return new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime(); }

  var now = new Date();
  var closes = config.closes_at ? new Date(config.closes_at) : null;
  if (closes && isNaN(closes.getTime())) closes = null;
  var state = config.state || 'open';
  if (state === 'open' && closes && now > closes) state = config.after_close || 'waitlist';
  var days = closes && state === 'open' ? Math.round((startOfDay(closes) - startOfDay(now)) / DAY) : null;

  function apply() {
    document.documentElement.setAttribute('data-offer-state', state);

    document.querySelectorAll('[data-offer-show]').forEach(function (el) {
      var states = el.getAttribute('data-offer-show').split(/\s+/);
      el.hidden = states.indexOf(state) === -1;
    });

    if (days !== null) {
      document.querySelectorAll('[data-offer-countdown]').forEach(function (el) {
        var tpl = days <= 0 ? el.getAttribute('data-zero')
          : days === 1 ? el.getAttribute('data-one')
          : el.getAttribute('data-many');
        if (tpl) el.textContent = tpl.replace('{n}', String(days));
      });
    }

    if (state !== 'open') {
      var attr = function (kind) { return 'data-offer-' + kind + '-' + state; };
      document.querySelectorAll('[' + attr('text') + ']').forEach(function (el) {
        el.textContent = el.getAttribute(attr('text'));
      });
      document.querySelectorAll('[' + attr('href') + ']').forEach(function (el) {
        el.setAttribute('href', el.getAttribute(attr('href')));
      });
      document.querySelectorAll('[' + attr('action') + ']').forEach(function (el) {
        el.setAttribute('action', el.getAttribute(attr('action')));
      });
      document.querySelectorAll('[' + attr('disabled') + ']').forEach(function (el) {
        el.disabled = true;
      });
    }

    document.dispatchEvent(new CustomEvent('landing:offer', { detail: { state: state, days: days } }));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', apply);
  else apply();
})();

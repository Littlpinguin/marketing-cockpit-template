/* ==========================================================================
   tracking.js · measurement relay of a landing page (GA4 / GTM dataLayer)
   --------------------------------------------------------------------------
   Turns the data-* hooks of the markup into analytics events, and passes the
   visit's UTM parameters on to the conversion. Sends nothing by itself: it
   only feeds window.dataLayer (or gtag), which the page's tag loads, or not.

   Configuration: window.LANDING_CONFIG.tracking, written by the assembler,
   which also writes the dataLayer initialisation in <head> (the page's
   declaration of measurement, read by qa-landing.py) unless mode is "off".
     mode   "datalayer" (default): dataLayer.push({ event, ...params })
            "gtm":   same push (a GTM container listens to it)
            "gtag":  gtag('event', name, params) (gtag.js loaded in <head>)
            "off":   nothing is sent (hooks stay in place for later)
     utm    true (default): UTM pass-through on, false: off
     page   page slug, sent as page_slug (default: body[data-page-slug])

   Events and their parameters (every event also carries page_slug and the
   visit's utm_source / utm_medium / utm_campaign / utm_content / utm_term
   when present):
     cta_click        click on an element with data-track="cta_click", or
                      with data-cta / data-cta-position and no data-track.
                      cta_position (data-cta-position), cta_label (visible
                      text, 80 chars), cta_primary (data-cta="primaire"),
                      link_url (href)
     generate_lead    valid submit of a form[data-track="generate_lead"]
                      (a form that forms.js refused carries data-invalid and
                      is not counted). form_id (form id), lead_source (page
                      slug)
     begin_checkout   submit of a form[data-track="begin_checkout"] (the
                      conversion ticket). value, currency, formula
     select_content   choice gate: content_type, content_id
     faq_open         a details[data-track="faq_open"] opened: question
     <any name>       any other data-track value on a link or button: pushed
                      on click under that name
   Extra parameters: every data-track-<name>="value" attribute on the tracked
   element is sent as <name>: value (dashes become underscores). A form may
   expose its current formula through a checked input[name="formule"] or
   [data-track-formula].

   UTM pass-through: utm_* (and gclid) of the landing URL are kept for the
   visit (sessionStorage) and appended to (a) every outbound conversion link
   (a[data-cta] or a[data-track] with an absolute http(s) href) and (b) every
   form[data-track] as hidden inputs. data-utm="off" on a link or form opts
   it out.
   ========================================================================== */
(function () {
  'use strict';
  if (window.__landingTracking) return;
  window.__landingTracking = true;

  var config = (window.LANDING_CONFIG && window.LANDING_CONFIG.tracking) || {};
  var mode = config.mode || 'datalayer';
  var UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'gclid'];

  // The page declares its measurement in <head> (the assembler writes the
  // dataLayer initialisation, and the GTM or gtag snippet when an id is set).
  // In "off" mode nothing is declared and nothing is created here.
  function layer() {
    if (!Array.isArray(window.dataLayer)) {
      var fresh = [];
      window.dataLayer = fresh;
    }
    return window.dataLayer;
  }

  function pageSlug() {
    return config.page || (document.body && document.body.getAttribute('data-page-slug')) || location.pathname;
  }

  /* ---- UTM of the visit ---- */
  var utm = {};
  try {
    var params = new URLSearchParams(location.search);
    var stored = JSON.parse(sessionStorage.getItem('landing_utm') || '{}');
    UTM_KEYS.forEach(function (k) {
      var v = params.get(k) || stored[k];
      if (v) utm[k] = v;
    });
    if (Object.keys(utm).length) sessionStorage.setItem('landing_utm', JSON.stringify(utm));
  } catch (e) { /* private mode, blocked storage: keep what the URL gives */ }

  function send(name, extra) {
    if (mode === 'off' || !name) return;
    var payload = { page_slug: pageSlug() };
    Object.keys(utm).forEach(function (k) { payload[k] = utm[k]; });
    Object.keys(extra || {}).forEach(function (k) {
      if (extra[k] !== undefined && extra[k] !== '') payload[k] = extra[k];
    });
    if (mode === 'gtag' && typeof window.gtag === 'function') {
      window.gtag('event', name, payload);
    } else {
      var obj = { event: name };
      Object.keys(payload).forEach(function (k) { obj[k] = payload[k]; });
      layer().push(obj);
    }
  }
  window.landingTrack = send;

  function extras(el) {
    var out = {};
    Array.prototype.forEach.call(el.attributes, function (a) {
      var m = a.name.match(/^data-track-(.+)$/);
      if (m) out[m[1].replace(/-/g, '_')] = a.value;
    });
    return out;
  }

  function label(el) {
    return (el.getAttribute('aria-label') || el.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 80);
  }

  /* ---- clicks ---- */
  document.addEventListener('click', function (e) {
    var el = e.target.closest && e.target.closest('[data-track], [data-cta], [data-cta-position]');
    if (!el || el.tagName === 'FORM' || el.tagName === 'DETAILS') return;
    // A submit button of a tracked form: the form's submit event counts.
    var form = el.form || null;
    if (form && form.hasAttribute('data-track') && (el.type === 'submit')) return;
    var name = el.getAttribute('data-track') || 'cta_click';
    var data = extras(el);
    if (name === 'cta_click') {
      data.cta_position = el.getAttribute('data-cta-position') || 'body';
      data.cta_label = label(el);
      data.cta_primary = /^(primaire|primary)$/i.test(el.getAttribute('data-cta') || '');
      if (el.tagName === 'A') data.link_url = el.getAttribute('href');
    }
    send(name, data);
  });

  /* ---- forms ---- */
  // Bubble phase: the form's own handler (forms.js) has validated it first,
  // and marked it data-invalid when it refused the submission.
  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.matches || !form.matches('form[data-track]')) return;
    if (form.hasAttribute('data-invalid')) return;
    var name = form.getAttribute('data-track');
    var data = extras(form);
    var checked = form.querySelector('input[name="formule"]:checked, input[name="formula"]:checked');
    if (checked) data.formula = checked.value;
    if (name === 'generate_lead') {
      data.form_id = form.id || '';
      data.lead_source = pageSlug();
    }
    if (name === 'begin_checkout' && checked && checked.getAttribute('data-price')) {
      data.value = Number(checked.getAttribute('data-price'));
    }
    send(name, data);
  });

  /* ---- FAQ ---- */
  document.addEventListener('toggle', function (e) {
    var d = e.target;
    if (!d || d.tagName !== 'DETAILS' || !d.open || d.getAttribute('data-track') !== 'faq_open') return;
    var s = d.querySelector('summary');
    send('faq_open', { question: s ? label(s) : '' });
  }, true);

  /* ---- UTM pass-through ---- */
  function passUtm() {
    if (config.utm === false || !Object.keys(utm).length) return;
    document.querySelectorAll('a[data-cta], a[data-track]').forEach(function (a) {
      if (a.getAttribute('data-utm') === 'off') return;
      var href = a.getAttribute('href') || '';
      if (!/^https?:\/\//i.test(href)) return;
      try {
        var url = new URL(href);
        Object.keys(utm).forEach(function (k) { if (!url.searchParams.has(k)) url.searchParams.set(k, utm[k]); });
        a.setAttribute('href', url.toString());
      } catch (err) { /* malformed href: leave it */ }
    });
    document.querySelectorAll('form[data-track]').forEach(function (form) {
      if (form.getAttribute('data-utm') === 'off') return;
      Object.keys(utm).forEach(function (k) {
        if (form.querySelector('input[type="hidden"][name="' + k + '"]')) return;
        var input = document.createElement('input');
        input.type = 'hidden';
        input.name = k;
        input.value = utm[k];
        form.appendChild(input);
      });
    });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', passUtm);
  else passUtm();
})();

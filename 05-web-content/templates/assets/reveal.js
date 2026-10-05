/* ==========================================================================
   reveal.js · the one reveal engine of a landing page
   --------------------------------------------------------------------------
   Contract (attributes read in the markup):
     [data-reveal-group]            a container; its [data-reveal] children
                                    enter together, 0.1 s apart, when the
                                    container's top reaches ~85 % of the
                                    viewport height.
     [data-reveal]                  an element that enters on its own (outside
                                    any group) or as part of its group.
                                    Values: "" or "up" (rise 32 px), "left",
                                    "right", "scale", "fade". Opacity and
                                    position only.
     [data-count]                   a number ("120", "1 900 €", "98 %") that
                                    counts up once, when it first comes into
                                    view from below the fold. Prefix, suffix
                                    and digit grouping are kept.
   Classes written:
     html.rv-on                     the engine started and motion is allowed:
                                    only then does base.css hide what waits.
     [data-reveal].is-in            entered (CSS transitions to the final
                                    state). --rv-i carries its rank in the
                                    group, for the stagger.
   Under prefers-reduced-motion, without IntersectionObserver, or without
   JavaScript: the engine does nothing, so everything is visible at once and
   counters show their final value. Elements inside a [hidden] part (the
   choice gate) enter when that part is revealed, never before.
   Events: none. No dependency. Runs once, whatever the number of sections.
   ========================================================================== */
(function () {
  'use strict';
  if (window.__landingReveal) return;
  window.__landingReveal = true;

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) return;

  var root = document.documentElement;
  root.classList.add('rv-on');

  var MAX_RANK = 8;

  function enter(target) {
    var items = target.hasAttribute('data-reveal-group')
      ? target.querySelectorAll('[data-reveal]')
      : [target];
    for (var i = 0; i < items.length; i++) {
      items[i].style.setProperty('--rv-i', String(Math.min(i, MAX_RANK)));
      items[i].classList.add('is-in');
    }
  }

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      observer.unobserve(entry.target);
      enter(entry.target);
    });
  }, { rootMargin: '0px 0px -15% 0px', threshold: 0 });

  document.querySelectorAll('[data-reveal-group]').forEach(function (group) {
    observer.observe(group);
  });
  document.querySelectorAll('[data-reveal]').forEach(function (el) {
    if (!el.parentElement || !el.parentElement.closest('[data-reveal-group]')) observer.observe(el);
  });

  /* ---- counters ---- */
  var COUNTABLE = /^(\D*?)(\d(?:[\d\s  .]*\d)?)(\D*)$/;
  function format(n, sample) {
    var sep = (sample.match(/\d([\s  .])\d{3}/) || [])[1];
    var s = String(Math.round(n));
    return sep ? s.replace(/\B(?=(\d{3})+(?!\d))/g, sep) : s;
  }
  var counters = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      counters.unobserve(entry.target);
      var el = entry.target;
      var m = (el.textContent || '').trim().match(COUNTABLE);
      if (!m) return;
      var target = parseInt(m[2].replace(/[^\d]/g, ''), 10);
      if (!isFinite(target)) return;
      var start = null;
      var DURATION = 1200;
      function frame(t) {
        if (start === null) start = t;
        var k = Math.min(1, (t - start) / DURATION);
        var eased = 1 - Math.pow(1 - k, 3);
        el.textContent = m[1] + format(target * eased, m[2]) + m[3];
        if (k < 1) window.requestAnimationFrame(frame);
      }
      window.requestAnimationFrame(frame);
    });
  }, { rootMargin: '0px 0px -12% 0px' });
  document.querySelectorAll('[data-count]').forEach(function (el) {
    // Already on screen at load: leave it at its value.
    if (el.getBoundingClientRect().top < window.innerHeight) return;
    counters.observe(el);
  });
})();

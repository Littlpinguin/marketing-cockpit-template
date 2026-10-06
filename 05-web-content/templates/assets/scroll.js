/* ==========================================================================
   scroll.js · scroll theatre helper (optional engine)
   --------------------------------------------------------------------------
   Pinned stages, scroll-driven progress, reading line and section junctions,
   all with position: sticky and CSS variables: no animation library, no pin
   of its own, nothing that runs while the page does not scroll.

   Classes on <html>:
     .sc-motion   motion allowed (prefers-reduced-motion: no-preference)
     .sc-pin      motion allowed AND viewport at least 1101 × 720 px: the
                  only case where a section pins (charter § 5). Sections
                  write their pinned layout under .sc-pin, so that without
                  JavaScript, on a small screen or in reduced motion, they
                  are plain readable lists.

   Contract (attributes read in the markup):
     [data-scroll-track]   a tall track (its pinned height is set by the
                           section's CSS under .sc-pin, from --steps). The
                           engine writes on it:
                             --p      progress 0..1 (pinned: through the
                                      track; not pinned: while it crosses the
                                      viewport; reduced motion: 1)
                             --steps  number of [data-step-item] inside
                             data-step  current step, 0-based (pinned only)
                           and inside it:
                             [data-step-item], [data-step-visual]
                                      data-active on the current one
                                      (pinned only; otherwise none, and the
                                      CSS shows them all)
                             [data-step-current]  text = step + 1
                           It dispatches "landing:step" on the track
                           (detail: { step, steps }) when the step changes.
     [data-rail]           a list whose line fills as the reading line (66 %
                           of the viewport) goes down it: --rail 0..1 on the
                           element, data-reached="true" on each
                           [data-milestone] whose centre has passed the line.
                           Reduced motion: --rail 1, every milestone reached.
     .reading-progress     3 px reading line at the top: --read 0..1 (shown
                           by base.css under .sc-pin only).
     [data-exit="fade"]    pinned layout only: --exit 0..1 as the section
                           leaves (base.css fades it out, no overlap).
     [data-enter="fade"|"curtain"]  pinned layout only: --enter 0..1 as the
                           section comes in (fade, or a dark band opening).
   No transition between the hero and the next section: never put
   data-exit on the hero.
   ========================================================================== */
(function () {
  'use strict';
  if (window.__landingScroll) return;
  window.__landingScroll = true;

  var root = document.documentElement;
  var mqMotion = window.matchMedia('(prefers-reduced-motion: no-preference)');
  var mqPin = window.matchMedia('(min-width: 1101px) and (min-height: 720px) and (prefers-reduced-motion: no-preference)');
  var READ_LINE = 0.66;
  var clamp = function (v) { return v < 0 ? 0 : v > 1 ? 1 : v; };
  var fixed = function (v) { return v.toFixed(4); };

  var tracks = [], rails = [], exits = [], enters = [], bars = [];

  function collect() {
    tracks = Array.prototype.map.call(document.querySelectorAll('[data-scroll-track]'), function (el) {
      var items = el.querySelectorAll('[data-step-item]');
      var n = parseInt(el.getAttribute('data-steps'), 10) || items.length || 1;
      el.style.setProperty('--steps', String(n));
      return { el: el, items: items, visuals: el.querySelectorAll('[data-step-visual]'),
               current: el.querySelectorAll('[data-step-current]'), n: n, step: -1 };
    });
    rails = Array.prototype.slice.call(document.querySelectorAll('[data-rail]'));
    exits = Array.prototype.slice.call(document.querySelectorAll('[data-exit="fade"]'));
    enters = Array.prototype.slice.call(document.querySelectorAll('[data-enter]'));
    bars = Array.prototype.slice.call(document.querySelectorAll('.reading-progress, [data-reading-progress]'));
  }

  function topbar() {
    return parseFloat(getComputedStyle(root).getPropertyValue('--topbar-h')) || 0;
  }

  function setStep(t, step) {
    if (step === t.step) return;
    t.step = step;
    if (step < 0) {
      t.el.removeAttribute('data-step');
    } else {
      t.el.setAttribute('data-step', String(step));
    }
    [t.items, t.visuals].forEach(function (list) {
      Array.prototype.forEach.call(list, function (it, i) {
        if (i === step) it.setAttribute('data-active', ''); else it.removeAttribute('data-active');
      });
    });
    Array.prototype.forEach.call(t.current, function (c) { c.textContent = String(Math.max(0, step) + 1); });
    t.el.dispatchEvent(new CustomEvent('landing:step', { bubbles: true, detail: { step: step, steps: t.n } }));
  }

  function update() {
    frame = 0;
    var motion = mqMotion.matches;
    var pin = mqPin.matches;
    var vh = window.innerHeight;
    var offset = topbar();

    tracks.forEach(function (t) {
      var p = 1;
      var r = t.el.getBoundingClientRect();
      if (pin) {
        var room = r.height - (vh - offset);
        p = room > 0 ? clamp((offset - r.top) / room) : 1;
        setStep(t, Math.min(t.n - 1, Math.floor(p * t.n)));
      } else {
        if (motion) p = clamp((vh * 0.9 - r.top) / (vh * 0.5 + r.height * 0.5));
        setStep(t, -1);
      }
      t.el.style.setProperty('--p', fixed(p));
    });

    rails.forEach(function (rail) {
      var marks = rail.querySelectorAll('[data-milestone]');
      if (!motion) {
        rail.style.setProperty('--rail', '1');
        Array.prototype.forEach.call(marks, function (m) { m.setAttribute('data-reached', 'true'); });
        return;
      }
      var line = vh * READ_LINE;
      var r = rail.getBoundingClientRect();
      var first = marks.length ? marks[0].getBoundingClientRect() : r;
      var last = marks.length ? marks[marks.length - 1].getBoundingClientRect() : r;
      var a = first.top + first.height / 2, b = last.top + last.height / 2;
      rail.style.setProperty('--rail', fixed(b > a ? clamp((line - a) / (b - a)) : (line >= a ? 1 : 0)));
      Array.prototype.forEach.call(marks, function (m) {
        var mr = m.getBoundingClientRect();
        m.setAttribute('data-reached', mr.top + Math.min(mr.height, 48) / 2 <= line ? 'true' : 'false');
      });
    });

    if (bars.length) {
      var doc = document.documentElement.scrollHeight - vh;
      var read = doc > 0 ? clamp(window.scrollY / doc) : 0;
      bars.forEach(function (b) { b.style.setProperty('--read', fixed(read)); });
    }

    exits.forEach(function (el) {
      if (!pin) { el.style.removeProperty('--exit'); return; }
      var r = el.getBoundingClientRect();
      // starts when the bottom reaches the bottom of the screen, ends at 40 %
      el.style.setProperty('--exit', fixed(clamp((vh - r.bottom) / (vh * 0.6))));
    });
    enters.forEach(function (el) {
      if (!pin) { el.style.removeProperty('--enter'); return; }
      var r = el.getBoundingClientRect();
      var kind = el.getAttribute('data-enter');
      var p = kind === 'curtain'
        ? clamp((vh - r.top) / (vh * 0.7))
        : clamp((vh * 0.72 - r.top) / (vh * 0.42));
      el.style.setProperty('--enter', fixed(p));
    });
  }

  var frame = 0;
  function request() {
    if (!frame) frame = window.requestAnimationFrame(update);
  }

  function modes() {
    root.classList.toggle('sc-motion', mqMotion.matches);
    root.classList.toggle('sc-pin', mqPin.matches);
    request();
  }

  function start() {
    collect();
    modes();
    window.addEventListener('scroll', request, { passive: true });
    window.addEventListener('resize', request);
    [mqMotion, mqPin].forEach(function (mq) {
      if (mq.addEventListener) mq.addEventListener('change', modes); else mq.addListener(modes);
    });
    if ('ResizeObserver' in window) new ResizeObserver(request).observe(document.body);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(request);
    // A part revealed later (choice gate) brings new tracks and rails.
    document.addEventListener('landing:revealed', function () { collect(); request(); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
})();

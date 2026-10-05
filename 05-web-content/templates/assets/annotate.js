/* ==========================================================================
   annotate.js · hand-drawn annotations on a word or a phrase (optional engine)
   --------------------------------------------------------------------------
   principe : Rough Notation (Preet Shihn, github.com/rough-stuff/rough-notation), MIT.
   The idea is taken and rewritten: an irregular SVG stroke laid on the text
   and drawn once when it comes into view. Here the irregularity is seeded by
   the annotated text (the same stroke on every load), there is no
   dependency, and the stroke takes the colour of the tokens (--hl, never the
   accent of the conversion button).

   Contract (markup, in any slot that accepts HTML):
     <mark data-annotate="underline">two words</mark>
       underline   a line under the text, one per line of text
       highlight   a marker band behind the text, one per line of text
       strike      a line through the text, one per line (if the meaning
                   "removed" matters, say it in words or use <s>)
       circle      a hand ellipse around 1 to 3 words (they never wrap)
       box         a hand frame around 1 to 3 words (they never wrap)
       bracket     a bracket on each side of the phrase
     Any inline element works (<mark>, <strong>, <s>, <span>). An unknown
     value falls back to underline.
   Classes written:
     html.an-on                  engine running: base.css drops the no-JS
                                 emphasis, the drawn stroke replaces it
     [data-annotate].an-pending  stroke laid out, dash hidden, about to draw
     [data-annotate].is-drawn    stroke drawn (once, ~0.8 s)
     svg.an-svg                  decorative overlay inside the element,
                                 aria-hidden: the text itself is unchanged
   Dosage: two annotations per page at most; never in a title that already
   carries a .hl segment; circle and box on 1 to 3 words.
   Loading: declared by evidence-chart and quote-interlude; anywhere else,
   add `engines: [annotate]` to the page spec.
   Without JavaScript (or on a page that does not load this engine): base.css
   gives a sober emphasis in --hl, never the browser's yellow <mark>.
   Under prefers-reduced-motion, or without IntersectionObserver: strokes are
   placed at once, without drawing. Strokes are laid out again (never drawn
   again) when the lines change: resize, web fonts loaded, a part revealed by
   the choice gate, a transform that ends (reveal entries).
   Styles: base.css, reserved block "annotations à main levée".
   ========================================================================== */
(function () {
  'use strict';
  if (window.__landingAnnotate) return;
  window.__landingAnnotate = true;

  var SHAPES = { underline: 1, highlight: 1, strike: 1, circle: 1, box: 1, bracket: 1 };
  var NS = 'http://www.w3.org/2000/svg';
  var root = document.documentElement;

  /* ---- seeded randomness: the same text always gets the same stroke ---- */
  function hash(s) {
    var h = 2166136261;
    for (var i = 0; i < s.length; i++) {
      h ^= s.charCodeAt(i);
      h = Math.imul(h, 16777619);
    }
    return h >>> 0;
  }

  function random(seed) { // mulberry32
    var a = seed >>> 0;
    return function () {
      a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  var items = [];
  var seen = {};
  Array.prototype.forEach.call(document.querySelectorAll('[data-annotate]'), function (el) {
    var type = (el.getAttribute('data-annotate') || '').trim().toLowerCase();
    if (!SHAPES[type]) type = 'underline';
    var key = type + '|' + (el.textContent || '').replace(/\s+/g, ' ').trim();
    seen[key] = (seen[key] || 0) + 1;
    items.push({ el: el, type: type, seed: hash(key + '|' + seen[key]), svg: null, drawn: false, waiting: false });
  });
  if (!items.length) return;

  root.classList.add('an-on');

  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var animate = !reduce && 'IntersectionObserver' in window;

  /* ---- geometry ---- */
  function r1(v) { return Math.round(v * 10) / 10; }
  function pt(p) { return r1(p[0]) + ' ' + r1(p[1]); }

  // Catmull-Rom spline through the points, written as cubic Béziers.
  function spline(points) {
    var d = 'M' + pt(points[0]);
    for (var i = 0; i < points.length - 1; i++) {
      var p0 = points[i - 1] || points[i];
      var p1 = points[i];
      var p2 = points[i + 1];
      var p3 = points[i + 2] || p2;
      d += 'C' + pt([p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6]) +
        ' ' + pt([p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6]) +
        ' ' + pt(p2);
    }
    return d;
  }

  // The element's line boxes, in the coordinates of its SVG overlay. An
  // ancestor scale (a reveal entry still running) is divided out; the final
  // layout is redone when the transform ends.
  function lines(item) {
    var el = item.el;
    var box = el.getBoundingClientRect();
    var scale = el.offsetWidth ? box.width / el.offsetWidth : 1;
    if (!(scale > 0.2 && scale < 5)) scale = 1;
    var o = item.svg.getBoundingClientRect();
    var out = [];
    var rects = el.getClientRects();
    for (var i = 0; i < rects.length; i++) {
      var r = rects[i];
      if (r.width < 1 || r.height < 1) continue;
      var x = (r.left - o.left) / scale;
      var y = (r.top - o.top) / scale;
      var w = r.width / scale;
      var h = r.height / scale;
      var last = out[out.length - 1];
      if (last && Math.abs(last.y - y) < h / 2) {
        var right = Math.max(last.x + last.w, x + w);
        last.x = Math.min(last.x, x);
        last.w = right - last.x;
        last.y = Math.min(last.y, y);
        last.h = Math.max(last.h, h);
      } else {
        out.push({ x: x, y: y, w: w, h: h });
      }
    }
    return out;
  }

  function shapes(type, ls, rnd) {
    function j(a) { return (rnd() * 2 - 1) * a; }
    // A slightly bowed hand line from x0 to x1 around y, rising by `rise`.
    function hand(x0, x1, y, em, rise) {
      var w = x1 - x0;
      return spline([
        [x0, y + rise / 2 + j(em * 0.03)],
        [x0 + w * 0.34, y + rise / 6 + j(em * 0.05)],
        [x0 + w * 0.67, y - rise / 6 + j(em * 0.05)],
        [x1, y - rise / 2 + j(em * 0.03)]
      ]);
    }
    var out = [];
    if (type === 'underline' || type === 'strike' || type === 'highlight') {
      ls.forEach(function (r) {
        var em = r.h / 1.2; // an inline box is about 1.2 em high
        // A short fragment (one word left on a line) gets a calmer stroke.
        var k = Math.min(1, r.w / (em * 4));
        if (type === 'underline') {
          out.push({ d: hand(r.x - em * 0.06, r.x + r.w + em * 0.1, r.y + r.h * 1.02, em * k, em * k * 0.05 + j(em * k * 0.04)),
                     w: Math.max(2, em * 0.085) });
        } else if (type === 'strike') {
          out.push({ d: hand(r.x - em * 0.08, r.x + r.w + em * 0.08, r.y + r.h * 0.56, em * k, em * k * 0.14 + j(em * k * 0.04)),
                     w: Math.max(2, em * 0.08) });
        } else {
          out.push({ d: hand(r.x - em * 0.12, r.x + r.w + em * 0.12, r.y + r.h * 0.54, em * k, j(em * k * 0.05)),
                     w: r.h * 0.72 });
        }
      });
      return out;
    }

    var u = ls.reduce(function (a, r) {
      var x0 = Math.min(a.x, r.x);
      var y0 = Math.min(a.y, r.y);
      return { x: x0, y: y0, w: Math.max(a.x + a.w, r.x + r.w) - x0, h: Math.max(a.y + a.h, r.y + r.h) - y0 };
    });
    var em = ls[0].h / 1.2;
    var sw = Math.max(2, em * 0.07);

    if (type === 'circle') {
      var cx = u.x + u.w / 2;
      var cy = u.y + u.h / 2;
      var rx = u.w / 2 + em * 0.42;
      var ry = u.h / 2 + em * 0.26;
      var start = Math.PI * (1.06 + rnd() * 0.14); // left, a little above the middle
      var sweep = Math.PI * 2 + 0.42 + rnd() * 0.26; // the end runs past the start
      var pts = [];
      var steps = 16;
      for (var i = 0; i <= steps; i++) {
        var k = i / steps;
        var a = start + sweep * k;
        var f = 0.985 + 0.07 * k + j(0.03);
        pts.push([cx + Math.cos(a) * rx * f, cy + Math.sin(a) * ry * f]);
      }
      out.push({ d: spline(pts), w: sw });
      return out;
    }

    if (type === 'box') {
      var b = em * 0.06;
      var x0 = u.x - em * 0.26;
      var x1 = u.x + u.w + em * 0.26;
      var y0 = u.y - em * 0.15;
      var y1 = u.y + u.h + em * 0.13;
      var c = [[x0 + j(b), y0 + j(b)], [x1 + j(b), y0 + j(b)], [x1 + j(b), y1 + j(b)], [x0 + j(b), y1 + j(b)]];
      var edge = function (p, q) {
        return 'Q' + pt([(p[0] + q[0]) / 2 + j(b), (p[1] + q[1]) / 2 + j(b)]) + ' ' + pt(q);
      };
      var first = [c[0][0] - em * 0.1, c[0][1] + j(b)];
      var last = [c[0][0] + Math.min(em * 0.5, (x1 - x0) * 0.3), c[0][1] + j(b)];
      out.push({ d: 'M' + pt(first) + edge(first, c[1]) + edge(c[1], c[2]) + edge(c[2], c[3]) +
                    edge(c[3], c[0]) + edge(c[0], last), w: sw });
      return out;
    }

    // bracket: one on each side, drawn together
    var arm = Math.min(em * 0.38, u.w * 0.25);
    var t = u.y - em * 0.12;
    var bt = u.y + u.h + em * 0.12;
    var l = u.x - em * 0.22;
    var rr = u.x + u.w + em * 0.22;
    var g = em * 0.04;
    out.push({ d: 'M' + pt([l + arm, t + j(g)]) + 'L' + pt([l + j(g), t + j(g)]) +
                  'L' + pt([l + j(g), bt + j(g)]) + 'L' + pt([l + arm, bt + j(g)]), w: sw });
    out.push({ d: 'M' + pt([rr - arm, t + j(g)]) + 'L' + pt([rr + j(g), t + j(g)]) +
                  'L' + pt([rr + j(g), bt + j(g)]) + 'L' + pt([rr - arm, bt + j(g)]), w: sw });
    return out;
  }

  /* ---- drawing ---- */
  function overlay(item) {
    if (!item.svg) {
      var svg = document.createElementNS(NS, 'svg');
      svg.setAttribute('class', 'an-svg');
      svg.setAttribute('aria-hidden', 'true');
      svg.setAttribute('focusable', 'false');
      item.el.appendChild(svg);
      item.svg = svg;
    }
    return item.svg;
  }

  // (Re)computes the paths; false when the text is not rendered (hidden part).
  function layout(item) {
    var svg = overlay(item);
    var ls = lines(item);
    if (!ls.length) return false;
    var list = shapes(item.type, ls, random(item.seed));
    var paths = svg.querySelectorAll('path');
    for (var i = paths.length - 1; i >= list.length; i--) svg.removeChild(paths[i]);
    var together = item.type === 'bracket';
    var each = together ? 0.6 : Math.max(0.3, 0.8 / list.length);
    list.forEach(function (s, k) {
      var p = paths[k];
      if (!p) {
        p = document.createElementNS(NS, 'path');
        p.setAttribute('pathLength', '1');
        svg.appendChild(p);
      }
      p.setAttribute('d', s.d);
      p.setAttribute('stroke-width', String(r1(s.w)));
      p.style.setProperty('--an-dur', each + 's');
      p.style.setProperty('--an-delay', (together ? 0 : k * each) + 's');
    });
    return true;
  }

  function draw(item, animated) {
    if (item.drawn) return;
    if (!layout(item)) return; // retried at the next layout change
    item.drawn = true;
    var el = item.el;
    if (!animated) {
      el.classList.add('is-drawn');
      return;
    }
    el.classList.add('an-pending');
    item.svg.getBoundingClientRect(); // commit the hidden dash before the transition
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        el.classList.remove('an-pending');
        el.classList.add('is-drawn');
      });
    });
  }

  // Draw once the text itself has entered (reveal.js), then a short beat.
  function drawWhenRead(item) {
    if (item.waiting || item.drawn) return;
    item.waiting = true;
    var host = root.classList.contains('rv-on') ? item.el.closest('[data-reveal]') : null;
    var tries = 0;
    (function wait() {
      if (host && !host.classList.contains('is-in') && tries++ < 50) {
        window.setTimeout(wait, 100);
        return;
      }
      window.setTimeout(function () {
        item.waiting = false;
        draw(item, true);
      }, host ? 450 : 200);
    })();
  }

  var queued = false;
  function relayout() {
    if (queued) return;
    queued = true;
    window.requestAnimationFrame(function () {
      queued = false;
      items.forEach(function (item) {
        if (item.drawn) layout(item);
        else if (!animate) draw(item, false);
      });
    });
  }

  if (animate) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        io.unobserve(entry.target);
        for (var i = 0; i < items.length; i++) {
          if (items[i].el === entry.target) drawWhenRead(items[i]);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.75 });
    items.forEach(function (item) { io.observe(item.el); });
  } else {
    items.forEach(function (item) { draw(item, false); });
  }

  if ('ResizeObserver' in window) new ResizeObserver(relayout).observe(root);
  else window.addEventListener('resize', relayout);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(relayout);
  document.addEventListener('landing:revealed', relayout);
  document.addEventListener('transitionend', function (e) {
    if (e.propertyName === 'transform' && e.target.querySelector && e.target.querySelector('.is-drawn')) relayout();
  }, true);
})();

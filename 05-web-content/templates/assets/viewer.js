/* ==========================================================================
   viewer.js · the shared viewer (lightbox) of a landing page
   --------------------------------------------------------------------------
   One native <dialog>, built on the first opening and reused by every
   section: an image, a video, an embed, or HTML content held in a
   <template>, alone or as pages to flip through (« 2 / 6 »).

   Triggers (a link or a button):
     [data-viewer]               opens the viewer on click. Value: "" (type
                                 guessed from the source), "image", "video",
                                 "iframe" (embedded player) or "html".
     href / [data-viewer-src]    the source. "#id" points to a <template> (or
                                 any element) whose content is shown; its
                                 [data-viewer-page] children become pages.
                                 A link stays a plain link to the media
                                 without JavaScript: give it a real href.
     [data-viewer-pages]         image pages: a pattern with {n} plus
                                 [data-viewer-count], or a space-separated
                                 list of URLs.
     [data-viewer-group]         triggers sharing a group are flipped through
                                 together, in page order (hidden ones are
                                 skipped).
     [data-viewer-title]         dialog title (default: the trigger's text).
     [data-viewer-caption]       caption under the media.
     [data-viewer-alt]           alternative text of an image (default: the
                                 title, plus the page number).
     [data-viewer-poster], [data-viewer-captions] (.vtt),
     [data-viewer-captions-lang] video poster and captions track. The .vtt
                                 file must come from the page's origin, or
                                 be served with CORS and the trigger carry
                                 [data-viewer-crossorigin] (the video is then
                                 requested with CORS too).
     [data-viewer-id]            identifier sent with the viewer_open event.
     [data-viewer-js]            a trigger with no destination without script
                                 (button, inline HTML): carries `hidden` in
                                 the markup; the engine shows it.
   Pages inside a <template>:
     <div data-viewer-page data-viewer-caption="…">HTML of the page</div>
     <div data-viewer-page data-viewer-src="page-2.webp" data-viewer-alt="…"
          data-viewer-caption="…"></div>         (an image page)

   Behaviour: showModal() (the rest of the page becomes inert), labelled
   title, caption as description, close button, Escape, click on the empty
   stage, arrows (and Home / End) within a sequence, swipe on touch screens,
   page scroll locked, video paused and removed on close, focus given back to
   the trigger. Previous / next never wrap: they are marked aria-disabled at
   the ends (still focusable). The page number reaches screen readers through
   a polite status, written once the flipping settles. A video starts on
   opening, except under prefers-reduced-motion (the visitor presses play).
   Fade and zoom on opening only when motion is allowed.

   Styles: injected once, in a <style data-viewer-style>, on the first
   opening (no CSS file for an engine; no colour written here, the dialog
   takes the dark band palette of base.css). Labels follow <html lang>:
   French, otherwise English.

   Events: `landing:viewer` on document (detail: { open, type, id, pages }),
   and viewer_open through the measurement relay (tracking.js) when loaded.
   API: window.landingViewer.open(trigger), window.landingViewer.close().
   Without JavaScript, or without <dialog>: nothing is intercepted, links go
   to their media. Principle: a paged proof viewer, rewritten on <dialog>.
   ========================================================================== */
(function () {
  'use strict';
  if (window.__landingViewer) return;
  window.__landingViewer = true;

  var doc = document;
  var root = doc.documentElement;
  var supported = typeof window.HTMLDialogElement === 'function'
    && typeof window.HTMLDialogElement.prototype.showModal === 'function';
  if (!supported) return;

  var motion = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var LABELS = {
    fr: { close: 'Fermer', prev: 'Précédent', next: 'Suivant', of: 'sur', page: 'page',
          error: 'Ce média n’a pas pu être chargé.', file: 'Ouvrir le fichier', captions: 'Sous-titres' },
    en: { close: 'Close', prev: 'Previous', next: 'Next', of: 'of', page: 'page',
          error: 'This media could not be loaded.', file: 'Open the file', captions: 'Captions' }
  };
  var lang = (root.getAttribute('lang') || 'fr').slice(0, 2).toLowerCase();
  var L = LABELS[lang] || LABELS.en;
  var VIDEO = /\.(mp4|webm|m4v|mov|ogv)(\?|#|$)/i;

  // A trigger that only works with script is shown now that it will work.
  doc.querySelectorAll('[data-viewer-js][hidden]').forEach(function (el) { el.hidden = false; });

  var CSS = [
    'html.lv-lock{overflow:hidden;scrollbar-gutter:stable}',
    '.lv{position:fixed;inset:0;width:100%;height:100%;max-width:none;max-height:none;margin:0;padding:0;border:0;overflow:hidden;background:var(--paper);color:var(--ink);font-family:var(--font-display)}',
    '.lv::backdrop{background:transparent}',
    '.lv [hidden]{display:none!important}',
    '.lv__frame{display:grid;grid-template-rows:auto minmax(0,1fr) auto;gap:clamp(10px,0.4rem + 1vw,20px);height:100%;padding:clamp(12px,0.4rem + 1vw,24px) clamp(16px,0.4rem + 2.4vw,48px)}',
    '.lv__bar{display:flex;align-items:center;gap:16px}',
    '.lv__title{flex:1;min-width:0;font-size:1.125rem;line-height:1.3;font-weight:700;letter-spacing:-0.01em;text-wrap:balance}',
    '.lv__icon{display:inline-grid;flex:none;place-items:center;width:48px;height:48px;padding:0;border:1.5px solid var(--line-strong);border-radius:50%;background:transparent;color:var(--ink);cursor:pointer;transition:border-color var(--dur-fast) var(--ease),transform var(--dur-fast) var(--ease)}',
    '.lv__icon:hover{border-color:var(--ink)}',
    '.lv__icon[aria-disabled="true"]{opacity:0.35;cursor:default}',
    '.lv__icon[aria-disabled="true"]:hover{border-color:var(--line-strong)}',
    '.lv__icon svg{width:22px;height:22px}',
    '.lv__stage{position:relative;display:grid;grid-template:minmax(0,1fr) / minmax(0,1fr);place-items:center;min-height:0;touch-action:pan-y pinch-zoom}',
    '.lv__media{display:block;width:auto;height:auto;max-width:100%;max-height:100%;object-fit:contain;border-radius:calc(var(--radius-card) / 2);background:var(--surface)}',
    '.lv__embed{display:block;width:min(100%,calc((100dvh - 230px) * 16 / 9));aspect-ratio:16 / 9;border:0;border-radius:calc(var(--radius-card) / 2);background:var(--surface)}',
    '.lv__page{--ink:var(--brand-dark);--paper:var(--brand-white);--surface:var(--brand-white);--surface-2:var(--brand-surface-2);--muted:var(--brand-muted);--hl:var(--brand-primary-text);--line:var(--brand-line);--line-strong:var(--brand-field-border);--focus:var(--brand-dark);width:min(100%,760px);max-height:100%;overflow:auto;padding:clamp(16px,0.6rem + 1.6vw,36px);border-radius:var(--radius-card);background:var(--paper);color:var(--ink);overscroll-behavior:contain}',
    '.lv__error{display:grid;justify-items:center;gap:12px;max-width:32rem;text-align:center}',
    '.lv__error a{color:var(--ink);font-weight:600}',
    '.lv__foot{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:12px 32px;min-height:48px}',
    '.lv__caption{max-width:62ch;color:var(--muted);font-size:var(--t-body);line-height:1.5;text-wrap:pretty}',
    '.lv__nav{display:flex;align-items:center;gap:12px}',
    '.lv__count{min-width:5.5em;font-family:var(--font-mono);font-size:var(--t-label);letter-spacing:0.06em;text-align:center;font-variant-numeric:tabular-nums}',
    '.lv .sr-only{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap;border:0}',
    '@media (max-width:640px){.lv__foot{grid-template-columns:minmax(0,1fr)}.lv__nav{justify-content:space-between}}',
    '@media (prefers-reduced-motion:no-preference){.lv[open]{animation:lv-fade .22s var(--ease)}.lv__slide{animation:lv-in .34s var(--ease)}}',
    '@keyframes lv-fade{from{opacity:0}}',
    '@keyframes lv-in{from{opacity:0;transform:scale(0.965)}}'
  ].join('\n');

  var ICON = {
    close: '<path d="M6 6l12 12M18 6 6 18"/>',
    prev: '<path d="M19 12H5"/><path d="m11 6-6 6 6 6"/>',
    next: '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>'
  };
  function icon(name) {
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" '
      + 'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + ICON[name] + '</svg>';
  }

  var dialog = null;
  var els = {};
  var state = null;
  var statusTimer = 0;
  var swipe = null;

  function build() {
    var style = doc.createElement('style');
    style.setAttribute('data-viewer-style', '');
    style.textContent = CSS;
    doc.head.appendChild(style);

    dialog = doc.createElement('dialog');
    dialog.className = 'lv band-dark';
    dialog.setAttribute('aria-labelledby', 'landing-viewer-title');
    dialog.setAttribute('aria-describedby', 'landing-viewer-caption');
    dialog.innerHTML =
      '<div class="lv__frame">'
      + '<div class="lv__bar"><h2 class="lv__title" id="landing-viewer-title"></h2>'
      + '<button type="button" class="lv__icon" data-lv="close" aria-label="' + L.close + '">' + icon('close') + '</button></div>'
      + '<div class="lv__stage" data-lv="stage"></div>'
      + '<div class="lv__foot"><p class="lv__caption" id="landing-viewer-caption" data-lv="caption"></p>'
      + '<div class="lv__nav" data-lv="nav">'
      + '<button type="button" class="lv__icon" data-lv="prev" aria-label="' + L.prev + '">' + icon('prev') + '</button>'
      + '<p class="lv__count"><span aria-hidden="true" data-lv="count"></span><span class="sr-only" data-lv="count-sr"></span></p>'
      + '<button type="button" class="lv__icon" data-lv="next" aria-label="' + L.next + '">' + icon('next') + '</button>'
      + '</div></div>'
      + '<p class="sr-only" role="status" data-lv="status"></p>'
      + '</div>';
    doc.body.appendChild(dialog);
    ['close', 'stage', 'caption', 'nav', 'prev', 'next', 'count', 'count-sr', 'status'].forEach(function (k) {
      els[k] = dialog.querySelector('[data-lv="' + k + '"]');
    });
    els.title = dialog.querySelector('.lv__title');

    els.close.addEventListener('click', close);
    els.prev.addEventListener('click', function () { go(state ? state.index - 1 : 0); });
    els.next.addEventListener('click', function () { go(state ? state.index + 1 : 0); });
    dialog.addEventListener('close', cleanup);
    dialog.addEventListener('keydown', onKey);
    dialog.addEventListener('click', function (e) {
      if (e.target === dialog || e.target === els.stage) close();
    });
    els.stage.addEventListener('pointerdown', function (e) {
      swipe = (e.pointerType === 'mouse' || !e.isPrimary) ? null : { x: e.clientX, y: e.clientY };
    });
    els.stage.addEventListener('pointerup', function (e) {
      if (!swipe || !state) return;
      var dx = e.clientX - swipe.x;
      var dy = e.clientY - swipe.y;
      swipe = null;
      if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) go(state.index + (dx < 0 ? 1 : -1));
    });
    els.stage.addEventListener('pointercancel', function () { swipe = null; });
  }

  /* ---- what a trigger shows ---- */
  function label(el) {
    return (el.getAttribute('data-viewer-title') || el.getAttribute('aria-label') || el.textContent || '')
      .replace(/\s+/g, ' ').trim();
  }

  function pagesOf(trigger) {
    var title = label(trigger);
    var caption = trigger.getAttribute('data-viewer-caption') || '';
    var kind = (trigger.getAttribute('data-viewer') || '').toLowerCase();
    var pattern = trigger.getAttribute('data-viewer-pages');
    var out = [];
    if (pattern) {
      var list = [];
      if (pattern.indexOf('{n}') !== -1) {
        var count = parseInt(trigger.getAttribute('data-viewer-count'), 10) || 1;
        for (var i = 1; i <= count; i++) list.push(pattern.split('{n}').join(String(i)));
      } else {
        list = pattern.trim().split(/\s+/);
      }
      list.forEach(function (src) {
        out.push({ type: 'image', src: src, alt: trigger.getAttribute('data-viewer-alt') || '' });
      });
    } else {
      var src = trigger.getAttribute('data-viewer-src') || trigger.getAttribute('href') || '';
      if (src.charAt(0) === '#' && src.length > 1) {
        var source = doc.getElementById(src.slice(1));
        if (source) {
          var content = source.content || source;
          var pages = content.querySelectorAll('[data-viewer-page]');
          if (pages.length) {
            Array.prototype.forEach.call(pages, function (p) {
              var psrc = p.getAttribute('data-viewer-src');
              out.push(psrc
                ? { type: 'image', src: psrc, alt: p.getAttribute('data-viewer-alt') || '', caption: p.getAttribute('data-viewer-caption') }
                : { type: 'html', node: p, caption: p.getAttribute('data-viewer-caption') });
            });
          } else {
            out.push({ type: 'html', node: content });
          }
        }
      } else if (src && src.charAt(0) !== '#') {
        var type = (kind === 'video' || kind === 'image' || kind === 'iframe') ? kind : (VIDEO.test(src) ? 'video' : 'image');
        out.push({ type: type, src: src, alt: trigger.getAttribute('data-viewer-alt') || '',
                   poster: trigger.getAttribute('data-viewer-poster') || '',
                   captions: trigger.getAttribute('data-viewer-captions') || '',
                   captionsLang: trigger.getAttribute('data-viewer-captions-lang') || lang,
                   cors: trigger.hasAttribute('data-viewer-crossorigin') });
      }
    }
    out.forEach(function (p) {
      p.trigger = trigger;
      p.title = title;
      if (!p.caption) p.caption = caption;
    });
    return out;
  }

  function rendered(el) {
    return !el.closest('[hidden]') && el.getClientRects().length > 0;
  }

  function sequence(trigger) {
    var group = trigger.getAttribute('data-viewer-group');
    var triggers = [trigger];
    if (group) {
      triggers = Array.prototype.filter.call(doc.querySelectorAll('[data-viewer-group]'), function (t) {
        return t.getAttribute('data-viewer-group') === group && (t === trigger || rendered(t));
      });
    }
    var slides = [];
    var start = 0;
    triggers.forEach(function (t) {
      if (t === trigger) start = slides.length;
      slides = slides.concat(pagesOf(t));
    });
    return { slides: slides, index: start };
  }

  /* ---- drawing a slide ---- */
  function failed(s) {
    var box = doc.createElement('div');
    box.className = 'lv__error lv__slide';
    var p = doc.createElement('p');
    p.textContent = L.error;
    box.appendChild(p);
    if (s.src) {
      var a = doc.createElement('a');
      a.href = s.src;
      a.textContent = L.file;
      box.appendChild(a);
    }
    return box;
  }

  function slide(s, n, total) {
    var el;
    if (s.type === 'image') {
      el = doc.createElement('img');
      el.className = 'lv__media lv__slide';
      el.decoding = 'async';
      el.alt = s.alt || (total > 1 ? s.title + ', ' + L.page + ' ' + n + ' ' + L.of + ' ' + total : s.title);
      el.addEventListener('error', function () { if (el.isConnected) el.replaceWith(failed(s)); });
      el.src = s.src;
    } else if (s.type === 'video') {
      el = doc.createElement('video');
      el.className = 'lv__media lv__slide';
      el.controls = true;
      el.playsInline = true;
      el.preload = 'metadata';
      if (s.poster) el.poster = s.poster;
      if (s.cors) el.crossOrigin = 'anonymous';
      if (s.captions) {
        var track = doc.createElement('track');
        track.kind = 'captions';
        track.src = s.captions;
        track.srclang = s.captionsLang;
        track.label = L.captions;
        track.default = true;
        el.appendChild(track);
      }
      el.addEventListener('error', function () { if (el.isConnected) el.replaceWith(failed(s)); });
      el.src = s.src;
    } else if (s.type === 'iframe') {
      el = doc.createElement('iframe');
      el.className = 'lv__embed lv__slide';
      el.title = s.title;
      el.allow = 'autoplay; fullscreen; picture-in-picture';
      el.setAttribute('allowfullscreen', '');
      el.src = s.src;
    } else {
      el = doc.createElement('div');
      el.className = 'lv__page lv__slide';
      var copy = s.node.cloneNode(true);
      if (copy.nodeType === 11) {
        el.appendChild(copy);
      } else {
        while (copy.firstChild) el.appendChild(copy.firstChild);
      }
      el.querySelectorAll('[id]').forEach(function (x) { x.removeAttribute('id'); });
    }
    return el;
  }

  function stopMedia() {
    if (!els.stage) return;
    els.stage.querySelectorAll('video, audio').forEach(function (m) { try { m.pause(); } catch (e) { /* gone */ } });
  }

  function preload(s) {
    if (s && s.type === 'image' && !s.preloaded) {
      s.preloaded = true;
      var img = new Image();
      img.decoding = 'async';
      img.src = s.src;
    }
  }

  function render(announce) {
    var s = state.slides[state.index];
    var total = state.slides.length;
    var n = state.index + 1;
    stopMedia();
    var el = slide(s, n, total);
    els.stage.replaceChildren(el);
    if (s.type === 'html') {
      // A page taller than the stage scrolls: make it reachable by keyboard.
      window.requestAnimationFrame(function () {
        if (el.isConnected && el.scrollHeight > el.clientHeight + 1) {
          el.tabIndex = 0;
          el.setAttribute('role', 'region');
          el.setAttribute('aria-label', s.title);
        }
      });
    }
    if (s.type === 'video' && !motion.matches) {
      var play = el.play && el.play();
      if (play && play.catch) play.catch(function () { /* blocked: controls stay */ });
    }
    els.title.textContent = s.title;
    els.caption.textContent = s.caption || '';
    els.nav.hidden = total < 2;
    els.count.textContent = n + ' / ' + total;
    els['count-sr'].textContent = n + ' ' + L.of + ' ' + total;
    els.prev.setAttribute('aria-disabled', n === 1 ? 'true' : 'false');
    els.next.setAttribute('aria-disabled', n === total ? 'true' : 'false');
    preload(state.slides[state.index + 1]);
    window.clearTimeout(statusTimer);
    if (announce) {
      statusTimer = window.setTimeout(function () {
        if (state) els.status.textContent = n + ' ' + L.of + ' ' + total + (s.caption ? '. ' + s.caption : '');
      }, 400);
    }
  }

  function go(i) {
    if (!state || i < 0 || i >= state.slides.length || i === state.index) return;
    state.index = i;
    render(true);
  }

  function onKey(e) {
    if (!state) return;
    var t = e.target;
    if (t && (/^(VIDEO|AUDIO|INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable)) return;
    var last = state.slides.length - 1;
    var to = { ArrowRight: state.index + 1, ArrowLeft: state.index - 1, Home: 0, End: last }[e.key];
    if (to === undefined || last < 1) return;
    e.preventDefault();
    go(Math.max(0, Math.min(last, to)));
  }

  function emit(open, s) {
    var detail = { open: open, type: s ? s.type : '', id: s ? (s.trigger.getAttribute('data-viewer-id') || s.title) : '',
                   pages: state ? state.slides.length : 0 };
    doc.dispatchEvent(new CustomEvent('landing:viewer', { detail: detail }));
    if (open && typeof window.landingTrack === 'function') {
      window.landingTrack('viewer_open', { content_type: detail.type, content_id: detail.id, pages: detail.pages });
    }
  }

  function open(trigger) {
    if (!trigger) return false;
    var seq = sequence(trigger);
    if (!seq.slides.length) return false;
    if (!dialog) build();
    // Already open (API call from a section): swap the content, keep the opener.
    var opener = (dialog.open && state) ? state.opener : trigger;
    state = { slides: seq.slides, index: seq.index, opener: opener };
    els.status.textContent = '';
    render(false);
    if (!dialog.open) {
      root.classList.add('lv-lock');
      dialog.showModal();
    }
    els.close.focus();
    emit(true, state.slides[state.index]);
    return true;
  }

  function close() {
    if (dialog && dialog.open) dialog.close();
  }

  function cleanup() {
    window.clearTimeout(statusTimer);
    stopMedia();
    if (els.stage) els.stage.replaceChildren();
    root.classList.remove('lv-lock');
    var opener = state && state.opener;
    var last = state && state.slides[state.index];
    emit(false, last);
    state = null;
    if (opener && opener.isConnected) opener.focus({ preventScroll: true });
  }

  doc.addEventListener('click', function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var trigger = e.target.closest ? e.target.closest('[data-viewer]') : null;
    if (!trigger || (dialog && dialog.contains(trigger))) return;
    if (open(trigger)) e.preventDefault();
  });

  window.landingViewer = { open: open, close: close };
})();

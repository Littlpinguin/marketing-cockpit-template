#!/usr/bin/env python3
"""QA d'une landing page HTML statique : ce qui se mesure dans un navigateur.

La page est rendue dans Chromium (Playwright) à trois tailles d'écran, puis une
fois avec `prefers-reduced-motion: reduce`, et, si elle déclare un suivi
d'audience, une dernière fois pour cliquer ses CTA primaires. Le script mesure ;
il ne juge ni le goût, ni le message, ni la marque (c'est le travail des
revues de la skill `landing-page`).

Usage :
    python3 05-web-content/scripts/qa-landing.py 05-web-content/landing-pages/<slug>/index.html
    python3 05-web-content/scripts/qa-landing.py <page.html> --format json

Déroulé, pour chaque taille d'écran (défaut 375x812, 768x1024, 1440x900) :
chargement, attente, relevé des CTA visibles sans défiler (le « pli »), puis
transitions et animations rendues instantanées, défilement de toute la page
(pour déclencher les apparitions au scroll), et relevé de l'état final.

Ce qu'il contrôle
-----------------
Page (une fois) :
  lang               `<html lang>` absent, vide ou mal formé                  erreur
  meta-viewport      pas de `<meta name="viewport">` : le mobile est faux      erreur
  titre-page         `<title>` absent ou vide                                 erreur
  titres-h1          aucun h1, ou plus d'un                                   erreur
  titres-ordre       niveau de titre sauté (h2 puis h4)                       erreur
  image-alt          `<img>` sans attribut alt (décoratif : alt="") ou
                     `role="img"` sans nom ; alt en nom de fichier             erreur / avert.
  nom-accessible     lien ou bouton sans nom accessible                        erreur
  champ-sans-label   champ de formulaire sans label (le placeholder n'en
                     est pas un)                                              erreur
  cta-absent         aucun CTA repéré                                         erreur
  cta-destination    CTA sans destination (href vide, `#`, ancre
                     introuvable) ; endpoint encore en placeholder ou
                     formulaire sans action                                   erreur / avert.
  cta-hors-objectif  CTA qui ne mène pas à la conversion primaire              avertissement
  tracking           suivi déclaré (gtag, GTM, dataLayer) : aucun
                     événement au clic d'un CTA primaire. Non déclaré :
                     crochet `data-track` absent du CTA primaire               erreur / avert.
  placeholder        `{{...}}` restant dans le texte ou un attribut            avertissement
  titre-ponctuation  titre h1-h4 terminé par un point ou portant une virgule   avertissement
  surtitre-pastille  pastille de sur-titre (eyebrow) posée sur un titre de
                     section                                                  avertissement

Par taille d'écran :
  debordement        la page défile horizontalement                           erreur
  debordement-masque un élément dépasse, caché par un overflow-x sur
                     html ou body (iOS laisse parfois glisser)                avertissement
  plancher-typo      texte sous son plancher (voir « Planchers »)              erreur
  contraste          WCAG 2.x AA (4,5:1 ; 3:1 dès 24 px, ou 18,66 px gras),
                     opacités composées. Texture répétée sur un aplat :
                     jugée sur l'aplat. Dégradé : jugé à chaque arrêt de
                     couleur ; erreur s'il échoue partout, avertissement
                     (un par fond) s'il échoue seulement au pire point.
                     Photo : non calculable, un avertissement par fond        erreur / avert.
  police             famille hors marque, si 01-brand/tokens.json (ou
                     --police) donne les familles                             erreur
  cible-tactile      écran mobile : cible sous 24 px (WCAG 2.5.8), ou sous
                     44 px pour un CTA ; entre 24 et 44 px ailleurs           erreur / avert.
  cta-pli            écran mobile : aucun CTA primaire visible sans défiler   erreur
  mot-orphelin       titre, accroche ou bouton dont la dernière ligne tient
                     en un seul mot                                           avertissement
  troncature         plus de textes que le collecteur n'en relève              avertissement

Mouvement réduit (une fois, à la plus large des tailles) :
  mouvement-reduit-masque     un texte reste masqué (opacité nulle ou
                              visibility) avec prefers-reduced-motion, alors
                              qu'il s'affiche sans                            erreur
  mouvement-reduit-apparition un texte n'apparaît qu'au défilement : l'état
                              final doit être affiché d'emblée                avertissement
  mouvement-reduit-anime      une animation tourne encore (CSS, transition,
                              script, vidéo en lecture automatique)           erreur
  compte-a-rebours            un nombre change seul à l'écran : l'urgence
                              honnête se compte en jours, pas en secondes     avertissement

Planchers
---------
  - étiquettes (tout texte visible) : 12 px ;
  - texte courant, c'est-à-dire tout texte de 12 mots ou plus : 16 px partout
    (erreur en dessous) ; à partir de 1024 px de large (bureau), 18 px
    recommandés (avertissement entre 16 et 18 px) ;
  - cibles tactiles sur mobile (largeur < 768 px) : 24 px minimum (WCAG 2.5.8
    AA), 44 px recommandés (WCAG 2.5.5, guides iOS et Android), exigés pour
    un CTA. Un lien dans une phrase est exempté.
Chaque plancher se règle par option (--plancher-etiquette, --plancher-courant,
--plancher-courant-bureau). Tolérance d'arrondi : 0,15 px.

Exemptions : un texte dans une scène `aria-hidden="true"` (doublée d'un
équivalent lisible) n'a pas de plancher, son contraste reste jugé ; un
conteneur `data-qa-decor` (illustration composée en HTML, maquette d'interface)
sort ses textes de tout jugement typographique. Les deux se posent sur
l'illustration, jamais sur un bloc de texte à lire. Un bandeau cookies ou une
boîte de dialogue n'est pas un CTA.

CTA
---
Un CTA est un lien ou un bouton qui porte `data-cta`, `data-cta-position` ou
`data-track`, une classe btn / button / cta, un bouton d'envoi de formulaire,
ou un lien dessiné en bouton (fond et marges intérieures). Le CTA primaire est,
dans l'ordre : celui qui porte `data-cta="primaire"` (ou `primary`), le premier
`data-cta-position="hero"`, le premier CTA de `<main>`, le premier CTA. Tous
les CTA qui mènent à la même destination sont primaires ; une ancre vers le
bloc qui contient le formulaire et le bouton d'envoi de ce formulaire mènent
à la même conversion. Pour lever toute ambiguïté, poser `data-cta="primaire"`.

Suivi : la page « déclare » un suivi quand elle charge gtag.js ou GTM, ou
qu'un script initialise `dataLayer` ou appelle `gtag('config', …)`
(--tracking oui|non force la décision). Le script clique alors chaque CTA
primaire, navigation empêchée et réseau coupé, et regarde ce qui part dans
`dataLayer`. Rien n'est envoyé hors de la machine.

Niveaux : `erreur` fait échouer la QA ; `avertissement` est listé sans la
faire échouer ; `resume` remplace les constats masqués par le plafond
(--max-par-type, 8 par type et par bloc) et ne compte jamais. Le JSON porte
aussi `errors_total`, `warnings_total` et `by_type`, calculés avant plafond.

Codes de sortie : 0 propre (avertissements admis), 1 au moins une erreur,
2 usage incorrect, fichier illisible ou Playwright absent.

Calculs (couleurs, contraste, opacité, police, viewport, collecteur des
textes) : `06-graphic-design/scripts/qa_common.py`, partagé avec qa-visuel.py.

Prérequis : Python 3.10+, pip install playwright && playwright install chromium
Tests     : python3 -m pytest scripts/tests/test_qa_landing.py -q
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from types import ModuleType

RACINE = Path(__file__).resolve().parents[2]


def charger_module(nom: str, chemin: Path) -> ModuleType:
    """Charge un module par chemin : ces dossiers ne sont pas des paquets importables."""
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qa_common = charger_module("qa_common", RACINE / "06-graphic-design" / "scripts" / "qa_common.py")

# --------------------------------------------------------------------------
# Seuils (doctrine : .claude/skills/landing-page/references/pieges.md)
# --------------------------------------------------------------------------
VIEWPORTS_DEFAUT = "375x812,768x1024,1440x900"
LARGEUR_MOBILE_MAX = 767         # en dessous de 768 px de large : écran mobile
LARGEUR_BUREAU_MIN = 1024        # à partir de 1024 px : plancher bureau du texte courant
PLANCHER_ETIQUETTE_PX = 12.0     # tout texte visible
PLANCHER_COURANT_PX = 16.0       # texte courant, mobile et tablette
PLANCHER_COURANT_BUREAU_PX = 18.0  # texte courant, bureau
MOTS_TEXTE_COURANT = 12          # à partir de 12 mots, un texte se lit comme du texte courant
CIBLE_MIN_PX = 24.0              # WCAG 2.5.8 (AA)
CIBLE_CONFORT_PX = 44.0          # WCAG 2.5.5 (AAA), guides iOS / Android ; exigé pour un CTA
MAX_PAR_TYPE = 8
MAX_TEXTES = 1500
ATTENTE_MS = 1200
OBSERVATION_MS = 1200            # mouvement réduit : temps d'observation entre deux relevés
CLIC_MS = 400                    # suivi : attente après le clic d'un CTA

RE_LANG = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{1,8})*$")
# Placeholders du dépôt : {{MAJUSCULES_SNAKE}} (docs/placeholders.json). Un {{prenom}} en
# minuscules est le plus souvent un exemple montré dans la page, pas un oubli.
RE_PLACEHOLDER = re.compile(r"\{\{\s*[A-Z][A-Z0-9_]*\s*\}\}")
RE_COULEURS = re.compile(r"rgba?\([^)]*\)|#[0-9a-fA-F]{3,8}\b|\btransparent\b")
TOLERANCE_PX = 0.15             # arrondi de rendu : 17,9 px se lit 18 px
RE_ALT_FICHIER = re.compile(r"(\.(png|jpe?g|webp|gif|svg|avif)$)|(^(img|image|dsc|photo)[-_ ]?\d+$)", re.I)

# Transitions et animations rendues instantanées pour mesurer l'état final : une
# apparition encore à mi-course fausserait le contraste.
SETTLE_CSS = """
*, *::before, *::after {
  transition-delay: 0s !important;
  transition-duration: 0.01ms !important;
  animation-delay: 0s !important;
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  scroll-behavior: auto !important;
}
"""


class ErreurUsage(Exception):
    """Usage incorrect, fichier illisible ou outil absent : sortie 2."""


# --------------------------------------------------------------------------
# JavaScript : les collecteurs relèvent, Python tranche
# --------------------------------------------------------------------------

# Fonctions communes, préfixées à chaque collecteur.
JS_OUTILS = r"""
const chemin = el => {
  const parts = [];
  for (let n = el; n && n.nodeType === 1 && n !== document.documentElement; n = n.parentElement) {
    let i = 1;
    for (let s = n.previousElementSibling; s; s = s.previousElementSibling) if (s.tagName === n.tagName) i++;
    parts.unshift(n.tagName.toLowerCase() + ':nth-of-type(' + i + ')');
  }
  return 'html > ' + parts.join(' > ');
};
const nom = el => {
  const id = el.id ? '#' + el.id : '';
  const cls = (el.getAttribute('class') || '').trim().split(/\s+/).filter(Boolean).slice(0, 2)
    .map(c => '.' + c).join('');
  return el.tagName.toLowerCase() + id + cls;
};
const extrait = (t, n) => (t || '').replace(/\s+/g, ' ').trim().slice(0, n || 50);
const rendu = el => el.checkVisibility ? el.checkVisibility()
  : getComputedStyle(el).display !== 'none';
const visible = el => el.checkVisibility
  ? el.checkVisibility({ checkOpacity: true, checkVisibilityCSS: true })
  : (() => { const cs = getComputedStyle(el);
             return cs.display !== 'none' && cs.visibility !== 'hidden' && parseFloat(cs.opacity) > 0; })();
const masqueVisuellement = el => {
  for (let n = el; n && n !== document.body && n !== document.documentElement; n = n.parentElement) {
    const cs = getComputedStyle(n);
    if (cs.clip && cs.clip !== 'auto' && cs.position === 'absolute') return true;
    if (/^inset\((50|100)%/.test(cs.clipPath || '')) return true;
    const r = n.getBoundingClientRect();
    if (r.width <= 1 && r.height <= 1 && cs.overflow === 'hidden') return true;
  }
  return false;
};
const dansAriaHidden = el => !!el.closest('[aria-hidden="true"]');
const motsDe = t => { const s = (t || '').trim(); return s ? s.split(/\s+/).length : 0; };
const nomAccessible = el => {
  const ids = el.getAttribute('aria-labelledby');
  if (ids) {
    const t = ids.split(/\s+/).map(id => { const r = document.getElementById(id);
      return r ? r.textContent : ''; }).join(' ').replace(/\s+/g, ' ').trim();
    if (t) return t;
  }
  const aria = (el.getAttribute('aria-label') || '').trim();
  if (aria) return aria;
  if (el.tagName === 'INPUT') {
    const type = (el.getAttribute('type') || 'text').toLowerCase();
    if (type === 'image') return (el.getAttribute('alt') || '').trim();
    if (['submit', 'reset', 'button'].includes(type))
      return (el.value || (type === 'submit' ? 'Submit' : type === 'reset' ? 'Reset' : '')).trim();
  }
  const parcours = n => {
    if (n.nodeType === 3) return n.textContent;
    if (n.nodeType !== 1) return '';
    if (n.getAttribute('aria-hidden') === 'true') return '';
    const cs = getComputedStyle(n);
    if (cs.display === 'none' || cs.visibility === 'hidden') return '';
    if (n.tagName === 'IMG') return n.getAttribute('alt') || '';
    if (n.tagName.toLowerCase() === 'svg') {
      const titre = n.querySelector('title');
      return n.getAttribute('aria-label') || (titre ? titre.textContent : '') || '';
    }
    if (n !== el && n.getAttribute('aria-label')) return n.getAttribute('aria-label');
    return Array.from(n.childNodes).map(parcours).join(' ');
  };
  const t = parcours(el).replace(/\s+/g, ' ').trim();
  return t || (el.getAttribute('title') || '').trim();
};

// --- CTA : repérage, destination, crochet de suivi ---
const CANDIDATS_CTA = 'a, button, input[type="submit"], input[type="button"], [role="button"]';
const HORS_CTA = 'dialog, [role="dialog"], [role="alertdialog"], [aria-modal="true"], '
  + '[id*="cookie" i], [class*="cookie" i], [id*="consent" i], [class*="consent" i]';
const estCta = el => {
  if (dansAriaHidden(el) || el.closest(HORS_CTA)) return false;
  if (el.hasAttribute('data-cta') || el.hasAttribute('data-cta-position') || el.hasAttribute('data-track')) return true;
  const cls = (el.getAttribute('class') || '').toLowerCase();
  if (/(^|[\s_-])(btn|button|cta)([\s_-]|$)/.test(cls)) return true;
  const form = el.form || null;
  if (form && ((el.tagName === 'BUTTON' && (el.getAttribute('type') || 'submit') === 'submit')
               || (el.tagName === 'INPUT' && el.type === 'submit'))) return true;
  if (el.tagName === 'A' && el.hasAttribute('href')) {
    const cs = getComputedStyle(el);
    const fond = cs.backgroundColor || '';
    const peint = (fond && fond !== 'transparent' && !/rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(fond))
                  || (cs.backgroundImage && cs.backgroundImage !== 'none');
    const marges = parseFloat(cs.paddingLeft) >= 12 && parseFloat(cs.paddingTop) >= 6;
    if (peint && marges && cs.display !== 'inline') return true;
  }
  return false;
};
const crochet = el => {
  for (const a of el.getAttributeNames())
    if (/^data-(track|event|gtm|analytics|ga)/.test(a)) return a + '=' + el.getAttribute(a);
  const clic = el.getAttribute('onclick') || '';
  if (/gtag|dataLayer/.test(clic)) return 'onclick';
  return '';
};
const destination = el => {
  if (el.tagName === 'A') {
    if (!el.hasAttribute('href')) return { genre: 'lien', dest: null, defaut: 'sans href' };
    const h = el.getAttribute('href').trim();
    if (h === '' || h === '#' || h === '#!' || /^javascript:/i.test(h))
      return { genre: 'lien', dest: h, defaut: 'href vide ou factice' };
    if (h.startsWith('#')) {
      let id = h.slice(1);
      try { id = decodeURIComponent(id); } catch (e) {}
      const cible = document.getElementById(id);
      const forms = cible ? Array.from(cible.matches('form') ? [cible] : cible.querySelectorAll('form')).map(chemin) : [];
      return { genre: 'ancre', dest: h, cible_existe: !!cible, formulaires: forms };
    }
    return { genre: 'lien', dest: h };
  }
  const form = el.form || el.closest('form');
  const envoi = form && ((el.tagName === 'BUTTON' && (el.getAttribute('type') || 'submit') === 'submit')
                         || (el.tagName === 'INPUT' && el.type === 'submit'));
  if (envoi) {
    const ids = [];
    for (let n = form; n; n = n.parentElement) if (n.id) ids.push(n.id);
    return { genre: 'envoi', dest: form.hasAttribute('action') ? form.getAttribute('action') : null,
             formulaire: chemin(form), ancetres: ids };
  }
  return { genre: 'script', dest: null };
};
const releverCtas = () => {
  const main = document.querySelector('main');
  const vh = window.innerHeight, vw = window.innerWidth;
  return Array.from(document.querySelectorAll(CANDIDATS_CTA)).filter(estCta).map(el => {
    const r = el.getBoundingClientRect();
    const vu = rendu(el) && visible(el) && !masqueVisuellement(el);
    let fixe = false;
    for (let n = el; n && n !== document.body; n = n.parentElement)
      if (getComputedStyle(n).position === 'fixed') { fixe = true; break; }
    return Object.assign({
      chemin: chemin(el), nom: nom(el), libelle: extrait(nomAccessible(el), 60),
      cta: el.getAttribute('data-cta') || '', position: el.getAttribute('data-cta-position') || '',
      crochet: crochet(el), dans_main: !!(main && main.contains(el)),
      visible: vu, fixe: fixe,
      pli: vu && r.width > 0 && r.height > 0 && r.top < vh && r.bottom > 0 && r.left < vw && r.right > 0,
    }, destination(el));
  });
};
"""

COLLECTEUR_PLI = "() => {" + JS_OUTILS + "\nreturn releverCtas();\n}"

# Relevé complet d'une taille d'écran, page défilée et apparitions terminées.
COLLECTEUR_VUE = "(args) => {" + JS_OUTILS + r"""
const [maxTextes, mobile] = args;
const scroller = document.scrollingElement || document.documentElement;
const vw = scroller.clientWidth;
const ovf = el => el ? getComputedStyle(el).overflowX : 'visible';

// 1. débordement horizontal
const coupeParAncetre = el => {
  for (let n = el.parentElement; n && n !== document.body && n !== document.documentElement; n = n.parentElement) {
    const o = getComputedStyle(n).overflowX;
    if (o !== 'visible') return true;
  }
  return false;
};
const fixeOuDecor = el => {
  for (let n = el; n && n !== document.body; n = n.parentElement)
    if (getComputedStyle(n).position === 'fixed') return true;
  return false;
};
const fautifs = [];
document.querySelectorAll('body *').forEach(el => {
  if (!rendu(el)) return;
  const r = el.getBoundingClientRect();
  if (r.width < 1 || r.height < 1) return;
  // seul un dépassement à droite fait défiler la page ; à gauche, il est hors d'atteinte
  if (r.right <= vw + 1) return;
  if (coupeParAncetre(el) || fixeOuDecor(el)) return;
  fautifs.push({ el: el, nom: nom(el), droite: Math.round(r.right - vw) });
});
const racines = fautifs.filter(f => !fautifs.some(g => g.el !== f.el && g.el.contains(f.el)))
  .map(f => ({ nom: f.nom, droite: f.droite }));

// 2. textes visibles (collecteur partagé de qa_common.py)
const ignorer = el => {
  if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE', 'TITLE'].includes(el.tagName)) return true;
  // texte SVG : son corps calculé est en unités du viewBox, pas en pixels rendus
  if (el.closest('svg')) return true;
  if (masqueVisuellement(el)) return true;
  const r = el.getBoundingClientRect();
  return r.right <= 0 || r.bottom + window.scrollY <= 0;
};
const extra = el => {
  const niv = [];
  for (let n = el, profondeur = 0; n && profondeur < 40; n = n.parentElement, profondeur++) {
    const cs = getComputedStyle(n);
    niv.push({ o: parseFloat(cs.opacity), r: cs.backgroundRepeat, s: cs.backgroundSize,
               b: cs.backgroundImage && cs.backgroundImage !== 'none' ? nom(n) : '' });
    if (n === document.documentElement) break;
  }
  return { niv: niv, nom: nom(el), mots: motsDe(el.textContent),
           decor: !!el.closest('[data-qa-decor]'), cache: dansAriaHidden(el) };
};
const collecte = __COLLECTE_TEXTES__;
const textes = collecte(document.body, null, { ignorer: ignorer, extra: extra, max: maxTextes });

// 3. cibles tactiles
const INTERACTIFS = 'a[href], button, input:not([type="hidden"]), select, textarea, summary, '
  + '[role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], [role="switch"]';
const cibles = [];
if (mobile) {
  document.querySelectorAll(INTERACTIFS).forEach(el => {
    if (!rendu(el) || !visible(el) || masqueVisuellement(el)) return;
    if (el.disabled || dansAriaHidden(el) || el.getAttribute('tabindex') === '-1') return;
    let r = el.getBoundingClientRect();
    if (r.right <= 0 || r.bottom + window.scrollY <= 0) return;  // hors champ (lien d'évitement)
    const cs = getComputedStyle(el);
    if (cs.display === 'inline' && el.parentElement) {
      const voisins = Array.from(el.parentElement.childNodes)
        .some(n => n.nodeType === 3 && n.textContent.trim());
      if (voisins) return;  // lien dans une phrase : exempté (WCAG 2.5.8)
    }
    if (el.tagName === 'INPUT' && ['checkbox', 'radio'].includes(el.type) && el.labels && el.labels.length) {
      const l = el.labels[0].getBoundingClientRect();
      const g = Math.min(r.left, l.left), d = Math.max(r.right, l.right);
      const h = Math.min(r.top, l.top), b = Math.max(r.bottom, l.bottom);
      r = { width: d - g, height: b - h };
    }
    cibles.push({ nom: nom(el), libelle: extrait(nomAccessible(el), 40), cta: estCta(el),
                  l: Math.round(r.width * 10) / 10, h: Math.round(r.height * 10) / 10 });
  });
}

// 4. lignes des titres, accroches et boutons (mot orphelin)
const lignesDe = bloc => {
  const mots = [];
  const marcheur = document.createTreeWalker(bloc, NodeFilter.SHOW_TEXT);
  for (let n = marcheur.nextNode(); n; n = marcheur.nextNode()) {
    const p = n.parentElement;
    if (!p || !visible(p) || masqueVisuellement(p)) continue;
    const re = /\S+/g;
    let m;
    while ((m = re.exec(n.textContent))) {
      if (!/[\p{L}\p{N}]/u.test(m[0])) continue;  // flèche, puce, tiret : pas un mot
      const plage = document.createRange();
      plage.setStart(n, m.index);
      plage.setEnd(n, m.index + m[0].length);
      const rects = Array.from(plage.getClientRects()).filter(x => x.width > 0);
      if (rects.length) mots.push(rects[0]);
    }
  }
  const lignes = [];
  mots.forEach(r => {
    const milieu = (r.top + r.bottom) / 2;
    const der = lignes[lignes.length - 1];
    if (der && Math.abs(milieu - der.milieu) < Math.max(4, r.height * 0.5)) der.n += 1;
    else lignes.push({ milieu: milieu, n: 1 });
  });
  return { total: mots.length, lignes: lignes.length, dernier: lignes.length ? lignes[lignes.length - 1].n : 0 };
};
const blocs = new Set();
document.querySelectorAll('h1, h2, h3, h4').forEach(el => blocs.add(el));
document.querySelectorAll('p').forEach(el => {
  if (/(lede|lead|intro|sub|accroche|chapo|tagline)/i.test(el.getAttribute('class') || '')) blocs.add(el);
});
document.querySelectorAll(CANDIDATS_CTA).forEach(el => { if (estCta(el)) blocs.add(el); });
const orphelins = [];
blocs.forEach(el => {
  if (!rendu(el) || !visible(el) || masqueVisuellement(el)) return;
  const l = lignesDe(el);
  if (l.lignes >= 2 && l.dernier === 1 && l.total >= 3)
    orphelins.push({ nom: nom(el), texte: extrait(el.textContent, 60) });
});

// 5. pastilles de sur-titre posées sur un titre de section
const pastille = el => {
  if (!el || !rendu(el) || !visible(el)) return false;
  const t = (el.textContent || '').trim();
  const mots = motsDe(t);
  if (!mots || mots > 6) return false;
  const cs = getComputedStyle(el);
  const r = el.getBoundingClientRect();
  if (r.height > 56 || r.height < 8) return false;
  const rayon = parseFloat(cs.borderTopLeftRadius) || 0;
  const arrondi = rayon >= 8 || rayon >= r.height * 0.3;
  const fond = cs.backgroundColor || '';
  const peint = (fond && fond !== 'transparent' && !/rgba\(\s*0,\s*0,\s*0,\s*0\s*\)/.test(fond))
                || (cs.backgroundImage && cs.backgroundImage !== 'none')
                || parseFloat(cs.borderTopWidth) > 0;
  return arrondi && peint;
};
const pastilles = [];
document.querySelectorAll('h1, h2').forEach(h => {
  if (!rendu(h)) return;
  const prec = h.previousElementSibling;
  const candidats = [prec];
  if (prec && prec.children.length === 1) candidats.push(prec.firstElementChild);
  const trouve = candidats.find(pastille);
  if (trouve) pastilles.push({ nom: nom(trouve), texte: extrait(trouve.textContent, 40), titre: extrait(h.textContent, 50) });
});

return {
  scroll_width: scroller.scrollWidth, client_width: vw,
  overflow_html: ovf(document.documentElement), overflow_body: ovf(document.body),
  debordants: racines.slice(0, 20), debordants_total: racines.length,
  textes: textes.liste, textes_total: textes.total,
  cibles: cibles, orphelins: orphelins, pastilles: pastilles,
};
}
"""

# Contrôles de la page entière : structure, alternatives, noms, champs, suivi.
COLLECTEUR_PAGE = "() => {" + JS_OUTILS + r"""
const html = document.documentElement;
const titres = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6, [role="heading"]')).map(el => ({
  niveau: el.getAttribute('aria-level') ? parseInt(el.getAttribute('aria-level'), 10)
          : (/^H[1-6]$/.test(el.tagName) ? parseInt(el.tagName.slice(1), 10) : 2),
  balise: el.tagName.toLowerCase(), nom: nom(el), texte: extrait(el.textContent, 80),
  rendu: rendu(el), aria_hidden: dansAriaHidden(el),
}));
const images = Array.from(document.querySelectorAll('img, input[type="image"]')).map(el => ({
  nom: nom(el), alt: el.hasAttribute('alt') ? el.getAttribute('alt') : null,
  src: extrait((el.getAttribute('src') || '').split('/').pop(), 60), aria_hidden: dansAriaHidden(el),
  presentation: ['presentation', 'none'].includes(el.getAttribute('role') || ''),
}));
const rolesImg = Array.from(document.querySelectorAll('[role="img"]'))
  .filter(el => !dansAriaHidden(el) && !nomAccessible(el)).map(el => ({ nom: nom(el) }));
const SANS_NOM = 'a[href], button, [role="button"], [role="link"], summary, '
  + 'input[type="submit"], input[type="button"], input[type="reset"], input[type="image"]';
const sansNom = Array.from(document.querySelectorAll(SANS_NOM))
  .filter(el => !dansAriaHidden(el) && rendu(el) && !nomAccessible(el))
  .map(el => ({ nom: nom(el), href: el.getAttribute('href') || '' }));
const CHAMPS = 'input:not([type="hidden"]):not([type="submit"]):not([type="button"]):not([type="reset"]):not([type="image"]), select, textarea';
const champs = Array.from(document.querySelectorAll(CHAMPS)).filter(el => !dansAriaHidden(el)).map(el => {
  let label = !!(el.labels && Array.from(el.labels).some(l => (l.textContent || '').trim()));
  if (!label) label = !!nomAccessible(el) && (el.hasAttribute('aria-label') || el.hasAttribute('aria-labelledby'));
  if (!label) label = !!(el.getAttribute('title') || '').trim();
  return { nom: nom(el), type: el.getAttribute('type') || el.tagName.toLowerCase(), label: label,
           placeholder: el.getAttribute('placeholder') || '' };
});
// placeholders restants : texte rendu et attributs, jamais les commentaires HTML
const restes = [];
const pousser = t => { (t || '').replace(/\{\{\s*[A-Z][A-Z0-9_]*\s*\}\}/g, m => { restes.push(m); return m; }); };
pousser(document.title);
pousser(document.body ? document.body.innerText : '');
document.querySelectorAll('[href], [src], [action], [content], [value], [alt], [placeholder], [lang], [title]')
  .forEach(el => ['href', 'src', 'action', 'content', 'value', 'alt', 'placeholder', 'lang', 'title']
    .forEach(a => { if (el.hasAttribute(a)) pousser(el.getAttribute(a)); }));
// suivi déclaré ?
const sources = Array.from(document.querySelectorAll('script[src]')).map(s => s.getAttribute('src'));
const inline = Array.from(document.querySelectorAll('script:not([src])')).map(s => s.textContent).join('\n');
let suivi = '';
if (sources.some(s => /googletagmanager\.com\/(gtag\/js|gtm\.js)/.test(s))) suivi = 'gtag.js / GTM';
else if (/dataLayer\s*=\s*(window\.)?dataLayer\s*\|\||dataLayer\s*=\s*\[/.test(inline)) suivi = 'dataLayer initialisé';
else if (/gtag\(\s*['"]config['"]/.test(inline)) suivi = "gtag('config')";
return {
  lang: html.getAttribute('lang'), titre: document.title,
  meta_viewport: !!document.querySelector('meta[name="viewport"]'),
  titres: titres, images: images, roles_img: rolesImg, sans_nom: sansNom, champs: champs,
  placeholders: restes, suivi: suivi, ctas: releverCtas(),
};
}
"""

# Mouvement réduit : textes rendus mais masqués par opacité ou visibility.
COLLECTEUR_MASQUES = "() => {" + JS_OUTILS + r"""
const causes = new Map();
document.querySelectorAll('body *').forEach(el => {
  if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName)) return;
  const propre = Array.from(el.childNodes).some(n => n.nodeType === 3 && n.textContent.trim());
  if (!propre || !rendu(el) || visible(el) || dansAriaHidden(el) || masqueVisuellement(el)) return;
  for (let n = el; n && n !== document.body; n = n.parentElement)
    if (getComputedStyle(n).position === 'fixed') return;
  const r = el.getBoundingClientRect();
  if (r.width < 1 || r.height < 1) return;
  // la cause : le plus haut ancêtre encore invisible (celui qui porte opacity: 0 ou visibility)
  let cause = el;
  for (let n = el.parentElement; n && n !== document.body; n = n.parentElement) {
    if (visible(n)) break;
    cause = n;
  }
  const cle = chemin(cause);
  if (causes.has(cle)) { causes.get(cle).textes += 1; return; }
  causes.set(cle, { chemin: cle, nom: nom(cause), texte: extrait(cause.textContent, 50), textes: 1 });
});
return Array.from(causes.values());
}
"""

COLLECTEUR_ANIMATIONS = "() => {" + JS_OUTILS + r"""
const anims = (document.getAnimations ? document.getAnimations() : [])
  .filter(a => a.playState === 'running').map(a => {
    const cible = a.effect && a.effect.target;
    const timing = a.effect && a.effect.getTiming ? a.effect.getTiming() : {};
    return { nom: cible ? nom(cible) + (a.effect.pseudoElement || '') : '?',
             chemin: cible ? chemin(cible) : '',
             genre: a.animationName ? 'animation ' + a.animationName
                    : (a.transitionProperty ? 'transition ' + a.transitionProperty : 'animation script'),
             iterations: timing.iterations === Infinity ? 'infinie' : timing.iterations };
  });
const videos = Array.from(document.querySelectorAll('video')).filter(v => !v.paused && !v.ended)
  .map(v => ({ nom: nom(v) }));
return { animations: anims, videos: videos };
}
"""

COLLECTEUR_INSTANTANE = "(max) => {" + JS_OUTILS + r"""
const out = {};
let n = 0;
for (const el of document.querySelectorAll('body *')) {
  if (n >= max) break;
  if (['SCRIPT', 'STYLE', 'NOSCRIPT', 'TEMPLATE'].includes(el.tagName)) continue;
  if (!rendu(el)) continue;
  const r = el.getBoundingClientRect();
  if (r.width < 1 || r.height < 1) continue;
  const cs = getComputedStyle(el);
  const propre = Array.from(el.childNodes).filter(x => x.nodeType === 3).map(x => x.textContent).join('').trim();
  out[chemin(el)] = { nom: nom(el), t: cs.transform + '|' + cs.translate + '|' + cs.rotate + '|' + cs.scale,
                      o: cs.opacity, x: propre.slice(0, 80) };
  n++;
}
return out;
}
"""

POLICES_PRETES = "() => document.fonts ? document.fonts.ready.then(() => true) : true"

DEFILER = r"""
async ([ratio, pause, maxPas]) => {
  const haut = () => Math.max(document.documentElement.scrollHeight, document.body ? document.body.scrollHeight : 0);
  const pas = Math.max(200, Math.floor(window.innerHeight * ratio));
  let i = 0;
  for (let y = 0; y <= haut() && i < maxPas; y += pas, i++) {
    window.scrollTo({ top: y, left: 0, behavior: 'instant' });
    await new Promise(r => setTimeout(r, pause));
  }
  window.scrollTo({ top: haut(), left: 0, behavior: 'instant' });
  await new Promise(r => setTimeout(r, pause * 4));
}
"""

# Suivi : espion posé avant tout script de la page sur `window.dataLayer`.
ESPION_SUIVI = r"""
(() => {
  const evenements = [];
  Object.defineProperty(window, '__qaEvenements', { value: evenements });
  const espionner = tableau => {
    if (!tableau || tableau.__qaEspion) return tableau;
    const pousser = tableau.push;
    tableau.push = function (...items) { items.forEach(it => evenements.push(it)); return pousser.apply(this, items); };
    Object.defineProperty(tableau, '__qaEspion', { value: true });
    return tableau;
  };
  let couche = espionner([]);
  Object.defineProperty(window, 'dataLayer', {
    configurable: true,
    get() { return couche; },
    set(v) { couche = espionner(Array.isArray(v) ? v : []); },
  });
})();
"""

CLIQUER = r"""
async ([cheminCta, attente]) => {
  const el = document.querySelector(cheminCta);
  if (!el) return { trouve: false, evenements: [] };
  const lire = it => {
    if (!it) return null;
    if (typeof it === 'object' && it.length !== undefined && it[0] === 'event') return String(it[1]);
    if (typeof it === 'object' && typeof it.event === 'string' && !/^gtm\./.test(it.event)) return it.event;
    return null;
  };
  const avant = window.__qaEvenements.length;
  const bloquer = e => e.preventDefault();
  window.addEventListener('click', bloquer, true);
  window.addEventListener('submit', bloquer, true);
  try {
    const form = el.form || el.closest('form');
    const envoi = form && ((el.tagName === 'BUTTON' && (el.getAttribute('type') || 'submit') === 'submit')
                           || (el.tagName === 'INPUT' && el.type === 'submit'));
    if (envoi) form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
    else el.click();
  } catch (e) {}
  await new Promise(r => setTimeout(r, attente));
  window.removeEventListener('click', bloquer, true);
  window.removeEventListener('submit', bloquer, true);
  return { trouve: true, evenements: window.__qaEvenements.slice(avant).map(lire).filter(Boolean) };
}
"""


# --------------------------------------------------------------------------
# Audit : valeurs relevées dans la page -> constats. Pur Python.
# --------------------------------------------------------------------------

def constat(niveau: str, type_: str, message: str, cible: str | None = None) -> dict:
    sortie = {"niveau": niveau, "type": type_, "message": message}
    if cible:
        sortie["cible"] = cible
    return sortie


def est_mobile(viewport: dict) -> bool:
    return viewport["width"] <= LARGEUR_MOBILE_MAX


def plancher_courant(viewport: dict, mobile_px: float, bureau_px: float) -> float:
    return bureau_px if viewport["width"] >= LARGEUR_BUREAU_MIN else mobile_px


def est_texture(image: str | None, repetition: str | None, taille: str | None) -> bool:
    """Un fond `url()` répété, ni étiré ni recadré : une texture (grain, points) posée sur un aplat.

    Sur un aplat opaque, la texture ne change presque pas la couleur perçue : le
    contraste se calcule contre l'aplat. Une photo (`cover`, `no-repeat`) ou un
    dégradé, eux, le rendent incalculable.
    """
    if not image or "gradient(" in image or "url(" not in image:
        return False
    if repetition and repetition.strip().startswith("no-repeat"):
        return False
    if taille and any(mot in taille for mot in ("cover", "contain")):
        return False
    return True


def niveaux_de_fond(texte: dict) -> list[dict]:
    """Fusionne la pile des fonds (collecteur de qa_common) avec les relevés propres à ce script.

    Chaque niveau porte sa couleur (`c`), son image (`i`), son opacité (`o`) et le
    nom de l'élément qui peint l'image (`b`). Une texture répétée posée sur un
    aplat opaque est ramenée à cet aplat (`i` = none).
    """
    fonds = texte.get("fonds") or []
    extra = texte.get("niv") or []
    niveaux = []
    for k, fond in enumerate(fonds):
        niveau = {"c": fond.get("c"), "i": fond.get("i"), "o": 1.0, "b": ""}
        if k < len(extra):
            niveau["o"] = extra[k].get("o")
            niveau["b"] = extra[k].get("b") or ""
            if not qa_common.fond_uni(niveau["i"]):
                couleur = qa_common.lire_couleur(niveau["c"])
                if (couleur is not None and couleur[3] >= 1.0
                        and est_texture(niveau["i"], extra[k].get("r"), extra[k].get("s"))):
                    niveau["i"] = "none"
        niveaux.append(niveau)
    return niveaux


def couleurs_du_degrade(image: str) -> list[tuple]:
    """Les arrêts de couleur d'un `background-image` calculé (tous calques confondus)."""
    return [c for c in (qa_common.lire_couleur(m) for m in RE_COULEURS.findall(image or ""))
            if c is not None]


def fonds_possibles(niveaux: list[dict]) -> tuple[list[tuple], str | None, str]:
    """Couleurs de fond possibles derrière un texte, du texte vers la racine.

    Rend `(candidats, raison, porteur)` :
      - aplat : un seul candidat ;
      - dégradé : un candidat par arrêt de couleur, composé sur ce qu'il y a dessous.
        Le contraste se juge alors au pire et au meilleur point du dégradé ;
      - photo ou image non répétée : aucun candidat, `raison` = "photo" ;
    `porteur` nomme l'élément qui peint le dégradé ou la photo.
    """
    calques: list[tuple] = []
    candidats: list[tuple] = [(255, 255, 255)]
    porteur = ""
    for k, niveau in enumerate(niveaux):
        image = niveau.get("i")
        couleur = qa_common.lire_couleur(niveau.get("c"))
        if not qa_common.fond_uni(image):
            porteur = niveau.get("b") or ""
            if "url(" in image:
                return [], "photo", porteur
            if couleur is not None and couleur[3] >= 1.0:
                bases = [couleur[:3]]
            else:
                bases, raison, dessous = fonds_possibles(niveaux[k + 1:])
                if raison:
                    return [], raison, dessous
                if couleur is not None and couleur[3] > 0:
                    bases = [qa_common.aplatir(couleur, b) for b in bases]
            arrets = couleurs_du_degrade(image)
            candidats = sorted({qa_common.aplatir(a, b) for a in arrets for b in bases}) or bases
            break
        if couleur is None or couleur[3] == 0.0:
            continue
        if couleur[3] >= 1.0:
            candidats = [couleur[:3]]
            break
        calques.append(couleur)
    for calque in reversed(calques):
        candidats = [qa_common.aplatir(calque, c) for c in candidats]
    return candidats, None, porteur


def auditer_textes(textes: list[dict], viewport: dict, planchers: dict,
                   familles: list[str]) -> tuple[list[dict], list[str]]:
    """Planchers, police et contraste des textes visibles d'une taille d'écran.

    Les textes posés sur un même dégradé ou une même photo se regroupent en un seul
    constat par fond : un constat par texte noierait le rapport.
    """
    constats: list[dict] = []
    gradients: list[str] = []
    photos: dict[str, list[str]] = {}
    degrades: dict[str, list[tuple]] = {}
    courant = plancher_courant(viewport, planchers["courant"], planchers["courant_bureau"])

    for texte in textes:
        cible = texte.get("nom") or texte.get("tag", "?").lower()
        extrait = (texte.get("texte") or "")[:40]
        taille = float(texte.get("fs") or 0)
        mots = int(texte.get("mots") or 0)
        gras = int(texte.get("poids") or 400) >= 700
        if texte.get("decor"):
            continue  # illustration composée en HTML (data-qa-decor) : ni plancher, ni contraste, ni police

        if texte.get("cache"):
            pass  # scène aria-hidden doublée d'un équivalent lisible : pas de plancher, le contraste reste
        elif taille < planchers["etiquette"] - TOLERANCE_PX:
            constats.append(constat(
                "erreur", "plancher-typo",
                f"{taille:g}px sous le plancher des étiquettes {planchers['etiquette']:g}px "
                f"sur {cible} « {extrait} »", cible))
        elif mots >= MOTS_TEXTE_COURANT and taille < planchers["courant"] - TOLERANCE_PX:
            constats.append(constat(
                "erreur", "plancher-typo",
                f"{taille:g}px sous le plancher du texte courant {planchers['courant']:g}px "
                f"({mots} mots) sur {cible} « {extrait} »", cible))
        elif mots >= MOTS_TEXTE_COURANT and taille < courant - TOLERANCE_PX:
            constats.append(constat(
                "avertissement", "plancher-typo",
                f"{taille:g}px sous les {courant:g}px recommandés pour le texte courant sur "
                f"bureau ({mots} mots) sur {cible} « {extrait} »", cible))

        if familles:
            mono = texte.get("tag") in ("CODE", "PRE", "KBD", "SAMP")
            if not qa_common.police_conforme(texte.get("police"), familles, mono_autorise=mono):
                constats.append(constat(
                    "erreur", "police",
                    f"police « {qa_common.premiere_famille(texte.get('police'))} » au lieu de "
                    f"{' / '.join(familles)} sur {cible}", cible))

        if texte.get("gradient"):
            gradients.append(f"{cible} « {extrait} »")
            continue

        niveaux = niveaux_de_fond(texte)
        candidats, raison, porteur = fonds_possibles(niveaux)
        if raison:
            photos.setdefault(porteur or "?", []).append(f"{cible} « {extrait} »")
            continue
        couleur = qa_common.lire_couleur(texte.get("couleur"))
        if couleur is None:
            continue
        opacite = qa_common.opacite_effective(niveaux)
        ratios = [qa_common.contraste(
                      qa_common.aplatir((couleur[0], couleur[1], couleur[2], couleur[3] * opacite), fond), fond)
                  for fond in candidats]
        pire, meilleur = min(ratios), max(ratios)
        seuil = qa_common.seuil_contraste(taille, gras=gras)
        estompe = f", opacité {opacite:.2f}" if opacite < 0.995 else ""
        if meilleur < seuil:
            partout = ", à tous les arrêts du dégradé" if len(candidats) > 1 else ""
            constats.append(constat(
                "erreur", "contraste",
                f"contraste {meilleur:.2f}:1 sous {seuil:g}:1 sur {cible} « {extrait} » "
                f"({taille:g}px{estompe}{partout})", cible))
        elif pire < seuil:
            degrades.setdefault(porteur or "?", []).append((pire, seuil, cible, extrait))

    for porteur, liste in photos.items():
        constats.append(constat(
            "avertissement", "contraste",
            f"{len(liste)} texte(s) sur l'image de fond de {porteur} : contraste non calculable, "
            f"à vérifier au pire endroit (ex. {liste[0]})", porteur))
    for porteur, liste in degrades.items():
        pire, seuil, cible, extrait = min(liste)
        constats.append(constat(
            "avertissement", "contraste",
            f"{len(liste)} texte(s) sous le seuil au pire point du dégradé de {porteur} "
            f"(pire : {pire:.2f}:1 pour {seuil:g}:1 sur {cible} « {extrait} ») : "
            f"vérifier là où le texte se pose", porteur))
    return constats, gradients


def auditer_debordement(releve: dict) -> list[dict]:
    largeur, contenu = releve["client_width"], releve["scroll_width"]
    racines = releve.get("debordants") or []
    noms = ", ".join(f"{d['nom']} (+{d['droite']}px)" for d in racines[:5])
    masque = any(o in ("hidden", "clip") for o in (releve.get("overflow_html"), releve.get("overflow_body")))
    if contenu > largeur + 1 and not masque:
        return [constat("erreur", "debordement",
                        f"la page défile horizontalement : {contenu}px de contenu pour {largeur}px"
                        + (f" ; en cause : {noms}" if noms else ""))]
    if racines:
        return [constat("avertissement", "debordement-masque",
                        f"{releve.get('debordants_total', len(racines))} élément(s) dépassent la largeur, "
                        f"cachés par overflow-x sur html ou body : {noms}")]
    return []


def auditer_cibles(cibles: list[dict]) -> list[dict]:
    constats = []
    for c in cibles:
        cote = min(c["l"], c["h"])
        desc = f"{c['nom']} « {c['libelle']} » {c['l']:g}×{c['h']:g}px"
        if cote < CIBLE_MIN_PX:
            constats.append(constat("erreur", "cible-tactile",
                                    f"cible sous {CIBLE_MIN_PX:g}px (WCAG 2.5.8) : {desc}", c["nom"]))
        elif cote < CIBLE_CONFORT_PX:
            if c.get("cta"):
                constats.append(constat("erreur", "cible-tactile",
                                        f"CTA sous {CIBLE_CONFORT_PX:g}px sur mobile : {desc}", c["nom"]))
            else:
                constats.append(constat("avertissement", "cible-tactile",
                                        f"cible sous {CIBLE_CONFORT_PX:g}px recommandés : {desc}", c["nom"]))
    return constats


def auditer_orphelins(orphelins: list[dict]) -> list[dict]:
    return [constat("avertissement", "mot-orphelin",
                    f"dernière ligne d'un seul mot sur {o['nom']} « {o['texte']} » : "
                    f"couper autrement ou équilibrer (text-wrap: balance)", o["nom"])
            for o in orphelins]


def auditer_troncature(releve: dict) -> list[dict]:
    reste = releve["textes_total"] - len(releve["textes"])
    if reste > 0:
        return [constat("avertissement", "troncature",
                        f"{reste} textes non audités ({releve['textes_total']} trouvés, "
                        f"{len(releve['textes'])} relevés)")]
    return []


# --- CTA ---------------------------------------------------------------------

def cle_cta(cta: dict) -> str:
    if cta["genre"] == "ancre":
        return "ancre:" + (cta.get("dest") or "")
    if cta["genre"] == "envoi":
        return "form:" + cta.get("formulaire", "")
    if cta["genre"] == "lien":
        return "lien:" + (cta.get("dest") or "")
    return "script:" + cta["chemin"]


def cta_primaire(ctas: list[dict]) -> tuple[dict | None, str]:
    """Le CTA de référence de la page, et la règle qui l'a désigné."""
    explicites = [c for c in ctas if c.get("cta", "").lower() in ("primaire", "primary")]
    if explicites:
        return explicites[0], 'data-cta="primaire"'
    hero = [c for c in ctas if c.get("position", "").lower() == "hero"]
    if hero:
        return hero[0], 'premier data-cta-position="hero"'
    dans_main = [c for c in ctas if c.get("dans_main")]
    if dans_main:
        return dans_main[0], "premier CTA de <main>"
    if ctas:
        return ctas[0], "premier CTA de la page"
    return None, ""


def cles_primaires(primaire: dict, ctas: list[dict]) -> set[str]:
    """Destinations équivalentes à celle du CTA primaire.

    Une ancre vers le bloc qui contient un formulaire et le bouton d'envoi de ce
    formulaire mènent à la même conversion : elles comptent ensemble.
    """
    cles = {cle_cta(primaire)}
    if primaire["genre"] == "ancre":
        cles.update("form:" + f for f in primaire.get("formulaires") or [])
    if primaire["genre"] == "envoi":
        cles.update("ancre:#" + i for i in primaire.get("ancetres") or [])
    for cta in ctas:  # une seconde ancre vers le même formulaire, sous un autre id
        if cta["genre"] == "ancre" and any("form:" + f in cles for f in cta.get("formulaires") or []):
            cles.add(cle_cta(cta))
    return cles


def auditer_ctas(ctas: list[dict]) -> tuple[list[dict], set[str], dict | None, str]:
    """Inventaire : destinations, CTA primaires, CTA hors objectif."""
    constats: list[dict] = []
    if not ctas:
        constats.append(constat("erreur", "cta-absent",
                                "aucun CTA repéré : poser au moins un bouton ou un lien d'action "
                                '(data-cta="primaire" pour le principal)'))
        return constats, set(), None, ""

    for cta in ctas:
        desc = f"{cta['nom']} « {cta['libelle']} »"
        dest = cta.get("dest")
        if cta.get("defaut"):
            constats.append(constat("erreur", "cta-destination",
                                    f"{desc} : {cta['defaut']} ({dest!r})", cta["nom"]))
        elif cta["genre"] == "ancre" and not cta.get("cible_existe"):
            constats.append(constat("erreur", "cta-destination",
                                    f"{desc} : l'ancre {dest} ne mène à aucun id de la page", cta["nom"]))
        elif dest and RE_PLACEHOLDER.search(dest):
            constats.append(constat("avertissement", "cta-destination",
                                    f"{desc} : destination encore en placeholder ({dest}), "
                                    f"à brancher avant publication", cta["nom"]))
        elif cta["genre"] == "envoi" and not (dest or "").strip():
            constats.append(constat("avertissement", "cta-destination",
                                    f"{desc} : formulaire sans action, l'envoi doit être géré en "
                                    f"script (à vérifier)", cta["nom"]))

    primaire, regle = cta_primaire(ctas)
    cles = cles_primaires(primaire, ctas)
    for cta in ctas:
        cta["primaire"] = cle_cta(cta) in cles
    for cta in ctas:
        # une ancre de la page (« voir le programme ») guide la lecture, elle ne détourne pas
        if not cta["primaire"] and cta["genre"] not in ("script", "ancre"):
            constats.append(constat(
                "avertissement", "cta-hors-objectif",
                f"{cta['nom']} « {cta['libelle']} » mène à {cta.get('dest') or cta['genre']}, "
                f"pas à la conversion primaire ({primaire.get('dest') or primaire['genre']}) : "
                f"une page, un objectif", cta["nom"]))
    return constats, cles, primaire, regle


def auditer_page(page: dict, pastilles: list[dict]) -> list[dict]:
    """Structure, alternatives, noms, champs, placeholders, titres, pastilles."""
    constats: list[dict] = []

    lang = (page.get("lang") or "").strip()
    if not lang:
        constats.append(constat("erreur", "lang", "<html> sans attribut lang : la langue de la page "
                                                  "n'est pas annoncée aux lecteurs d'écran"))
    elif not RE_LANG.match(lang):
        constats.append(constat("erreur", "lang", f"lang=\"{lang}\" n'est pas un code de langue valide"))
    if not page.get("meta_viewport"):
        constats.append(constat("erreur", "meta-viewport",
                                '<meta name="viewport" content="width=device-width, initial-scale=1"> '
                                "absent : le rendu mobile est faux"))
    if not (page.get("titre") or "").strip():
        constats.append(constat("erreur", "titre-page", "<title> absent ou vide"))

    titres = [t for t in page.get("titres") or [] if t["rendu"] and not t["aria_hidden"]]
    h1 = [t for t in titres if t["niveau"] == 1]
    if len(h1) != 1:
        detail = "aucun h1" if not h1 else f"{len(h1)} h1 : " + " ; ".join(f"« {t['texte'][:40]} »" for t in h1)
        constats.append(constat("erreur", "titres-h1", f"une page porte un seul h1 ({detail})"))
    precedent = None
    for t in titres:
        if precedent is not None and t["niveau"] > precedent + 1:
            constats.append(constat("erreur", "titres-ordre",
                                    f"h{precedent} puis h{t['niveau']} : niveau sauté avant "
                                    f"« {t['texte'][:50]} »", t["nom"]))
        precedent = t["niveau"]
    for t in titres:
        if t["niveau"] > 4 or t["balise"] not in ("h1", "h2", "h3", "h4"):
            continue
        texte = t["texte"].strip()
        # une virgule entre deux chiffres est une décimale, pas une ponctuation
        if (texte.endswith(".") and not texte.endswith("..")) or re.search(r"(?<!\d),|,(?!\d)", texte):
            constats.append(constat("avertissement", "titre-ponctuation",
                                    f"titre avec virgule ou point final : « {texte[:60]} » "
                                    f"(reformuler ou passer à la ligne)", t["nom"]))

    for img in page.get("images") or []:
        if img["aria_hidden"] or img["presentation"]:
            continue
        if img["alt"] is None:
            constats.append(constat("erreur", "image-alt",
                                    f"{img['nom']} ({img['src']}) sans attribut alt : décrire l'image, "
                                    f'ou alt="" si elle est décorative', img["nom"]))
        elif RE_ALT_FICHIER.search(img["alt"].strip()):
            constats.append(constat("avertissement", "image-alt",
                                    f"{img['nom']} : alt « {img['alt']} » ressemble à un nom de fichier",
                                    img["nom"]))
    for el in page.get("roles_img") or []:
        constats.append(constat("erreur", "image-alt", f'{el["nom"]} role="img" sans nom accessible',
                                el["nom"]))

    for el in page.get("sans_nom") or []:
        constats.append(constat("erreur", "nom-accessible",
                                f"{el['nom']} sans nom accessible (texte, aria-label ou alt d'image)"
                                + (f", href {el['href']}" if el["href"] else ""), el["nom"]))

    for champ in page.get("champs") or []:
        if not champ["label"]:
            indice = f" (placeholder « {champ['placeholder']} » : ce n'est pas un label)" \
                if champ["placeholder"] else ""
            constats.append(constat("erreur", "champ-sans-label",
                                    f"{champ['nom']} [{champ['type']}] sans label associé{indice}",
                                    champ["nom"]))

    restes = page.get("placeholders") or []
    if restes:
        distincts = sorted(set(restes))
        constats.append(constat("avertissement", "placeholder",
                                f"{len(restes)} placeholder(s) restant(s) : {', '.join(distincts[:6])}"
                                + (" …" if len(distincts) > 6 else "")
                                + " (à remplacer avant publication)"))

    vus = set()
    for p in pastilles:
        if p["nom"] + p["titre"] in vus:
            continue
        vus.add(p["nom"] + p["titre"])
        constats.append(constat("avertissement", "surtitre-pastille",
                                f"pastille de sur-titre {p['nom']} « {p['texte']} » au-dessus de "
                                f"« {p['titre']} » : l'en-tête commence par son titre", p["nom"]))
    return constats


def auditer_suivi(suivi: str, primaires: list[dict], clics: dict | None) -> list[dict]:
    """Suivi déclaré : un événement part au clic. Sinon : le crochet data-track est posé."""
    constats: list[dict] = []
    if suivi:
        for cta in primaires:
            resultat = (clics or {}).get(cta["chemin"])
            if resultat is None:
                continue
            if resultat.get("evenements"):
                cta["evenements"] = resultat["evenements"]
                continue
            if cta["genre"] == "envoi":
                constats.append(constat(
                    "avertissement", "tracking",
                    f"{cta['nom']} « {cta['libelle']} » : aucun événement à l'envoi du formulaire "
                    f"(il peut partir après la réponse du serveur : à vérifier en préproduction)",
                    cta["nom"]))
            else:
                constats.append(constat(
                    "erreur", "tracking",
                    f"{cta['nom']} « {cta['libelle']} » : suivi déclaré ({suivi}) mais aucun "
                    f"événement dataLayer / gtag au clic", cta["nom"]))
    else:
        if primaires and not any(c.get("crochet") for c in primaires):
            constats.append(constat(
                "avertissement", "tracking",
                "aucun crochet de suivi (data-track) sur les CTA primaires : la skill landing-page "
                "le pose même sans GA4, pour brancher la mesure sans retoucher le HTML"))
    return constats


def auditer_mouvement(masques_charge: list[dict], masques_apres: list[dict],
                      masques_normal: set[str], anims: dict,
                      avant: dict, apres: dict) -> list[dict]:
    """prefers-reduced-motion : tout est visible d'emblée, rien ne bouge."""
    constats: list[dict] = []
    apres_chemins = {m["chemin"] for m in masques_apres}

    def combien(m: dict) -> str:
        return f" ({m['textes']} textes)" if m.get("textes", 1) > 1 else ""

    for m in masques_apres:
        if m["chemin"] in masques_normal:
            continue  # masqué aussi sans préférence : menu fermé, onglet inactif, voulu
        constats.append(constat(
            "erreur", "mouvement-reduit-masque",
            f"{m['nom']} « {m['texte']} »{combien(m)} reste masqué avec prefers-reduced-motion "
            f"(visible sans la préférence)", m["nom"]))
    for m in masques_charge:
        if m["chemin"] in apres_chemins or m["chemin"] in masques_normal:
            continue
        constats.append(constat(
            "avertissement", "mouvement-reduit-apparition",
            f"{m['nom']} « {m['texte']} »{combien(m)} n'apparaît qu'au défilement avec "
            f"prefers-reduced-motion : afficher l'état final d'emblée", m["nom"]))

    for a in anims.get("animations") or []:
        constats.append(constat(
            "erreur", "mouvement-reduit-anime",
            f"{a['genre']} en cours sur {a['nom']} (itérations : {a['iterations']}) malgré "
            f"prefers-reduced-motion : animation: none, ou une seule itération", a["nom"]))
    for v in anims.get("videos") or []:
        constats.append(constat(
            "erreur", "mouvement-reduit-anime",
            f"vidéo {v['nom']} en lecture automatique malgré prefers-reduced-motion", v["nom"]))

    deja = {a.get("chemin") for a in anims.get("animations") or []}
    for chemin, etat in avant.items():
        suite = apres.get(chemin)
        if not suite or chemin in deja:
            continue
        if etat["t"] != suite["t"] or etat["o"] != suite["o"]:
            constats.append(constat(
                "erreur", "mouvement-reduit-anime",
                f"{etat['nom']} bouge encore (transform ou opacité pilotés par script) malgré "
                f"prefers-reduced-motion", etat["nom"]))
        elif etat["x"] != suite["x"] and etat["x"] and suite["x"]:
            if re.search(r"\d", etat["x"]) and re.search(r"\d", suite["x"]):
                constats.append(constat(
                    "avertissement", "compte-a-rebours",
                    f"{etat['nom']} change seul (« {etat['x'][:30]} » → « {suite['x'][:30]} ») : "
                    f"l'urgence honnête se compte en jours, jamais en secondes", etat["nom"]))
            else:
                constats.append(constat(
                    "erreur", "mouvement-reduit-anime",
                    f"{etat['nom']} change de texte seul (« {etat['x'][:30]} » → « {suite['x'][:30]} ») "
                    f"malgré prefers-reduced-motion", etat["nom"]))
    return constats


# --------------------------------------------------------------------------
# Totaux et plafond
# --------------------------------------------------------------------------

def compter(constats: list[dict], niveau: str) -> int:
    """Les lignes de résumé ne comptent jamais."""
    return sum(1 for c in constats if c["niveau"] == niveau)


def plafonner(constats: list[dict], limite: int = MAX_PAR_TYPE) -> list[dict]:
    """Garde au plus `limite` constats par type ; le reste devient une ligne `resume`."""
    if not limite or limite <= 0:
        return list(constats)
    gardes, vus, caches = [], {}, {}
    for c in constats:
        vus[c["type"]] = vus.get(c["type"], 0) + 1
        if vus[c["type"]] <= limite:
            gardes.append(c)
        else:
            caches[c["type"]] = caches.get(c["type"], 0) + 1
    for type_, nombre in caches.items():
        gardes.append({"niveau": "resume", "type": type_, "masques": nombre,
                       "message": f"… {nombre} constat(s) « {type_} » de plus, non listés"})
    return gardes


def par_type(constats: list[dict]) -> dict[str, dict[str, int]]:
    sortie: dict[str, dict[str, int]] = {}
    for c in constats:
        if c["niveau"] not in ("erreur", "avertissement"):
            continue
        entree = sortie.setdefault(c["type"], {"errors": 0, "warnings": 0})
        entree["errors" if c["niveau"] == "erreur" else "warnings"] += 1
    return dict(sorted(sortie.items()))


# --------------------------------------------------------------------------
# Navigateur
# --------------------------------------------------------------------------

def lire_viewports(valeur: str) -> list[dict]:
    tailles = []
    for morceau in [v for v in valeur.split(",") if v.strip()]:
        try:
            tailles.append(qa_common.lire_viewport(morceau.strip()))
        except ValueError as err:
            raise ErreurUsage(str(err)) from err
    if not tailles:
        raise ErreurUsage("--viewports : au moins une taille LARGEURxHAUTEUR")
    return tailles


def texte_viewport(viewport: dict) -> str:
    return f"{viewport['width']}x{viewport['height']}"


def collecteur_vue() -> str:
    return COLLECTEUR_VUE.replace("__COLLECTE_TEXTES__", qa_common.JS_TEXTES.strip())


def passe_vue(navigateur, url: str, viewport: dict, attente: int, capture: Path | None) -> dict:
    """Une taille d'écran : pli, défilement complet, état final."""
    contexte = navigateur.new_context(viewport=viewport, reduced_motion="no-preference")
    try:
        page = contexte.new_page()
        page.goto(url, wait_until="load")
        page.evaluate(POLICES_PRETES)
        page.wait_for_timeout(attente)
        pli = page.evaluate(COLLECTEUR_PLI)
        page.add_style_tag(content=SETTLE_CSS)
        page.evaluate(DEFILER, [0.7, 60, 400])
        page.wait_for_timeout(300)
        releve = page.evaluate(collecteur_vue(), [MAX_TEXTES, est_mobile(viewport)])
        releve["pli"] = pli
        releve["page"] = page.evaluate(COLLECTEUR_PAGE)
        releve["masques"] = page.evaluate(COLLECTEUR_MASQUES)
        if capture:
            capture.mkdir(parents=True, exist_ok=True)
            page.evaluate("() => window.scrollTo({ top: 0, behavior: 'instant' })")
            page.screenshot(path=str(capture / f"vue-{texte_viewport(viewport)}.png"), full_page=True)
        return releve
    finally:
        contexte.close()


def passe_mouvement(navigateur, url: str, viewport: dict, attente: int) -> dict:
    """prefers-reduced-motion : masqués au chargement, après défilement, animations, instantanés."""
    contexte = navigateur.new_context(viewport=viewport, reduced_motion="reduce")
    try:
        page = contexte.new_page()
        page.goto(url, wait_until="load")
        page.evaluate(POLICES_PRETES)
        page.wait_for_timeout(attente)
        masques_charge = page.evaluate(COLLECTEUR_MASQUES)
        page.evaluate(DEFILER, [0.7, 60, 400])
        page.wait_for_timeout(600)
        masques_apres = page.evaluate(COLLECTEUR_MASQUES)
        anims = page.evaluate(COLLECTEUR_ANIMATIONS)
        avant = page.evaluate(COLLECTEUR_INSTANTANE, 4000)
        page.wait_for_timeout(OBSERVATION_MS)
        apres = page.evaluate(COLLECTEUR_INSTANTANE, 4000)
        return {"charge": masques_charge, "apres": masques_apres, "anims": anims,
                "avant": avant, "apres_instantane": apres}
    finally:
        contexte.close()


def passe_suivi(navigateur, url: str, viewport: dict, attente: int, chemins: list[str]) -> dict:
    """Clique chaque CTA primaire, navigation empêchée et réseau coupé hors fichiers locaux."""
    contexte = navigateur.new_context(viewport=viewport, reduced_motion="reduce")
    resultats: dict = {}
    try:
        contexte.route("**/*", lambda route: route.continue_()
                       if route.request.url.startswith("file:") else route.abort())
        contexte.add_init_script(ESPION_SUIVI)
        page = contexte.new_page()
        page.goto(url, wait_until="load")
        page.wait_for_timeout(attente)
        for chemin in chemins:
            try:
                resultats[chemin] = page.evaluate(CLIQUER, [chemin, CLIC_MS])
            except Exception:  # noqa: BLE001 - une navigation forcée a détruit la page
                page = contexte.new_page()
                page.goto(url, wait_until="load")
                page.wait_for_timeout(attente)
                resultats[chemin] = {"trouve": True, "evenements": []}
        return resultats
    finally:
        contexte.close()


# --------------------------------------------------------------------------
# Rapport
# --------------------------------------------------------------------------

MARQUE = {"erreur": "!", "avertissement": "~"}


def imprimer_bloc(titre: str, constats: list[dict]) -> None:
    if not constats:
        print(f"  {titre} · ok")
        return
    print(f"  {titre} · {compter(constats, 'erreur')} erreur(s), "
          f"{compter(constats, 'avertissement')} avertissement(s)")
    for c in constats:
        print(f"    {MARQUE.get(c['niveau'], '+')} [{c['type']}] {c['message']}")


def rapport_texte(sortie: dict) -> None:
    resume = sortie["summary"]
    print(f"qa  · landing   {resume['fichier']}")
    print(f"qa  · écrans    {' · '.join(resume['viewports'])} "
          f"(mouvement réduit : {resume['mouvement_reduit']})")
    p = resume["planchers"]
    print(f"qa  · planchers étiquettes {p['etiquette']:g}px · texte courant ({p['mots_texte_courant']} mots "
          f"et plus) {p['courant']:g}px, {p['courant_bureau']:g}px dès {LARGEUR_BUREAU_MIN}px · "
          f"cibles mobiles {CIBLE_MIN_PX:g}/{CIBLE_CONFORT_PX:g}px")
    print(f"qa  · polices   {' / '.join(resume['polices']) or 'non contrôlées (ni tokens.json ni --police)'}")
    print(f"qa  · suivi     {resume['tracking'] or 'non déclaré (crochets data-track contrôlés)'}")
    primaire = resume.get("cta_primaire") or {}
    print(f"qa  · CTA       {resume['ctas']} repérés, {resume['ctas_primaires']} primaires"
          + (f" → {primaire.get('destination')} ({primaire.get('regle')})" if primaire else "") + "\n")

    imprimer_bloc("page", sortie["page"])
    for vue in sortie["viewports"]:
        imprimer_bloc(vue["viewport"] + (" mobile" if vue["mobile"] else ""), vue["constats"])
    imprimer_bloc(f"mouvement réduit {resume['mouvement_reduit']}", sortie["mouvement_reduit"]["constats"])

    if sortie["gradient_text"]:
        print("\n  texte en dégradé (background-clip: text), contraste non jugé, à relire à l'œil :")
        for ligne in sortie["gradient_text"][:12]:
            print(f"    · {ligne}")

    print()
    erreurs, avertissements = resume["errors"], resume["warnings"]
    if erreurs:
        print(f"FAIL · {erreurs} erreur(s), {avertissements} avertissement(s)")
    else:
        print("Landing clean" + (f" · {avertissements} avertissement(s)" if avertissements else ""))
    if (resume["errors_total"], resume["warnings_total"]) != (erreurs, avertissements):
        print(f"     · avant plafond de {resume['max_par_type']} par type et par bloc : "
              f"{resume['errors_total']} erreur(s), {resume['warnings_total']} avertissement(s)")
    if resume["by_type"] and (erreurs or avertissements):
        morceaux = []
        for type_, n in resume["by_type"].items():
            bouts = [f"{n['errors']} err" if n["errors"] else "", f"{n['warnings']} avert" if n["warnings"] else ""]
            morceaux.append(f"{type_} " + " ".join(b for b in bouts if b))
        print("     · par type : " + " · ".join(morceaux))


# --------------------------------------------------------------------------
# Programme
# --------------------------------------------------------------------------

def construire_parseur() -> argparse.ArgumentParser:
    parseur = argparse.ArgumentParser(
        description="QA Playwright d'une landing page HTML statique : débordement, planchers "
                    "typographiques, contraste, titres, alternatives, noms accessibles, cibles "
                    "tactiles, CTA et pli mobile, mouvement réduit, langue, champs, suivi.",
    )
    parseur.add_argument("fichier", help="page HTML à contrôler (index.html autonome)")
    parseur.add_argument("--viewports", default=VIEWPORTS_DEFAUT,
                         help=f"tailles d'écran, séparées par des virgules (défaut : {VIEWPORTS_DEFAUT}). "
                              f"Sous {LARGEUR_MOBILE_MAX + 1}px de large, un écran est mobile : cibles "
                              f"tactiles et CTA au-dessus du pli y sont contrôlés")
    parseur.add_argument("--plancher-etiquette", type=float, default=PLANCHER_ETIQUETTE_PX,
                         help=f"plancher de tout texte visible, en px (défaut : {PLANCHER_ETIQUETTE_PX:g})")
    parseur.add_argument("--plancher-courant", type=float, default=PLANCHER_COURANT_PX,
                         help=f"plancher du texte courant ({MOTS_TEXTE_COURANT} mots et plus) sous "
                              f"{LARGEUR_BUREAU_MIN}px de large (défaut : {PLANCHER_COURANT_PX:g})")
    parseur.add_argument("--plancher-courant-bureau", type=float, default=PLANCHER_COURANT_BUREAU_PX,
                         help=f"plancher du texte courant à partir de {LARGEUR_BUREAU_MIN}px de large "
                              f"(défaut : {PLANCHER_COURANT_BUREAU_PX:g})")
    parseur.add_argument("--tokens", default=str(RACINE / "01-brand" / "tokens.json"),
                         help="tokens DTCG d'où lire les familles de police de la marque (défaut : "
                              "01-brand/tokens.json ; absent, la police n'est pas contrôlée)")
    parseur.add_argument("--police", action="append", default=[], metavar="FAMILLE",
                         help="famille de police admise, à la place de celles de tokens.json. Répétable")
    parseur.add_argument("--tracking", choices=("auto", "oui", "non"), default="auto",
                         help="la page déclare-t-elle un suivi d'audience ? auto : détecté (gtag.js, "
                              "GTM, dataLayer initialisé, gtag('config')). oui : cliquer les CTA "
                              "primaires et exiger un événement. non : contrôler seulement les "
                              "crochets data-track")
    parseur.add_argument("--attente", type=int, default=ATTENTE_MS, metavar="MS",
                         help=f"attente après chargement, en ms (défaut : {ATTENTE_MS})")
    parseur.add_argument("--max-par-type", type=int, default=MAX_PAR_TYPE, metavar="N",
                         help=f"constats listés par type et par bloc (défaut : {MAX_PAR_TYPE}, 0 = tout). "
                              "Les totaux sont toujours calculés avant plafond")
    parseur.add_argument("--format", choices=("text", "json"), default="text",
                         help="forme de la sortie (défaut : text)")
    parseur.add_argument("--captures", metavar="DOSSIER",
                         help="enregistrer une capture pleine page par taille d'écran (hors du dépôt)")
    return parseur


def familles_de_police(args: argparse.Namespace) -> list[str]:
    if args.police:
        return list(args.police)
    chemin = Path(args.tokens)
    if not chemin.is_file():
        return []
    try:
        return qa_common.familles_de_marque(qa_common.lire_tokens(chemin))
    except ValueError as err:
        raise ErreurUsage(str(err)) from err


def executer(args: argparse.Namespace) -> int:
    cible = Path(args.fichier)
    if not cible.is_file():
        raise ErreurUsage(f"fichier introuvable : {cible}")
    viewports = lire_viewports(args.viewports)
    planchers = {"etiquette": args.plancher_etiquette, "courant": args.plancher_courant,
                 "courant_bureau": args.plancher_courant_bureau, "mots_texte_courant": MOTS_TEXTE_COURANT}
    familles = familles_de_police(args)
    capture = Path(args.captures) if args.captures else None

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as err:
        raise ErreurUsage("Playwright n'est pas installé. Lancer :\n"
                          "  pip install playwright && playwright install chromium") from err

    url = cible.resolve().as_uri()
    large = max(viewports, key=lambda v: v["width"])
    releves: list[tuple[dict, dict]] = []
    with sync_playwright() as playwright:
        navigateur = playwright.chromium.launch()
        try:
            for viewport in viewports:
                releves.append((viewport, passe_vue(navigateur, url, viewport, args.attente, capture)))
            mouvement = passe_mouvement(navigateur, url, large, args.attente)

            releve_large = next(r for v, r in releves if v is large)
            page = releve_large["page"]
            ctas = page["ctas"]
            constats_cta, cles, primaire, regle = auditer_ctas(ctas)
            primaires = [c for c in ctas if c.get("primaire")]
            suivi = {"auto": page.get("suivi") or "", "oui": page.get("suivi") or "forcé (--tracking oui)",
                     "non": ""}[args.tracking]
            clics = None
            if suivi and primaires:
                clics = passe_suivi(navigateur, url, large, args.attente, [c["chemin"] for c in primaires])
        finally:
            navigateur.close()

    # ---- page ----
    pastilles = releve_large.get("pastilles") or []
    constats_page = auditer_page(page, pastilles) + constats_cta + auditer_suivi(suivi, primaires, clics)

    # ---- tailles d'écran ----
    vues, gradients, non_plafonnes = [], [], list(constats_page)
    for viewport, releve in releves:
        constats = auditer_debordement(releve)
        textes, grads = auditer_textes(releve["textes"], viewport, planchers, familles)
        constats += textes
        gradients.extend(f"{texte_viewport(viewport)} · {g}" for g in grads)
        if est_mobile(viewport):
            constats += auditer_cibles(releve["cibles"])
            pli = {c["chemin"] for c in releve["pli"] if c["pli"]}
            if primaires and not any(c["chemin"] in pli for c in primaires):
                constats.append(constat(
                    "erreur", "cta-pli",
                    f"aucun CTA primaire visible sans défiler à {texte_viewport(viewport)} "
                    f"(destination {primaire.get('dest') or primaire['genre']})"))
        for cta in ctas:
            etat = next((c for c in releve["pli"] if c["chemin"] == cta["chemin"]), None)
            cta.setdefault("au_dessus_du_pli", {})[texte_viewport(viewport)] = bool(etat and etat["pli"])
        constats += auditer_orphelins(releve["orphelins"])
        constats += auditer_troncature(releve)
        non_plafonnes.extend(constats)
        vues.append({"viewport": texte_viewport(viewport), "mobile": est_mobile(viewport),
                     "textes": releve["textes_total"], "constats": plafonner(constats, args.max_par_type)})

    # ---- mouvement réduit ----
    masques_normal = {m["chemin"] for m in releve_large.get("masques") or []}
    constats_mvt = auditer_mouvement(mouvement["charge"], mouvement["apres"], masques_normal,
                                     mouvement["anims"], mouvement["avant"], mouvement["apres_instantane"])
    non_plafonnes.extend(constats_mvt)

    page_plafonnes = plafonner(constats_page, args.max_par_type)
    mvt_plafonnes = plafonner(constats_mvt, args.max_par_type)
    listes = page_plafonnes + [c for v in vues for c in v["constats"]] + mvt_plafonnes

    inventaire = [{
        "libelle": c["libelle"], "nom": c["nom"], "genre": c["genre"], "destination": c.get("dest"),
        "primaire": c.get("primaire", False), "visible": c["visible"], "fixe": c["fixe"],
        "crochet": c.get("crochet") or None, "evenements": c.get("evenements"),
        "au_dessus_du_pli": c.get("au_dessus_du_pli", {}),
    } for c in ctas]
    resume = {
        "fichier": str(cible),
        "viewports": [texte_viewport(v) for v in viewports],
        "mouvement_reduit": texte_viewport(large),
        "planchers": planchers,
        "cibles_tactiles": {"min": CIBLE_MIN_PX, "confort": CIBLE_CONFORT_PX},
        "polices": familles,
        "tracking": suivi,
        "ctas": len(ctas), "ctas_primaires": len(primaires),
        "cta_primaire": {"libelle": primaire["libelle"], "destination": primaire.get("dest") or primaire["genre"],
                         "regle": regle} if primaire else None,
        "max_par_type": args.max_par_type,
        "errors": compter(listes, "erreur"), "warnings": compter(listes, "avertissement"),
        "errors_total": compter(non_plafonnes, "erreur"),
        "warnings_total": compter(non_plafonnes, "avertissement"),
        "by_type": par_type(non_plafonnes),
    }
    sortie = {
        "summary": resume,
        "page": page_plafonnes,
        "viewports": vues,
        "mouvement_reduit": {"viewport": texte_viewport(large), "constats": mvt_plafonnes},
        "ctas": inventaire,
        "gradient_text": gradients,
    }
    if args.format == "json":
        print(json.dumps(sortie, ensure_ascii=False, indent=2))
    else:
        rapport_texte(sortie)
    return 1 if resume["errors"] else 0


def main(argv: list[str] | None = None) -> int:
    args = construire_parseur().parse_args(argv)
    try:
        return executer(args)
    except ErreurUsage as err:
        sys.stderr.write(f"{err}\n")
        return 2
    except Exception as err:  # noqa: BLE001
        # Une panne du contrôle n'est pas un défaut de la page : elle sort en 2,
        # en une ligne, pour qu'un appelant ne la prenne jamais pour une QA rouge.
        sys.stderr.write(f"contrôle interrompu : {type(err).__name__} : {err}\n")
        return 2


if __name__ == "__main__":
    sys.exit(main())

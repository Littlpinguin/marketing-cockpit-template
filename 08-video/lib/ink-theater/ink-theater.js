/*
 * Ink Theater (marketing-cockpit-template, MIT) : moteur déterministe de
 * dessin à l'encre pour les compositions HyperFrames.
 *
 * Toute valeur visuelle est une fonction pure de la géométrie, d'une graine
 * et du temps t : aucune horloge, aucun hasard non semé. L'image N se
 * reproduit à partir de son seul instant, condition du rendu image par image.
 *
 * Navigateur : global `InkTheater`. Node : module CommonJS (fonctions pures,
 * pour les tests). Mode d'emploi : README.md de ce dossier.
 */
(function (racine, fabrique) {
  "use strict";
  var api = fabrique();
  if (typeof module === "object" && module && module.exports) {
    module.exports = api;
  } else {
    racine.InkTheater = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";

  // ------------------------------------------------------------ hasard semé

  /** Générateur pseudo-aléatoire 32 bits à graine (algorithme public mulberry32), sortie dans [0, 1). */
  function aleatoire(graine) {
    var etat = graine >>> 0;
    return function () {
      etat = (etat + 0x6d2b79f5) >>> 0;
      var x = etat;
      x = Math.imul(x ^ (x >>> 15), x | 1);
      x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
      return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
    };
  }

  /** Valeur stable dans [0, 1) pour un couple (graine, n). */
  function hacher(graine, n) {
    var x = (Math.imul(graine | 0, 0x27d4eb2d) ^ Math.imul(n | 0, 0x165667b1)) >>> 0;
    x = Math.imul(x ^ (x >>> 15), 0x85ebca6b) >>> 0;
    x = Math.imul(x ^ (x >>> 13), 0xc2b2ae35) >>> 0;
    return ((x ^ (x >>> 16)) >>> 0) / 4294967296;
  }

  /** Bruit de valeur 1D lissé, dans [-1, 1] : continu en x, stable pour une graine. */
  function bruit(graine, x) {
    var i = Math.floor(x);
    var f = x - i;
    var lisse = f * f * (3 - 2 * f);
    var a = hacher(graine, i) * 2 - 1;
    var b = hacher(graine, i + 1) * 2 - 1;
    return a + (b - a) * lisse;
  }

  // ------------------------------------------------------------ temps

  function borner(v, min, max) {
    return v < min ? min : v > max ? max : v;
  }

  /** Avancement linéaire d'une action entre debut et debut + duree, borné à [0, 1]. */
  function progression(t, debut, duree) {
    if (!(duree > 0)) return t >= debut ? 1 : 0;
    return borner((t - debut) / duree, 0, 1);
  }

  /** Lissage entrée-sortie (cubique) d'un avancement dans [0, 1]. */
  function adoucir(p) {
    return p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
  }

  /** Indice d'état du « boil » : change exactement à chaque multiple de 1 / cadence. */
  function etatBoil(t, cadence) {
    if (!(cadence > 0)) return 0;
    return Math.floor(t * cadence + 1e-9);
  }

  /** Graine qui change avec l'état du boil : le trait « bout » à cadence fixe. */
  function graineDuBoil(graine, t, cadence) {
    return ((graine | 0) + etatBoil(t, cadence) * 7919) | 0;
  }

  // ------------------------------------------------------------ géométrie

  function longueur(points) {
    var total = 0;
    for (var i = 1; i < points.length; i++) {
      total += Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
    }
    return total;
  }

  /** Déplace chaque point le long de la normale locale d'un bruit lissé : le tremblé de la main. */
  function trembler(points, options) {
    options = options || {};
    var amplitude = options.amplitude == null ? 2 : options.amplitude;
    var frequence = options.frequence == null ? 0.08 : options.frequence;
    var graine = options.graine | 0;
    if (amplitude === 0 || points.length < 2) {
      return points.map(function (p) { return [p[0], p[1]]; });
    }
    var parcouru = 0;
    return points.map(function (p, i) {
      var avant = points[Math.max(0, i - 1)];
      var apres = points[Math.min(points.length - 1, i + 1)];
      var dx = apres[0] - avant[0];
      var dy = apres[1] - avant[1];
      var norme = Math.hypot(dx, dy) || 1;
      if (i > 0) parcouru += Math.hypot(p[0] - points[i - 1][0], p[1] - points[i - 1][1]);
      var decalage = amplitude * bruit(graine, parcouru * frequence);
      return [p[0] - (dy / norme) * decalage, p[1] + (dx / norme) * decalage];
    });
  }

  /** Tremblé qui change d'état à cadence fixe (effet dessin animé). */
  function boil(points, t, options) {
    options = options || {};
    var cadence = options.cadence == null ? 10 : options.cadence;
    return trembler(points, {
      amplitude: options.amplitude,
      frequence: options.frequence,
      graine: graineDuBoil(options.graine || 1, t, cadence)
    });
  }

  function arrondir(v) {
    return Math.round(v * 100) / 100;
  }

  function versChemin(points) {
    return points.map(function (p, i) {
      return (i === 0 ? "M" : "L") + arrondir(p[0]) + " " + arrondir(p[1]);
    }).join(" ");
  }

  /** Calendrier d'écriture : une lettre après l'autre, une espace compte pour un tiers de lettre. */
  function lettres(texte, debut, duree) {
    var poids = [];
    var total = 0;
    for (var i = 0; i < texte.length; i++) {
      var w = texte[i] === " " ? 1 / 3 : 1;
      poids.push(w);
      total += w;
    }
    var t = debut;
    var resultat = [];
    for (var j = 0; j < texte.length; j++) {
      var d = total ? (duree * poids[j]) / total : 0;
      resultat.push({ car: texte[j], debut: t, duree: d });
      t += d;
    }
    return resultat;
  }

  // ------------------------------------------------------------ synchronisation

  /**
   * Lie un rendu à une timeline GSAP en pause pilotée par HyperFrames.
   * Un mandataire porte une propriété `t` à accesseur : GSAP l'écrit à chaque
   * rendu de la timeline, y compris lors d'un seek qui supprime les callbacks,
   * et l'accesseur appelle rendre(t). L'événement `hf-seek` est aussi écouté.
   */
  function attach(timeline, rendre, duree) {
    var courant = 0;
    var mandataire = {};
    Object.defineProperty(mandataire, "t", {
      enumerable: true,
      get: function () { return courant; },
      set: function (v) { courant = v; rendre(v); }
    });
    timeline.fromTo(mandataire, { t: 0 }, { t: duree, duration: duree, ease: "none", immediateRender: true }, 0);
    if (typeof window !== "undefined" && window.addEventListener) {
      window.addEventListener("hf-seek", function (e) {
        if (e && e.detail && typeof e.detail.time === "number") rendre(e.detail.time);
      });
    }
    rendre(0);
    return mandataire;
  }

  // ------------------------------------------------------------ DOM (navigateur)

  function creer(tag, attributs, parent) {
    var el = document.createElementNS(SVG_NS, tag);
    for (var cle in attributs) {
      if (Object.prototype.hasOwnProperty.call(attributs, cle)) el.setAttribute(cle, attributs[cle]);
    }
    if (parent) parent.appendChild(el);
    return el;
  }

  /** Échantillonne un chemin SVG (attribut d) en points tous les `pas` px. */
  function echantillonner(d, pas, svg) {
    var tmp = creer("path", { d: d }, svg);
    var total = tmp.getTotalLength();
    var n = Math.max(2, Math.ceil(total / (pas || 4)) + 1);
    var points = [];
    for (var i = 0; i < n; i++) {
      var p = tmp.getPointAtLength((total * i) / (n - 1));
      points.push([p.x, p.y]);
    }
    svg.removeChild(tmp);
    return points;
  }

  /**
   * Trait d'encre tracé progressivement.
   * options : debut, duree (s), epaisseur (px), couleur, tremble (px, 0 = net),
   * cadence (boil, changements par seconde, 0 = figé), graine, pas (px), parent.
   */
  function drawPath(svg, chemin, options) {
    options = options || {};
    var base = typeof chemin === "string" ? echantillonner(chemin, options.pas, svg) : chemin;
    var el = creer("path", {
      fill: "none",
      stroke: options.couleur || "currentColor",
      "stroke-width": options.epaisseur == null ? 4 : options.epaisseur,
      "stroke-linecap": "round",
      "stroke-linejoin": "round"
    }, options.parent || svg);
    var debut = options.debut || 0;
    var duree = options.duree == null ? 1 : options.duree;
    function rendre(t) {
      var pts = boil(base, t, { amplitude: options.tremble == null ? 1.5 : options.tremble,
        cadence: options.cadence, graine: options.graine || 1 });
      var total = longueur(pts);
      var p = adoucir(progression(t, debut, duree));
      el.setAttribute("d", versChemin(pts));
      el.setAttribute("stroke-dasharray", total + " " + total);
      el.setAttribute("stroke-dashoffset", String(total * (1 - p)));
      el.setAttribute("visibility", p > 0 ? "visible" : "hidden");
    }
    return { element: el, rendre: rendre };
  }

  /**
   * Écriture manuscrite lettre à lettre.
   * options : x, y, taille, police, couleur, ancre, debut, duree, graine, cadence, parent.
   */
  function writeText(svg, texte, options) {
    options = options || {};
    var el = creer("text", {
      x: options.x || 0,
      y: options.y || 0,
      "font-family": options.police || "Patrick Hand, cursive",
      "font-size": options.taille || 64,
      fill: options.couleur || "currentColor",
      "text-anchor": options.ancre || "start"
    }, options.parent || svg);
    var plan = lettres(texte, options.debut || 0, options.duree == null ? 1 : options.duree);
    var spans = plan.map(function (l) {
      var s = creer("tspan", {}, el);
      s.textContent = l.car;
      return s;
    });
    var cadence = options.cadence == null ? 8 : options.cadence;
    function rendre(t) {
      var g = graineDuBoil(options.graine || 7, t, cadence);
      for (var i = 0; i < spans.length; i++) {
        spans[i].setAttribute("opacity", t >= plan[i].debut ? "1" : "0");
        spans[i].setAttribute("rotate", String(arrondir((hacher(g, i) * 2 - 1) * 2)));
      }
    }
    return { element: el, rendre: rendre };
  }

  /** Fond papier : aplat teinté et grain fixe (feTurbulence à graine constante). */
  function paper(svg, options) {
    options = options || {};
    var graine = (options.graine || 3) >>> 0;
    var id = "ink-papier-" + graine;
    var defs = svg.querySelector("defs") || creer("defs", {}, null);
    if (!defs.parentNode) svg.insertBefore(defs, svg.firstChild);
    var filtre = creer("filter", { id: id, x: "0", y: "0", width: "100%", height: "100%" }, defs);
    creer("feTurbulence", { type: "fractalNoise", baseFrequency: options.grain || 0.9,
      numOctaves: 2, seed: graine, result: "bruit" }, filtre);
    creer("feColorMatrix", { type: "saturate", values: "0", "in": "bruit", result: "gris" }, filtre);
    var transfert = creer("feComponentTransfer", { "in": "gris", result: "doux" }, filtre);
    creer("feFuncA", { type: "linear", slope: options.intensite == null ? 0.08 : options.intensite }, transfert);
    creer("feBlend", { "in": "SourceGraphic", in2: "doux", mode: "multiply" }, filtre);
    var fond = creer("rect", { x: 0, y: 0, width: "100%", height: "100%",
      fill: options.couleur || "#F5F1E8", filter: "url(#" + id + ")" }, null);
    svg.insertBefore(fond, defs.nextSibling);
    return { element: fond, rendre: function () {} };
  }

  /** Regroupe des objets { rendre(t) } et les rend ensemble. */
  function scene(objets) {
    objets = objets || [];
    return {
      ajouter: function (o) { objets.push(o); return o; },
      rendre: function (t) { for (var i = 0; i < objets.length; i++) objets[i].rendre(t); }
    };
  }

  return {
    version: "1.0.0",
    aleatoire: aleatoire,
    hacher: hacher,
    bruit: bruit,
    progression: progression,
    adoucir: adoucir,
    etatBoil: etatBoil,
    graineDuBoil: graineDuBoil,
    longueur: longueur,
    trembler: trembler,
    boil: boil,
    versChemin: versChemin,
    lettres: lettres,
    attach: attach,
    drawPath: drawPath,
    writeText: writeText,
    paper: paper,
    scene: scene
  };
});

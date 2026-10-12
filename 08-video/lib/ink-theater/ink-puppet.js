/*
 * Ink Puppet (marketing-cockpit-template, MIT) : silhouette en traits d'encre
 * animée par des clips de mouvement 2D (format de 08-video/scripts/bvh2clip.py).
 *
 * Pose à l'instant t = interpolation linéaire entre deux images du clip ; une
 * séquence enchaîne des clips avec un fondu de pose de 0,2 s. Rendu
 * déterministe : même clip, même graine, même t, même image.
 *
 * Navigateur : global `InkPuppet` (charger ink-theater.js avant). Node : module
 * CommonJS (fonctions pures, pour les tests).
 */
(function (racine, fabrique) {
  "use strict";
  var api = fabrique(racine);
  if (typeof module === "object" && module && module.exports) {
    module.exports = api;
  } else {
    racine.InkPuppet = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function (racine) {
  "use strict";

  var SVG_NS = "http://www.w3.org/2000/svg";
  var ARTICULATIONS = ["tete", "cou", "epaule_g", "coude_g", "main_g", "epaule_d", "coude_d", "main_d",
    "hanche", "genou_g", "pied_g", "genou_d", "pied_d"];
  var INDICE = {};
  ARTICULATIONS.forEach(function (nom, i) { INDICE[nom] = i; });
  var SEGMENTS = [["cou", "hanche"], ["cou", "epaule_g"], ["epaule_g", "coude_g"], ["coude_g", "main_g"],
    ["cou", "epaule_d"], ["epaule_d", "coude_d"], ["coude_d", "main_d"], ["hanche", "genou_g"],
    ["genou_g", "pied_g"], ["hanche", "genou_d"], ["genou_d", "pied_d"]];
  var FONDU = 0.2;

  function valider(clip) {
    if (!clip || typeof clip !== "object") throw new Error("clip absent");
    var nom = clip.nom ? "clip « " + clip.nom + " »" : "clip sans nom";
    if (!(Number.isFinite(clip.fps) && clip.fps > 0)) throw new Error(nom + " : fps invalide");
    if (!Array.isArray(clip.articulations) || clip.articulations.join() !== ARTICULATIONS.join()) {
      throw new Error(nom + " : articulations attendues " + ARTICULATIONS.join(", "));
    }
    if (!Array.isArray(clip.images) || !clip.images.length) throw new Error(nom + " : aucune image");
    clip.images.forEach(function (image, n) {
      if (!Array.isArray(image) || image.length !== ARTICULATIONS.length) {
        throw new Error(nom + ", image " + n + " : 13 points attendus");
      }
      image.forEach(function (p) {
        if (!Array.isArray(p) || p.length !== 2 || !Number.isFinite(p[0]) || !Number.isFinite(p[1])) {
          throw new Error(nom + ", image " + n + " : point invalide");
        }
      });
    });
    return true;
  }

  function melanger(a, b, x) {
    return a.map(function (p, i) {
      return [p[0] + (b[i][0] - p[0]) * x, p[1] + (b[i][1] - p[1]) * x];
    });
  }

  /**
   * Pose à l'instant t ; en boucle (défaut), la dernière image rejoint la première.
   * Un instant négatif vaut 0 ; un instant non fini (NaN, infini) est traité comme 0.
   */
  function pose(clip, t, options) {
    var boucle = !options || options.boucle !== false;
    var n = clip.images.length;
    if (n === 1) return clip.images[0].map(function (p) { return [p[0], p[1]]; });
    var f = (Number.isFinite(t) ? Math.max(0, t) : 0) * clip.fps;
    var i, j;
    if (boucle) {
      f = f % n;
      i = Math.floor(f);
      j = (i + 1) % n;
    } else {
      f = Math.min(f, n - 1);
      i = Math.floor(f);
      j = Math.min(i + 1, n - 1);
    }
    return melanger(clip.images[i], clip.images[j], f - i);
  }

  function debutEntree(e) {
    return e.debut == null ? 0 : e.debut;
  }

  /**
   * Temps (en s) pendant lequel une entrée avance avant de se figer sur sa dernière pose :
   * `duree` si elle est donnée ; sinon sans limite pour une entrée en boucle (elle boucle
   * jusqu'à l'entrée suivante) et (images - 1) / fps pour une entrée `boucle: false`.
   */
  function dureeEntree(e) {
    if (e.duree != null) return e.duree;
    if (e.boucle !== false) return Infinity;
    return (e.clip.images.length - 1) / e.clip.fps;
  }

  function poseEntree(e, local) {
    return pose(e.clip, local, { boucle: e.boucle !== false });
  }

  /**
   * Pose d'une séquence [{clip, debut, duree, boucle}] à l'instant t, fondu de FONDU s entre
   * deux entrées. Avant la première entrée, la première image de la première entrée est tenue.
   * Une entrée en boucle sans `duree` boucle jusqu'à l'entrée suivante (la dernière, sans fin) ;
   * avec `duree` elle se fige ensuite sur sa dernière pose ; avec `boucle: false` et sans
   * `duree` elle se fige sur sa dernière image. Le fondu part de la pose que l'entrée
   * précédente a, selon la même règle, à l'instant où la nouvelle démarre.
   */
  function sequenceAt(entrees, t) {
    if (!entrees.length) throw new Error("séquence vide");
    var tri = entrees.slice().sort(function (a, b) { return debutEntree(a) - debutEntree(b); });
    var k = 0;
    for (var i = 0; i < tri.length; i++) if (t >= debutEntree(tri[i])) k = i;
    var e = tri[k];
    var depuis = t - debutEntree(e);
    var local = Math.max(0, Math.min(depuis, dureeEntree(e)));
    var courante = poseEntree(e, local);
    if (k > 0 && depuis < FONDU) {
      var precedente = tri[k - 1];
      var finPrecedente = Math.min(debutEntree(e) - debutEntree(precedente), dureeEntree(precedente));
      return melanger(poseEntree(precedente, finPrecedente), courante, Math.max(0, depuis) / FONDU);
    }
    return courante;
  }

  function sequence(entrees) {
    entrees.forEach(function (e) { valider(e.clip); });
    return { at: function (t) { return sequenceAt(entrees, t); } };
  }

  /** Coordonnées normalisées (y vers le haut) → SVG (y vers le bas), hanche en (x, y). */
  function versSVG(p, placement) {
    var x = placement.x || 0;
    var y = placement.y || 0;
    var e = placement.echelle || 400;
    return p.map(function (pt) { return [x + pt[0] * e, y - pt[1] * e]; });
  }

  function subdiviser(a, b, n) {
    var r = [];
    for (var i = 0; i <= n; i++) r.push([a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n]);
    return r;
  }

  function cercle(centre, rayon, n) {
    var pts = [];
    for (var i = 0; i <= n; i++) {
      var a = (2 * Math.PI * i) / n;
      pts.push([centre[0] + rayon * Math.cos(a), centre[1] + rayon * Math.sin(a)]);
    }
    return pts;
  }

  function trait(groupe, options) {
    var p = document.createElementNS(SVG_NS, "path");
    p.setAttribute("fill", "none");
    p.setAttribute("stroke", options.couleur || "currentColor");
    p.setAttribute("stroke-width", options.epaisseur == null ? 6 : options.epaisseur);
    p.setAttribute("stroke-linecap", "round");
    p.setAttribute("stroke-linejoin", "round");
    groupe.appendChild(p);
    return p;
  }

  /**
   * Silhouette dans un SVG. options : clip (+ boucle) ou sequence, x, y (hanche),
   * echelle (px pour une hauteur debout), couleur, epaisseur, graine, cadence,
   * tremble, parent, theatre (InkTheater ; défaut : le global).
   */
  function create(svg, options) {
    if (!options || !(options.clip || options.sequence)) throw new Error("options requises : clip ou sequence");
    var theatre = options.theatre || racine.InkTheater;
    if (!theatre) throw new Error("InkTheater introuvable : charger ink-theater.js avant ink-puppet.js");
    var source;
    if (options.sequence) {
      source = sequence(options.sequence);
    } else {
      valider(options.clip);
      source = { at: function (t) { return pose(options.clip, t, { boucle: options.boucle !== false }); } };
    }
    var groupe = document.createElementNS(SVG_NS, "g");
    (options.parent || svg).appendChild(groupe);
    var traits = SEGMENTS.map(function () { return trait(groupe, options); });
    var tete = trait(groupe, options);
    var cadence = options.cadence == null ? 10 : options.cadence;
    var tremble = options.tremble == null ? 1.2 : options.tremble;
    function rendre(t) {
      var pts = versSVG(source.at(t), options);
      var g = theatre.graineDuBoil(options.graine == null ? 11 : options.graine, t, cadence);
      SEGMENTS.forEach(function (s, k) {
        var ligne = subdiviser(pts[INDICE[s[0]]], pts[INDICE[s[1]]], 6);
        traits[k].setAttribute("d", theatre.versChemin(theatre.trembler(ligne, { amplitude: tremble, graine: g + k })));
      });
      var cou = pts[INDICE.cou];
      var sommet = pts[INDICE.tete];
      var centre = [(cou[0] + sommet[0]) / 2, (cou[1] + sommet[1]) / 2];
      var rayon = Math.hypot(sommet[0] - cou[0], sommet[1] - cou[1]) / 2;
      var contour = theatre.trembler(cercle(centre, rayon, 18), { amplitude: tremble, graine: g + 99 });
      contour[contour.length - 1] = [contour[0][0], contour[0][1]];
      tete.setAttribute("d", theatre.versChemin(contour));
    }
    return { element: groupe, rendre: rendre };
  }

  return {
    ARTICULATIONS: ARTICULATIONS,
    SEGMENTS: SEGMENTS,
    FONDU: FONDU,
    valider: valider,
    pose: pose,
    melanger: melanger,
    sequenceAt: sequenceAt,
    sequence: sequence,
    versSVG: versSVG,
    subdiviser: subdiviser,
    create: create
  };
});

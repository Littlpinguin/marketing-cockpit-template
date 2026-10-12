"""Tests du moteur ink-theater (08-video/lib/ink-theater/) via Node.

Les fonctions pures sont appelées sous Node (les fichiers s'exportent en
CommonJS) ; la couche DOM se vérifie au rendu HyperFrames (tâche 14). Un test
statique interdit toute source de non-déterminisme.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOSSIER = REPO / "08-video" / "lib" / "ink-theater"
THEATRE = (DOSSIER / "ink-theater.js").as_posix()
PUPPET = (DOSSIER / "ink-puppet.js").as_posix()
requiert_node = pytest.mark.skipif(shutil.which("node") is None, reason="node absent")


def node(code: str):
    res = subprocess.run(["node", "-e", code], capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout)


def test_sources_sans_hasard_ni_horloge():
    for chemin in (DOSSIER / "ink-theater.js", DOSSIER / "ink-puppet.js"):
        texte = chemin.read_text(encoding="utf-8")
        for interdit in ("Math.random", "Date.now", "performance.now", "requestAnimationFrame",
                         "setTimeout", "setInterval", "new Date"):
            assert interdit not in texte, f"{chemin.name} contient {interdit}"


@requiert_node
def test_aleatoire_deterministe():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      const tirer = g => {{ const f = I.aleatoire(g); return [f(), f(), f()]; }};
      console.log(JSON.stringify({{a: tirer(42), b: tirer(42), c: tirer(43)}}));""")
    assert r["a"] == r["b"] and r["a"] != r["c"]
    assert all(0 <= v < 1 for v in r["a"] + r["c"])


@requiert_node
def test_bruit_continu_borne_et_stable():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      const xs = Array.from({{length: 200}}, (_, i) => i * 0.137);
      console.log(JSON.stringify({{
        v: xs.map(x => I.bruit(7, x)), w: xs.map(x => I.bruit(7, x)),
        a: I.bruit(7, 3.5), b: I.bruit(7, 3.5 + 1e-6)}}));""")
    assert r["v"] == r["w"]
    assert all(-1 <= v <= 1 for v in r["v"])
    assert abs(r["a"] - r["b"]) < 1e-4


@requiert_node
def test_trembler_stable_par_graine():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      const pts = Array.from({{length: 30}}, (_, i) => [i * 10, 50]);
      console.log(JSON.stringify({{
        a: I.trembler(pts, {{amplitude: 3, graine: 1}}), b: I.trembler(pts, {{amplitude: 3, graine: 1}}),
        c: I.trembler(pts, {{amplitude: 3, graine: 2}}), zero: I.trembler(pts, {{amplitude: 0, graine: 1}}),
        pts}}));""")
    assert r["a"] == r["b"] and r["a"] != r["c"]
    assert r["zero"] == r["pts"]
    assert max(abs(p[1] - 50) for p in r["a"]) <= 3 + 1e-9


@requiert_node
def test_trembler_deplace_selon_la_normale_et_non_la_tangente():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      const horizontale = Array.from({{length: 30}}, (_, i) => [i * 10, 50]);
      const verticale = Array.from({{length: 30}}, (_, i) => [50, i * 10]);
      console.log(JSON.stringify({{
        h: I.trembler(horizontale, {{amplitude: 3, graine: 1}}),
        v: I.trembler(verticale, {{amplitude: 3, graine: 1}})}}));""")
    # ligne horizontale : seule l'ordonnée bouge ; ligne verticale : seule l'abscisse bouge
    deplacements_h = [abs(p[1] - 50) for p in r["h"]]
    assert all(p[0] == i * 10 for i, p in enumerate(r["h"]))
    assert 0 < max(deplacements_h) <= 3 + 1e-9
    deplacements_v = [abs(p[0] - 50) for p in r["v"]]
    assert all(p[1] == i * 10 for i, p in enumerate(r["v"]))
    assert 0 < max(deplacements_v) <= 3 + 1e-9


@requiert_node
def test_etat_boil_change_exactement_a_la_cadence():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      console.log(JSON.stringify([0, 0.0999, 0.1, 0.3, 0.7, 1.0].map(t => I.etatBoil(t, 10))
        .concat([I.etatBoil(5, 0)])));""")
    assert r == [0, 0, 1, 3, 7, 10, 0]


@requiert_node
def test_progression_lettres_et_chemin():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      console.log(JSON.stringify({{
        p: [I.progression(-1, 0, 2), I.progression(1, 0, 2), I.progression(5, 0, 2), I.progression(1, 1, 0)],
        l: I.lettres("ab c", 1, 2), d: I.versChemin([[0, 0], [10.123, 5]])}}));""")
    assert r["p"] == [0, 0.5, 1, 1]
    lettres = r["l"]
    assert [x["car"] for x in lettres] == ["a", "b", " ", "c"]
    assert lettres[0]["debut"] == 1
    assert abs(sum(x["duree"] for x in lettres) - 2) < 1e-9
    assert lettres[2]["duree"] < lettres[0]["duree"]
    assert r["d"] == "M0 0 L10.12 5"


@requiert_node
def test_attach_rend_via_l_accesseur():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      const appels = [];
      const tl = {{ fromTo(cible, de, vers, position) {{
        this.vars = vers; this.position = position; cible.t = de.t; cible.t = 1.5; }} }};
      const m = I.attach(tl, t => appels.push(t), 6);
      console.log(JSON.stringify({{appels, vars: tl.vars, position: tl.position, t: m.t}}));""")
    assert 1.5 in r["appels"] and 0 in r["appels"]
    assert r["vars"]["duration"] == 6 and r["vars"]["t"] == 6 and r["vars"]["ease"] == "none"
    assert r["position"] == 0 and r["t"] == 1.5


CLIP = """{nom: "test", fps: 10, articulations: P.ARTICULATIONS.slice(),
  images: [P.ARTICULATIONS.map(() => [0, 0]), P.ARTICULATIONS.map(() => [1, 2])]}"""


@requiert_node
def test_valider_refuse_un_clip_malforme():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const essais = [null, {{nom: "a", fps: 0, articulations: P.ARTICULATIONS, images: [[]]}},
        {{nom: "b", fps: 10, articulations: ["x"], images: []}},
        {{nom: "c", fps: 10, articulations: P.ARTICULATIONS, images: [[[0, 0]]]}}];
      const erreurs = essais.map(c => {{ try {{ P.valider(c); return null; }} catch (e) {{ return e.message; }} }});
      console.log(JSON.stringify({{erreurs, ok: P.valider({CLIP})}}));""")
    assert all(r["erreurs"]) and r["ok"] is True


@requiert_node
def test_pose_interpole_et_boucle():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const clip = {CLIP};
      console.log(JSON.stringify({{
        milieu: P.pose(clip, 0.05)[0], boucle: P.pose(clip, 0.15)[0],
        fige: P.pose(clip, 0.15, {{boucle: false}})[0], negatif: P.pose(clip, -3)[0]}}));""")
    assert r["milieu"] == [0.5, 1] and r["boucle"] == [0.5, 1]
    assert r["fige"] == [1, 2] and r["negatif"] == [0, 0]


@requiert_node
def test_clip_d_une_seule_image():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const clip = {{nom: "un", fps: 30, articulations: P.ARTICULATIONS.slice(),
        images: [P.ARTICULATIONS.map(() => [0.25, 0.5])]}};
      console.log(JSON.stringify([P.pose(clip, 0)[0], P.pose(clip, 12.3)[0]]));""")
    assert r == [[0.25, 0.5], [0.25, 0.5]]


@requiert_node
def test_sequence_fondu_entre_deux_clips():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const fixe = v => ({{nom: "f" + v, fps: 30, articulations: P.ARTICULATIONS.slice(),
        images: [P.ARTICULATIONS.map(() => [v, v])]}});
      const s = P.sequence([{{clip: fixe(1), debut: 1, duree: 1}}, {{clip: fixe(0), debut: 0, duree: 1}}]);
      console.log(JSON.stringify([0.5, 1.1, 1.3, 5].map(t => s.at(t)[0])));""")
    assert r[0] == [0, 0]
    assert r[1][0] == pytest.approx(0.5)
    assert r[2] == [1, 1] and r[3] == [1, 1]


# ---------------------------------------------------------------- ronde de correction 1

# Document factice minimal : suffit à exécuter sous Node la construction des
# éléments SVG de drawPath, writeText et InkPuppet.create (pas paper(), qui
# interroge le DOM : vérifié dans un vrai Chromium, voir le rapport).
FAUX_DOM = """globalThis.document = { createElementNS(ns, tag) {
  return { tag, attrs: {}, enfants: [], textContent: "",
    setAttribute(k, v) { this.attrs[k] = String(v); },
    appendChild(c) { this.enfants.push(c); return c; } }; } };
const faux_svg = () => document.createElementNS("", "svg");"""

# Clip de 4 images à 10 i/s : l'image k vaut [k, k] pour toutes les articulations.
CLIP4 = """{nom: "q", fps: 10, articulations: P.ARTICULATIONS.slice(),
  images: [0, 1, 2, 3].map(k => P.ARTICULATIONS.map(() => [k, k]))}"""
# Même clip de 4 images, mais avec une silhouette non dégénérée (articulations distinctes).
CLIP_TETE = """{nom: "q", fps: 10, articulations: P.ARTICULATIONS.slice(),
  images: [0, 1, 2, 3].map(k => P.ARTICULATIONS.map((_, i) => [k * 0.1 + i * 0.05, k * 0.1 + i * 0.07]))}"""
FIXE = """const fixe = v => ({nom: "f" + v, fps: 30, articulations: P.ARTICULATIONS.slice(),
  images: [P.ARTICULATIONS.map(() => [v, v])]});"""


@requiert_node
def test_attach_borne_le_temps_de_hf_seek_comme_l_accesseur():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      const ecouteurs = {{}};
      globalThis.window = {{ addEventListener(type, fn) {{ ecouteurs[type] = fn; }} }};
      const appels = [];
      const tl = {{ fromTo(cible, de) {{ cible.t = de.t; }} }};
      I.attach(tl, t => appels.push(t), 6);
      const avant = appels.length;
      for (const e of [{{detail: {{time: 99}}}}, {{detail: {{time: -4}}}}, {{detail: {{time: 2.5}}}},
                       {{detail: {{time: "x"}}}}, {{detail: {{time: NaN}}}}, {{}}]) ecouteurs["hf-seek"](e);
      console.log(JSON.stringify(appels.slice(avant)));""")
    assert r == [6, 0, 2.5]


@requiert_node
def test_graine_zero_est_utilisable_partout():
    r = node(f"""const I = require({json.dumps(THEATRE)});
      {FAUX_DOM}
      const pts = Array.from({{length: 20}}, (_, i) => [i * 10, 50]);
      const boil = g => I.boil(pts, 0, g === undefined ? {{amplitude: 3}} : {{amplitude: 3, graine: g}});
      const trace = g => {{
        const o = {{tremble: 5, duree: 1}}; if (g !== undefined) o.graine = g;
        const p = I.drawPath(faux_svg(), pts, o); p.rendre(0.5); return p.element.attrs.d; }};
      const ecrit = g => {{
        const o = {{duree: 1}}; if (g !== undefined) o.graine = g;
        const w = I.writeText(faux_svg(), "abcdefgh", o); w.rendre(2);
        return w.element.enfants.map(s => s.attrs.rotate).join(","); }};
      console.log(JSON.stringify({{
        boil: [boil(0), boil(), boil(1)], trace: [trace(0), trace(), trace(1)], ecrit: [ecrit(0), ecrit(), ecrit(7)]}}));""")
    assert not [nom for nom, (zero, defaut, _) in r.items() if zero == defaut], \
        "graine 0 traitée comme absente"
    assert all(defaut == explicite for defaut, explicite in ((v[1], v[2]) for v in r.values())), \
        "la graine par défaut a changé"


@requiert_node
def test_lettres_par_point_de_code():
    texte = "a\U0001F600b"
    r = node(f"""const I = require({json.dumps(THEATRE)});
      const l = I.lettres({json.dumps(texte)}, 0, 3);
      console.log(JSON.stringify({{n: l.length, points: l.map(x => x.car.codePointAt(0)),
        somme: l.reduce((s, x) => s + x.duree, 0), debuts: l.map(x => x.debut)}}));""")
    assert r["n"] == 3
    assert r["points"] == [ord("a"), 0x1F600, ord("b")]
    assert r["somme"] == pytest.approx(3)
    assert r["debuts"] == pytest.approx([0, 1, 2])


@requiert_node
def test_valider_rejette_les_non_finis_et_nomme_un_clip_sans_nom():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const avec = (fps, point) => {{
        const image = P.ARTICULATIONS.map(() => [0, 0]);
        if (point !== undefined) image[3] = point;
        return {{nom: "x", fps, articulations: P.ARTICULATIONS.slice(), images: [image]}}; }};
      const essayer = c => {{ try {{ return P.valider(c); }} catch (e) {{ return e.message; }} }};
      console.log(JSON.stringify({{
        bon: essayer(avec(10)),
        rejetes: [avec("10"), avec(Infinity), avec(10, [null, 0]), avec(10, ["1", 0]),
                  avec(10, [0, Infinity]), avec(10, [NaN, 0])].map(essayer),
        sans_nom: essayer({{fps: 10, articulations: P.ARTICULATIONS.slice(), images: []}})}}));""")
    assert r["bon"] is True
    assert all(isinstance(m, str) for m in r["rejetes"]), r["rejetes"]
    assert r["sans_nom"].startswith("clip sans nom")


@requiert_node
def test_pose_traite_un_instant_non_fini_comme_zero():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const clip = {CLIP4};
      const essayer = (t, o) => {{ try {{ return P.pose(clip, t, o)[0]; }} catch (e) {{ return e.message; }} }};
      console.log(JSON.stringify([NaN, Infinity, -Infinity, undefined, "x"].flatMap(t =>
        [essayer(t), essayer(t, {{boucle: false}})])));""")
    assert r == [[0, 0]] * 10


@requiert_node
def test_sequence_entree_en_boucle_sans_duree_continue_de_boucler():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const clip = {CLIP4};
      {FIXE}
      const boucle = P.sequence([{{clip, debut: 0}}]);
      const explicite = P.sequence([{{clip, debut: 0, duree: 0.2}}]);
      const fige = P.sequence([{{clip, debut: 0, boucle: false}}]);
      const avant = P.sequence([{{clip, debut: 1}}]);
      const sans_debut = P.sequence([{{clip}}]);
      const fondu = P.sequence([{{clip, debut: 0}}, {{clip: fixe(10), debut: 0.45}}]);
      console.log(JSON.stringify({{
        boucle: [0.3, 0.4, 0.5, 2.1].map(t => boucle.at(t)[0]),
        explicite: [0.1, 0.2, 0.9].map(t => explicite.at(t)[0]),
        fige: [0.1, 0.3, 5].map(t => fige.at(t)[0]),
        avant: avant.at(0.2)[0],
        sans_debut: [0.3, 0.4].map(t => sans_debut.at(t)[0]),
        fondu: fondu.at(0.55)[0]}}));""")
    assert r["boucle"] == [[3, 3], [0, 0], [1, 1], [1, 1]]
    assert r["explicite"] == [[1, 1], [2, 2], [2, 2]]
    assert r["fige"] == [[1, 1], [3, 3], [3, 3]]
    assert r["avant"] == [0, 0]
    assert r["sans_debut"] == [[3, 3], [0, 0]]  # debut absent = 0
    # le fondu part de la pose de l'entrée précédente à l'instant où la suivante démarre :
    # t = 0,45 → image 4,5 de la boucle = 0,5 ; mélange à moitié avec 10 → 5,25
    assert r["fondu"][0] == pytest.approx(5.25)


@requiert_node
def test_create_refuse_l_absence_d_options():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      {FAUX_DOM}
      const essayer = f => {{ try {{ f(); return null; }} catch (e) {{ return e.message; }} }};
      console.log(JSON.stringify([essayer(() => P.create(faux_svg())), essayer(() => P.create(faux_svg(), {{}}))]));""")
    assert r == ["options requises : clip ou sequence"] * 2


@requiert_node
def test_create_une_sequence_d_un_clip_boucle_comme_le_clip_seul():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const T = require({json.dumps(THEATRE)});
      {FAUX_DOM}
      const clip = {CLIP_TETE};
      const dessin = autres => {{
        const p = P.create(faux_svg(), Object.assign({{x: 100, y: 200, echelle: 50, theatre: T, graine: 5}}, autres));
        return t => {{ p.rendre(t); return p.element.enfants.map(e => e.attrs.d).join("|"); }}; }};
      const seul = dessin({{clip}});
      const sequence = dessin({{sequence: [{{clip, debut: 0}}]}});
      const sans_debut = dessin({{sequence: [{{clip}}]}});
      console.log(JSON.stringify({{
        egal: [0.05, 0.4, 0.55, 3.3].map(t => seul(t) === sequence(t)),
        egal_sans_debut: [0.05, 0.4, 0.55, 3.3].map(t => seul(t) === sans_debut(t)),
        boucle: seul(0.25) !== seul(0.45)}}));""")
    assert r["boucle"] is True
    assert r["egal"] == [True] * 4
    assert r["egal_sans_debut"] == [True] * 4


@requiert_node
def test_create_graine_zero_est_utilisable():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const T = require({json.dumps(THEATRE)});
      {FAUX_DOM}
      const clip = {CLIP_TETE};
      const dessin = graine => {{
        const o = {{clip, x: 100, y: 200, echelle: 100, theatre: T}};
        if (graine !== undefined) o.graine = graine;
        const p = P.create(faux_svg(), o); p.rendre(0);
        return p.element.enfants.map(e => e.attrs.d).join("|"); }};
      console.log(JSON.stringify({{zero: dessin(0), defaut: dessin(), onze: dessin(11)}}));""")
    assert r["zero"] != r["defaut"], "graine 0 traitée comme absente"
    assert r["defaut"] == r["onze"], "la graine par défaut a changé"


@requiert_node
def test_create_referme_le_contour_de_la_tete():
    r = node(f"""const P = require({json.dumps(PUPPET)});
      const T = require({json.dumps(THEATRE)});
      {FAUX_DOM}
      const clip = {CLIP_TETE};
      const ecarts = [0, 0.05, 0.2, 0.37].map(t => {{
        const p = P.create(faux_svg(), {{clip, x: 100, y: 200, echelle: 100, theatre: T, tremble: 3}});
        p.rendre(t);
        const morceaux = p.element.enfants.pop().attrs.d.split(" L");
        return [morceaux[0].slice(1), morceaux[morceaux.length - 1]]; }});
      console.log(JSON.stringify(ecarts));""")
    for debut, fin in r:
        assert debut == fin, "le contour de la tête ne se referme pas"

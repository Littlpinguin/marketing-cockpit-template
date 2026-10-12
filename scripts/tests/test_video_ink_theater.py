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

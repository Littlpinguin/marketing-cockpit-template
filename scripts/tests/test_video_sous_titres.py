"""Tests de 08-video/scripts/controle-sous-titres.py et du hook .claude/hooks/controle-sous-titres.py.

Le contrôle applique 08-video/scripts/sous-titres.toml aux .srt et aux compositions d'un projet ;
le hook le lance après chaque écriture et bloque (code 2) sur erreur. Les projets d'exemple sont
écrits dans un dossier temporaire, sous un dossier `projets/` comme dans le module.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "08-video" / "scripts" / "controle-sous-titres.py"
REGLES = REPO / "08-video" / "scripts" / "sous-titres.toml"
HOOK = REPO / ".claude" / "hooks" / "controle-sous-titres.py"

SCRIPT_MD = """# Script

| Temps | Image | Voix |
|---|---|---|
| 0–3 s | Titre | Bonjour à tous, voici la méthode. |
| 3–5 s | Liste | Trois étapes suffisent. |
"""

SRT_CONFORME = """1
00:00:00,000 --> 00:00:01,500
Bonjour à tous,

2
00:00:01,500 --> 00:00:03,000
voici la méthode.

3
00:00:03,000 --> 00:00:04,500
Trois étapes suffisent.
"""


def _projet(tmp_path: Path, *, srt: str = SRT_CONFORME, toile: str = "1080 × 1920",
            corps_px: int = 72, coupe: dict | None = None) -> Path:
    projet = tmp_path / "projets" / "2026-10-26-exemple"
    (projet / "sous-titres").mkdir(parents=True)
    (projet / "hyperframes").mkdir()
    (projet / "script.md").write_text(SCRIPT_MD, encoding="utf-8")
    (projet / "sous-titres" / "exemple-reels.srt").write_text(srt, encoding="utf-8")
    (projet / "hyperframes" / "frame.md").write_text(f"# Frame\n\nToile : {toile}\n", encoding="utf-8")
    (projet / "hyperframes" / "index.html").write_text(
        f"<html><style>.st {{ font-size: {corps_px}px; }} .titre {{ font-size: 20px; }}</style></html>",
        encoding="utf-8")
    if coupe is not None:
        (projet / "montage").mkdir()
        (projet / "montage" / "coupe.json").write_text(json.dumps(coupe), encoding="utf-8")
    return projet


def _controler(cible: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), str(cible)], capture_output=True, text=True)


def _hook(payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload),
                          capture_output=True, text=True)


def test_projet_conforme_passe(tmp_path):
    r = _controler(_projet(tmp_path))
    assert r.returncode == 0, r.stdout
    assert "0 erreur(s)" in r.stdout and "toile 1080x1920" in r.stdout


@pytest.mark.parametrize("srt, motif", [
    (SRT_CONFORME.replace("Trois étapes suffisent.", "Trois étapes suffisent largement."), "caractères, 25 au plus"),
    (SRT_CONFORME.replace("Bonjour à tous,", "Bonjour\nà tous,"), "2 lignes, 1 au plus"),
    (SRT_CONFORME.replace("00:00:01,500 --> 00:00:03,000", "00:00:01,200 --> 00:00:03,000"), "chevauche"),
    (SRT_CONFORME.replace("00:00:03,000 --> 00:00:04,500", "00:00:03,000 --> 00:00:03,100"), "affiché 0.10 s"),
    (SRT_CONFORME.replace("Trois étapes suffisent.", "Quatre détours suffisent."), "colonne Voix"),
])
def test_srt_hors_regles_bloque(tmp_path, srt, motif):
    r = _controler(_projet(tmp_path, srt=srt))
    assert r.returncode == 1, r.stdout
    assert motif in r.stdout


def test_corps_trop_petit_dans_la_composition(tmp_path):
    r = _controler(_projet(tmp_path, corps_px=40))
    assert r.returncode == 1
    assert "« .st » en 40 px, 60 px au moins" in r.stdout
    assert ".titre" not in r.stdout  # seules les règles de sous-titres comptent


def test_segment_a_cheval_sur_une_coupe(tmp_path):
    coupe = {"ips": 30, "morceaux": [
        {"montage_debut": 0.0, "image_debut": 0, "image_fin": 60},     # 0 → 2 s
        {"montage_debut": 2.0, "image_debut": 300, "image_fin": 390},  # 2 → 5 s
    ]}
    r = _controler(_projet(tmp_path, coupe=coupe))
    assert r.returncode == 1
    assert "à cheval sur la coupe de 2.00 s" in r.stdout


def test_toile_16_9_admet_deux_lignes(tmp_path):
    srt = SRT_CONFORME.replace("Bonjour à tous,", "Bonjour à tous,\nvoici").replace("voici la méthode.", "la méthode.")
    r = _controler(_projet(tmp_path, srt=srt, toile="1920 × 1080", corps_px=48))
    assert r.returncode == 0, r.stdout
    assert "toile 1920x1080" in r.stdout


def test_hook_bloque_une_ecriture_hors_regles(tmp_path):
    projet = _projet(tmp_path, srt=SRT_CONFORME.replace("Bonjour à tous,", "Bonjour à tous et bienvenue,"))
    srt = projet / "sous-titres" / "exemple-reels.srt"
    r = _hook({"tool_name": "Write", "tool_input": {"file_path": str(srt)}})
    assert r.returncode == 2
    assert "Sous-titres hors règles dans 2026-10-26-exemple" in r.stderr
    assert "08-video/formats.md" in r.stderr


def test_hook_laisse_passer(tmp_path):
    projet = _projet(tmp_path)
    for chemin in (projet / "sous-titres" / "exemple-reels.srt", projet / "hyperframes" / "index.html",
                   projet / "brief.md"):
        assert _hook({"tool_name": "Edit", "tool_input": {"file_path": str(chemin)}}).returncode == 0
    assert subprocess.run([sys.executable, str(HOOK)], input="pas du json",
                          capture_output=True, text=True).returncode == 0


def test_hook_cable_dans_les_reglages():
    reglages = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
    entrees = [e for e in reglages["hooks"]["PostToolUse"]
               if any("controle-sous-titres.py" in h["command"] for h in e["hooks"])]
    assert len(entrees) == 1
    assert set(entrees[0]["matcher"].split("|")) >= {"Write", "Edit", "Bash"}


def test_regles_et_doctrine_concordent():
    """Changer une règle, c'est changer le .toml et 08-video/formats.md dans le même commit."""
    toiles = tomllib.loads(REGLES.read_text(encoding="utf-8"))["toile"]
    doctrine = (REPO / "08-video" / "formats.md").read_text(encoding="utf-8")
    section = re.search(r"^## Sous-titres.*?(?=^## )", doctrine, re.S | re.M).group(0)
    v, p45, carre, h = (toiles[k] for k in ("1080x1920", "1080x1350", "1080x1080", "1920x1080"))
    assert v["lignes_max"] == 1 and f"une ligne de {v['car_max']} caractères au plus" in section
    assert p45["car_max"] == carre["car_max"] and p45["lignes_max"] == carre["lignes_max"] == h["lignes_max"] == 2
    assert f"2 lignes de {p45['car_max']} caractères au plus en 4:5 et 1:1, de {h['car_max']} en 16:9" in section
    assert f"{v['taille_min_px']} px au moins" in section
    assert carre["taille_min_px"] == h["taille_min_px"]
    assert f"{p45['taille_min_px']} px en 4:5, {carre['taille_min_px']} px en 1:1 et 16:9" in section
    commun = tomllib.loads(REGLES.read_text(encoding="utf-8"))["commun"]
    assert f"{commun['cps_alerte']:.0f} caractères par seconde au plus" in section
    assert f"{commun['cps_max']:.0f} au plus" in section
    assert "08-video/scripts/sous-titres.toml" in section

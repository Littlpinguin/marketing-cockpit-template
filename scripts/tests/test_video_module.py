"""Tests de structure et de câblage du module vidéo (skills, doctrine, module, documentation).

Ces tests vérifient des fichiers, pas un comportement : présence, frontmatter,
termes obligatoires, absence de reliquats (Palmier Pro), licences tierces.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / ".claude" / "skills"


def texte(rel: str) -> str:
    return (REPO / rel).read_text(encoding="utf-8")


def frontmatter(chemin: Path) -> dict[str, str]:
    """Clés simples (name, description, tools) du frontmatter YAML d'une skill ou d'un agent."""
    contenu = chemin.read_text(encoding="utf-8")
    bloc = re.match(r"^---\n(.*?)\n---\n", contenu, re.S)
    assert bloc, f"{chemin} : frontmatter absent"
    resultat = {}
    for ligne in bloc.group(1).splitlines():
        cle = re.match(r"^([a-z_-]+):\s*(.*)$", ligne)
        if cle:
            resultat[cle.group(1)] = cle.group(2).strip()
    return resultat


# ------------------------------------------------------------------ Manim (tâche 8)

@pytest.mark.parametrize("nom, sous_dossier, minimum", [
    ("manim-composer", "references", 3),
    ("manim-ce", "rules", 20),
])
def test_manim_vendorise(nom, sous_dossier, minimum):
    dossier = SKILLS / nom
    skill = dossier / "SKILL.md"
    assert frontmatter(skill)["name"] == nom
    contenu = skill.read_text(encoding="utf-8")
    assert "adithya-s-k/manim_skill" in contenu and "cef0450" in contenu
    assert "video-production" in contenu and "01-brand/tokens.json" in contenu
    assert "MIT License" in (dossier / "LICENSE.txt").read_text(encoding="utf-8")
    assert len(list((dossier / sous_dossier).glob("*.md"))) >= minimum
    assert not list(dossier.rglob("*.py")), "aucun script Python vendorisé (politique du template)"


def test_registre_video_cite_manim():
    registre = texte("docs/vendored-video.md")
    assert "cef045011722d285692e3381d12d4d637da56e18" in registre and "MIT" in registre

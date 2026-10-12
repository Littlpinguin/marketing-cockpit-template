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


# ------------------------------------------------------------------ doctrine (tâche 9)

DOCTRINE = {
    "08-video/narration.md": ["## Arc d'un explainer", "## Écrire pour l'oreille", "## Calibrer la longueur",
                              "## Direction de voix", "## Mix voix et musique", "## Divulgation", "## Check-list"],
    "08-video/motion.md": ["## Profil de goût", "## Revue de singularité", "## Promesse de mouvement et variété",
                           "## Choisir le moteur", "## Repères typographiques", "## 3D", "## Personnages",
                           "## Encre", "## Manim", "## Interdits"],
    "08-video/documentaire.md": ["## Ton", "## Du thème aux emplacements", "## Règles de sélection",
                                "## Étalonnage d'archives", "## Crédits et licences", "## Outillage", "## Check-list"],
}


@pytest.mark.parametrize("rel, titres", DOCTRINE.items())
def test_doctrine_nouvelle(rel, titres):
    contenu = texte(rel)
    for titre in titres:
        assert titre in contenu, f"{rel} : section « {titre} » absente"
    assert "—" not in contenu, f"{rel} : tiret cadratin"
    assert "OpenMontage" in contenu and "docs/vendored-video.md" in contenu


def test_doctrine_enrichie():
    formats = texte("08-video/formats.md")
    assert "## Format court : repères de production" in formats
    assert "plateformes.toml" in formats and "qa-video.py" in formats
    montage = texte("08-video/montage.md")
    assert "## Démo produit et capture d'écran" in montage
    motion = texte("08-video/motion.md")
    for terme in ("brand-frame.py", "frame.md", "design-taste", "hyperframes", "manim-composer", "ink-theater"):
        assert terme in motion, terme
    documentaire = texte("08-video/documentaire.md")
    for terme in ("corpus.py", "credits.md", "01-brand/droits.md", "selections.json"):
        assert terme in documentaire, terme

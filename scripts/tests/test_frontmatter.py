"""Le frontmatter de chaque agent, skill et commande de .claude/ se lit en YAML strict.

Un frontmatter mal formé ne se voit pas à l'usage : Claude Code ignore sans avertissement un agent dont le
YAML ne se lit pas, et charge une skill sans sa description, si bien qu'elle ne se déclenche plus seule
(documentation Claude Code, pages sub-agents et skills). Cas courant : une description non protégée qui
contient un deux-points suivi d'une espace. Corriger avec des guillemets doubles ou un bloc `>-`.

Lancé en CI par .github/workflows/frontmatter.yml.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[2]
CLAUDE = REPO / ".claude"

# Skills dont le frontmatter est encore invalide, à réparer (audit du 2026-11-03). La liste ne doit que
# rétrécir : test_en_attente_toujours_invalides échoue dès qu'une skill réparée y reste.
EN_ATTENTE = {"accessibility-web", "cro-popup", "landing-page", "n8n-builder", "print"}


def fichiers():
    yield from sorted((CLAUDE / "agents").glob("*.md"))
    yield from sorted((CLAUDE / "skills").glob("*/SKILL.md"))
    yield from sorted((CLAUDE / "commands").glob("*.md"))


def bloc_frontmatter(chemin: Path) -> str | None:
    texte = chemin.read_text(encoding="utf-8")
    if not texte.startswith("---"):
        return None
    fin = texte.find("\n---", 3)
    assert fin > 0, "frontmatter ouvert par --- mais jamais fermé"
    return texte[3:fin]


@pytest.mark.parametrize("chemin", list(fichiers()), ids=lambda p: str(p.relative_to(REPO)))
def test_frontmatter_yaml_strict(chemin: Path):
    bloc = bloc_frontmatter(chemin)
    est_commande = chemin.parent.name == "commands"
    if bloc is None:
        if est_commande:
            pytest.skip("commande sans frontmatter")
        pytest.fail("frontmatter absent")
    if chemin.name == "SKILL.md" and chemin.parent.name in EN_ATTENTE:
        pytest.xfail("frontmatter invalide connu, à réparer (audit du 2026-11-03)")
    donnees = yaml.safe_load(bloc)
    assert isinstance(donnees, dict), "le frontmatter doit être une suite de clés et de valeurs"
    if not est_commande:
        assert donnees.get("description"), "description absente : la skill ou l'agent ne se déclenche pas"
    if chemin.parent.name == "agents":
        assert donnees.get("name"), "name absent : Claude Code ignore l'agent"


def test_en_attente_toujours_invalides():
    """Une skill réparée sort de EN_ATTENTE, sinon la liste masquerait une régression future."""
    reparees = []
    for nom in sorted(EN_ATTENTE):
        try:
            yaml.safe_load(bloc_frontmatter(CLAUDE / "skills" / nom / "SKILL.md") or "")
        except yaml.YAMLError:
            continue
        reparees.append(nom)
    assert not reparees, f"retirer de EN_ATTENTE : {', '.join(reparees)}"

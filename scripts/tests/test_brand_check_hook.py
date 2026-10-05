"""Tests de .claude/hooks/brand-check-reminder.py (gate de marque au fil de l'eau).

Le hook est un PostToolUse : il ne doit jamais bloquer une écriture, jamais lever,
et toujours sortir en 0. Quand `scripts/lint-brand.py` est joignable, il joint le
constat déterministe au rappel ; sinon il retombe sur le rappel seul.

Les brouillons sont écrits dans un dossier temporaire ; le linter tourne avec la
configuration livrée du dépôt. Dans le template, 01-brand/tokens.json n'existe
pas encore : seules les règles de texte s'appliquent, ce qui suffit ici.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / ".claude" / "hooks" / "brand-check-reminder.py"


def _charger():
    """Charge le hook par chemin : son nom contient des tirets."""
    spec = importlib.util.spec_from_file_location("brand_check_reminder", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


hook = _charger()


def executer(monkeypatch, capsys, payload: dict) -> tuple[int, str]:
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    code = hook.main()
    return code, capsys.readouterr().out


def brouillon(tmp_path: Path, nom: str, contenu: str) -> Path:
    draft = tmp_path / "03-social-media" / "linkedin" / nom
    draft.parent.mkdir(parents=True, exist_ok=True)
    draft.write_text(contenu, encoding="utf-8")
    return draft


# --- Routage par chemin ------------------------------------------------------

@pytest.mark.parametrize(
    "chemin, attendu",
    [
        ("/repo/03-social-media/linkedin/post-lancement.md", True),
        ("/repo/05-web-content/landing-pages/offre.html", True),
        ("/repo/06-graphic-design/presentations/decks/deck-2026.html", True),
        ("/repo/09-seo/articles/guide-2026.md", True),
        ("/repo/03-social-media/CLAUDE.md", False),
        ("/repo/03-social-media/examples/post-publie.md", False),
        ("/repo/01-brand/voice.md", False),
        ("/repo/04-email/newsletter/push.py", False),
        ("/repo/04-email/promos/[WIP]-promo.md", False),
        ("", False),
    ],
)
def test_should_trigger(chemin, attendu):
    assert hook.should_trigger(chemin) is attendu


# --- main() sur un payload simulé -------------------------------------------

def test_payload_sans_file_path(monkeypatch, capsys):
    code, sortie = executer(monkeypatch, capsys, {"tool_input": {}})
    assert code == 0
    assert sortie.strip() == "" or json.loads(sortie) == {}


def test_payload_illisible(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("pas du json"))
    assert hook.main() == 0
    assert capsys.readouterr().out.strip() == ""


def test_fichier_de_production_avec_une_erreur(tmp_path, monkeypatch, capsys):
    draft = brouillon(tmp_path, "post.md", "Une première idée — une seconde idée\n")

    code, sortie = executer(monkeypatch, capsys, {"tool_input": {"file_path": str(draft)}})
    assert code == 0

    contexte = json.loads(sortie)["hookSpecificOutput"]["additionalContext"]
    assert "LINT DE MARQUE" in contexte
    assert "1 erreur" in contexte
    assert "dashes" in contexte
    assert "BRAND CHECK REQUIRED" in contexte


def test_fichier_de_production_sans_constat(tmp_path, monkeypatch, capsys):
    draft = brouillon(tmp_path, "propre.md", "Une première idée, puis une seconde\n")

    _, sortie = executer(monkeypatch, capsys, {"tool_input": {"file_path": str(draft)}})
    contexte = json.loads(sortie)["hookSpecificOutput"]["additionalContext"]
    assert "LINT DE MARQUE" in contexte
    assert "aucun constat" in contexte


def test_linter_absent_retombe_sur_le_rappel(tmp_path, monkeypatch, capsys):
    draft = brouillon(tmp_path, "post.md", "Une première idée — une seconde idée\n")
    monkeypatch.setattr(hook, "LINTER", tmp_path / "lint-brand-absent.py")

    code, sortie = executer(monkeypatch, capsys, {"tool_input": {"file_path": str(draft)}})
    assert code == 0

    contexte = json.loads(sortie)["hookSpecificOutput"]["additionalContext"]
    assert "LINT DE MARQUE" not in contexte
    assert "BRAND CHECK REQUIRED" in contexte


def test_linter_qui_plante_ne_bloque_pas(tmp_path, monkeypatch, capsys):
    draft = brouillon(tmp_path, "post.md", "Une idée\n")

    def exploser(*_args, **_kwargs):
        raise RuntimeError("sous-processus indisponible")

    monkeypatch.setattr(hook.subprocess, "run", exploser)

    code, sortie = executer(monkeypatch, capsys, {"tool_input": {"file_path": str(draft)}})
    assert code == 0
    contexte = json.loads(sortie)["hookSpecificOutput"]["additionalContext"]
    assert "LINT DE MARQUE" not in contexte
    assert "BRAND CHECK REQUIRED" in contexte


def test_sortie_du_lint_tronquee(tmp_path, monkeypatch, capsys):
    draft = brouillon(tmp_path, "long.md", "Une ligne — fautive\n" * 60)

    _, sortie = executer(monkeypatch, capsys, {"tool_input": {"file_path": str(draft)}})
    contexte = json.loads(sortie)["hookSpecificOutput"]["additionalContext"]
    lignes_lint = [ligne for ligne in contexte.splitlines() if "[dashes]" in ligne]
    assert len(lignes_lint) == hook.MAX_LIGNES_LINT
    assert "autres constats" in contexte


def test_rapport_de_lint_malforme_retombe_sur_le_rappel(tmp_path, monkeypatch, capsys):
    """Un `findings` qui n'est pas une liste ne doit produire aucun traceback."""
    draft = brouillon(tmp_path, "post.md", "Une idée\n")

    class FauxResultat:
        stdout = '{"summary": {"errors": 1, "warnings": 0}, "findings": "pas une liste"}'
        stderr = ""
        returncode = 1

    monkeypatch.setattr(hook.subprocess, "run", lambda *a, **k: FauxResultat())

    code, sortie = executer(monkeypatch, capsys, {"tool_input": {"file_path": str(draft)}})
    assert code == 0
    contexte = json.loads(sortie)["hookSpecificOutput"]["additionalContext"]
    assert "LINT DE MARQUE" not in contexte
    assert "BRAND CHECK REQUIRED" in contexte


def test_summary_absent_retombe_sur_le_rappel(tmp_path, monkeypatch, capsys):
    draft = brouillon(tmp_path, "post.md", "Une idée\n")

    class FauxResultat:
        stdout = '{"autre": 1}'
        stderr = ""
        returncode = 0

    monkeypatch.setattr(hook.subprocess, "run", lambda *a, **k: FauxResultat())

    _, sortie = executer(monkeypatch, capsys, {"tool_input": {"file_path": str(draft)}})
    contexte = json.loads(sortie)["hookSpecificOutput"]["additionalContext"]
    assert "LINT DE MARQUE" not in contexte
    assert "BRAND CHECK REQUIRED" in contexte

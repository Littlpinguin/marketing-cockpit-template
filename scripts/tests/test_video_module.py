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


# ------------------------------------------------------------------ nouvelles skills (tâche 10)

NOUVELLES = {
    "video-production": ["brief.md", "REPRISE.md", "decisions.md", "couts.md", "BRIEF.md", "frame.md",
                         "brand-frame.py", "qa-video.py", "video-reviewer", "storyboard: yes",
                         "hyperframes:faceless-explainer", "hyperframes:product-launch-video",
                         "hyperframes:motion-graphics", "hyperframes:general-video", "hyperframes:pr-to-video",
                         "hyperframes:music-to-video", "reel-talking-head", "video-repurpose", "video-documentary",
                         "manim-composer", "`slides`", "/modules", "account_balance", "02-strategy/calendar/calendar.md"],
    "motion-design": ["frame.md", "brand.css", "brand-frame.py", "references/3d.md", "references/personnages.md",
                      "references/encre.md", "08-video/motion.md", "design-taste", "hf-seek", "data-duration",
                      "document.fonts.ready", "npx hyperframes lint", "frame-presets", "hyperframes:hyperframes-registry",
                      "manim"],
    "video-repurpose": ["se comprend sans contexte", "whisper", "captions", "9:16", "qa-video.py", "video-editing",
                        "02-strategy/calendar/calendar.md"],
    "video-documentary": ["corpus.py build", "corpus.py index", "corpus.py search", "corpus.py credits",
                          "selections.json", "08-video/documentaire.md", "requirements-corpus.txt",
                          "hyperframes:general-video", "narration.md"],
}
REFERENCES_MOTION = {
    "3d.md": ["Three.js", "hf-seek", "data-duration", "Poly Haven", "01-brand/droits.md", "models3d"],
    "personnages.md": ["Lottie", "ink-puppet", "fiche personnage", "poses"],
    "encre.md": ["InkTheater.attach", "08-video/lib/ink-theater", "InkPuppet.create", "brand.css", "InkClips"],
}


@pytest.mark.parametrize("nom, termes", NOUVELLES.items())
def test_nouvelle_skill(nom, termes):
    chemin = SKILLS / nom / "SKILL.md"
    assert frontmatter(chemin)["name"] == nom
    assert len(frontmatter(chemin).get("description", "")) > 80
    contenu = chemin.read_text(encoding="utf-8")
    manquants = [t for t in termes if t not in contenu]
    assert not manquants, f"{nom} : termes absents {manquants}"
    assert "OpenMontage" in contenu and "docs/vendored-video.md" in contenu
    assert "palmier" not in contenu.lower() and "—" not in contenu


@pytest.mark.parametrize("fichier, termes", REFERENCES_MOTION.items())
def test_references_motion(fichier, termes):
    contenu = (SKILLS / "motion-design" / "references" / fichier).read_text(encoding="utf-8")
    manquants = [t for t in termes if t not in contenu]
    assert not manquants, f"{fichier} : termes absents {manquants}"


# ------------------------------------------------------------------ correctifs de revue (tâches 9 et 10)

def _textes_video_nouveaux():
    chemins = [*sorted((REPO / "08-video").glob("*.md")),
               *(SKILLS / nom / "SKILL.md" for nom in NOUVELLES),
               *sorted((SKILLS / "motion-design" / "references").glob("*.md"))]
    return {chemin: chemin.read_text(encoding="utf-8") for chemin in chemins}


def test_commandes_audio_hyperframes_reelles():
    narration = texte("08-video/narration.md")
    assert "--provider" not in narration, "npx hyperframes tts n'a pas d'option --provider"
    assert "npx hyperframes tts" in narration and "ff_siwis" in narration
    for chemin, contenu in _textes_video_nouveaux().items():
        assert "hyperframes bgm" not in contenu, f"{chemin} : la commande bgm n'existe pas"


def test_passation_porte_voix_musique_et_sous_titres():
    contenu = (SKILLS / "video-production" / "SKILL.md").read_text(encoding="utf-8")
    for terme in ("voice: ff_siwis", "music: none", "caption-skin.html", "auth status"):
        assert terme in contenu, terme


@pytest.mark.parametrize("nom", NOUVELLES)
def test_checklist_avant_livraison(nom):
    assert "## Checklist avant livraison" in (SKILLS / nom / "SKILL.md").read_text(encoding="utf-8")


def test_motion_design_references_a_charger():
    assert "## Références à charger" in (SKILLS / "motion-design" / "SKILL.md").read_text(encoding="utf-8")


def test_theme_d_exemple_decrit_en_anglais():
    import tomllib
    theme = tomllib.loads(texte("08-video/corpus/themes/exemple-savoir-faire.toml"))
    assert all(e["description"].isascii() for e in theme["emplacements"]), "descriptions CLIP en anglais"
    geste = next(e for e in theme["emplacements"] if e["id"] == "geste")
    assert f'description = "{geste["description"]}"' in texte("08-video/documentaire.md"), \
        "l'extrait de documentaire.md doit reprendre le thème livré"

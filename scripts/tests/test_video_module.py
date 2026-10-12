"""Tests de structure et de câblage du module vidéo (skills, doctrine, module, documentation).

Ces tests vérifient des fichiers, pas un comportement : présence, frontmatter,
termes obligatoires, absence de reliquats de l'ancien éditeur vidéo, licences tierces.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILLS = REPO / ".claude" / "skills"
# Nom de l'éditeur retiré du module, construit à l'exécution : ce fichier ne le contient pas,
# et le test d'absence peut donc le parcourir comme les autres.
ANCIEN_EDITEUR = "pal" + "mier"


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
    assert ANCIEN_EDITEUR not in contenu.lower() and "—" not in contenu


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


# ------------------------------------------------------------------ bibliothèque d'inspiration (tâche 16)

INSPIRATION_SECTIONS = ["## Rôle", "## Chercher des références", "## Extraire le mécanisme, pas le look",
                        "## Transposer dans la marque", "## De la catégorie à la filière",
                        "## Montrer une référence au client", "## Interdits", "## Check-list"]


def _ligne(contenu: str, debut: str) -> str:
    """La ligne (puce) d'un fichier qui commence par `debut`."""
    trouvees = [ligne for ligne in contenu.splitlines() if ligne.startswith(debut)]
    assert len(trouvees) == 1, f"{debut!r} : {len(trouvees)} ligne(s)"
    return trouvees[0]


def test_doctrine_inspiration():
    contenu = texte("08-video/inspiration.md")
    positions = [contenu.find(titre) for titre in INSPIRATION_SECTIONS]
    assert all(p >= 0 for p in positions), [t for t, p in zip(INSPIRATION_SECTIONS, positions) if p < 0]
    assert positions == sorted(positions), "sections dans l'ordre de la spec"
    assert "—" not in contenu, "tiret cadratin"
    for terme in ("inspiration.py", "references.md", "frame.md", "brand.css", "01-brand/voice.md", "08-video/motion.md",
                  "revue de singularité", "profil de goût", "tropes bannis", "référence → transposition",
                  "mécanisme", "Structure dans le temps", "Rythme", "Transitions", "en anglais", "Check-list"):
        assert terme in contenu, terme
    pied = contenu.rstrip().splitlines()[-1]
    assert "https://github.com/yihui-dev/awesome-opus5-5-videos" in pied
    assert "chaque vidéo et chaque prompt appartient à son créateur" in pied


def test_inspiration_table_categorie_filiere_et_techs():
    contenu = texte("08-video/inspiration.md")
    production = texte(".claude/skills/video-production/SKILL.md")
    for filiere in ("hyperframes:motion-graphics", "hyperframes:general-video", "hyperframes:faceless-explainer"):
        assert filiere in contenu and filiere in production, f"{filiere} : même nom dans la doctrine et dans la skill"
    for terme in ("`motion`", "`explainer`", "`3d`", "`interactive`", ".claude/skills/motion-design/references/3d.md",
                  "landing-page", "Démo produit et capture d'écran", "hyperframes:hyperframes-audio", "hf-seek",
                  "Three.js", "`gsap`", "`canvas`", "`shader`", "`threejs`", "`audio`"):
        assert terme in contenu, terme
    assert (REPO / ".claude/skills/motion-design/references/3d.md").is_file()


def test_inspiration_interdits_et_propriete():
    contenu = texte("08-video/inspiration.md")
    interdits = contenu.split("## Interdits")[1].split("## Check-list")[0]
    for idee in ("Recopier le prompt", "visuels ou le code", "création de l'agence", "vidéo virale identifiable",
                 "données tierces"):
        assert idee in interdits, idee
    assert "jamais une capture" in contenu
    assert ".cache/inspiration/" in contenu


def test_inspiration_cablee_dans_les_skills():
    production = texte(".claude/skills/video-production/SKILL.md")
    concepts = production.split("2. **Concepts.**")[1].split("→ **Validation 1")[0]
    for terme in ("08-video/scripts/inspiration.py", "08-video/inspiration.md", "références", "lien", "créateur",
                  "references.md"):
        assert terme in concepts, f"étape Concepts : {terme}"
    storyboard = production.split("4. **Storyboard.**")[1].split("→ **Validation 3")[0]
    assert "référence → transposition" in storyboard and "references.md" in storyboard
    assert "references.md" in production.split("### `brief.md`")[0], "références.md figure dans l'arborescence du projet"
    motion = texte(".claude/skills/motion-design/SKILL.md")
    assert "08-video/inspiration.md" in motion.split("## Charte du projet")[0], "renvoi dans « Références à charger »"
    assert (REPO / "08-video/scripts/inspiration.py").is_file()


def test_pas_de_musique_hors_ligne_pour_les_workflows_scriptes():
    production = texte(".claude/skills/video-production/SKILL.md")
    connexion = _ligne(production, "- **Connexion et médias.**")
    musique = _ligne(production, "- **Musique : la licence d'abord, même gratuite.**")
    for ligne in (connexion, musique):
        for workflow in ("faceless-explainer", "product-launch-video", "pr-to-video"):
            assert workflow in ligne, workflow
        assert "hyperframes:general-video" in ligne and "usage direct du moteur" in ligne
        assert "MusicGen" in ligne and "Lyria" in ligne
    assert "aucune musique" in connexion and "récupérer chez HeyGen" in connexion
    assert "n'en ont aucune hors ligne" in musique
    assert "CC BY-NC 4.0" in musique and "01-brand/droits.md" in production, "contrôle de licence MusicGen conservé"
    assert "la musique est générée (Lyria" not in production, "ancienne affirmation retirée"


def test_frame_presets_hors_peau_de_sous_titres():
    production = texte(".claude/skills/video-production/SKILL.md")
    assert "(hors la peau de sous-titres)" in _ligne(production, "Rappels : jamais de preset `frame-presets`")
    motion = texte(".claude/skills/motion-design/SKILL.md")
    assert "(hors la peau de sous-titres)" in _ligne(motion, "- [ ] Aucun preset `frame-presets`")


def test_voix_payante_met_a_jour_voice_apres_l_echantillon():
    production = texte(".claude/skills/video-production/SKILL.md")
    bloc = _ligne(production, "- **Voix et storyboard.**")
    apres = bloc.split("échantillon payant annoncé et validé")[1]
    assert "validation 3" in apres and "mettre `voice:` à jour dans `BRIEF.md`" in apres
    assert apres.index("mettre `voice:` à jour") < apres.index("avant de lancer l'étape audio")


# ------------------------------------------------------------------ skills refondues, agent (tâche 11)

REFONDUES = {
    "video-editing": ["hyperframes:talking-head-recut", "hyperframes:general-video", "silencedetect",
                      "qa-video.py", "08-video/projets/", "montage.md", "formats.md", "loudnorm"],
    "captions": ["hyperframes:embedded-captions", "whisper", "formats.md", ".srt"],
    "reel-talking-head": ["qa-video.py", "video-reviewer", "video-production", "Format court"],
    "video-generation": ["sujet", "mouvement", "scène", "espace", "caméra", "## Stock ou génération",
                         "## Choisir un fournisseur", "video-model-scout", "video-production", "fidélité"],
}


@pytest.mark.parametrize("nom, termes", REFONDUES.items())
def test_skill_refondue(nom, termes):
    chemin = SKILLS / nom / "SKILL.md"
    assert frontmatter(chemin)["name"] == nom
    contenu = chemin.read_text(encoding="utf-8")
    manquants = [t for t in termes if t not in contenu]
    assert not manquants, f"{nom} : termes absents {manquants}"
    assert ANCIEN_EDITEUR not in contenu.lower() and "—" not in contenu


@pytest.mark.parametrize("nom", ["video-generation", "reel-talking-head"])
def test_pied_de_page_openmontage(nom):
    pied = (SKILLS / nom / "SKILL.md").read_text(encoding="utf-8").rstrip().splitlines()[-1]
    assert "OpenMontage" in pied and "docs/vendored-video.md" in pied


def test_agent_video_reviewer():
    chemin = REPO / ".claude" / "agents" / "video-reviewer.md"
    meta = frontmatter(chemin)
    assert meta["name"] == "video-reviewer"
    assert set(t.strip() for t in meta["tools"].split(",")) == {"Bash", "Read", "Glob", "Grep"}
    contenu = chemin.read_text(encoding="utf-8")
    for terme in ("qa-video.py", "planche", "brand-frame.py --check", "P1", "P2", "P3",
                  "01-brand/divulgation-ia.md", "01-brand/droits.md", "brief.md", "lecture seule"):
        assert terme in contenu, terme
    assert ANCIEN_EDITEUR not in contenu.lower() and "—" not in contenu


# ------------------------------------------------------------------ câblage du module (tâche 12)

import json
import subprocess


def test_commande_modules():
    modules = texte(".claude/commands/modules.md")
    for terme in ("claude plugin marketplace add heygen-com/hyperframes --scope local",
                  "claude plugin install hyperframes@hyperframes --scope local",
                  "npx --yes hyperframes doctor", "node --version", "ffprobe", "WHISPER_MODEL",
                  "import open_clip", "manim --version", '"capacites"', '"hyperframes"'):
        assert terme in modules, terme
    assert ANCIEN_EDITEUR not in modules.lower()
    sante = texte(".claude/commands/health-check.md")
    assert "hyperframes@hyperframes" in sante and ANCIEN_EDITEUR not in sante.lower()


def test_schema_du_module_video():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(texte("docs/setup-completed.schema.json"))
    video = {"enabled": True, "checked_at": "2026-10-12T10:00:00Z", "hyperframes": "0.8.149",
             "capacites": {"whisper": True, "manim": False, "corpus": False}}
    sous_schema = schema["properties"]["modules"]["properties"]["video"]
    resolveur = {"$defs": schema["$defs"], **sous_schema}
    jsonschema.validate(video, resolveur)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**video, "capacites": {"whisper": "oui"}}, resolveur)


@pytest.mark.parametrize("chemin, ignore", [
    ("08-video/projets/demo/rushes/a.mp4", True),
    ("08-video/projets/demo/exports/demo-reels.mp4", True),
    ("08-video/projets/demo/hyperframes/node_modules/x.js", True),
    ("08-video/projets/demo/hyperframes/assets/voix.wav", True),
    ("08-video/projets/demo/hyperframes/renders/demo_2026-10-12_10-00-00.mp4", True),
    ("08-video/projets/demo/hyperframes/snapshots/frame-01.png", True),
    ("08-video/projets/demo/hyperframes/frames_fg/000001.png", True),
    ("08-video/projets/demo/hyperframes-sous-titres/frames_fg/000001.png", True),
    ("08-video/projets/demo/hyperframes-sous-titres/frames_bg/000001.png", True),
    ("08-video/projets/demo/hyperframes/.media/audio/voice/l1.wav", True),
    ("08-video/projets/demo/hyperframes/.media/image/fond.png", True),
    ("08-video/projets/demo/hyperframes-sous-titres/renders/final.mp4", True),
    ("08-video/projets/demo/hyperframes/assets/fonts/Marque-Regular.woff2", False),
    ("08-video/projets/demo/hyperframes/assets/logo.svg", False),
    ("08-video/projets/demo/hyperframes-sous-titres/theme.json", False),
    ("08-video/projets/demo/qa/demo-reels/planche.jpg", True),
    ("08-video/projets/demo/qa/demo-reels/rapport.json", True),
    ("08-video/projets/demo/qa/demo-reels/rapport.md", False),
    ("08-video/projets/demo/brief.md", False),
    ("08-video/projets/demo/references.md", False),
    ("08-video/projets/demo/sous-titres/demo-reels.srt", False),
    ("08-video/projets/demo/hyperframes/index.html", False),
    ("08-video/corpus/savoir-faire/clips/a.mp4", True),
    ("08-video/corpus/themes/exemple-savoir-faire.toml", False),
    ("08-video/rushes/vieux.mp4", True),
    ("08-video/exports/vieux-reels.mp4", True),
])
def test_gitignore_du_module(chemin, ignore):
    res = subprocess.run(["git", "check-ignore", "-q", "--no-index", chemin], cwd=REPO)
    assert (res.returncode == 0) is ignore, chemin


def test_env_et_inventaire():
    env = texte(".env.example")
    assert 'PIXABAY_API_KEY=""' in env and 'WHISPER_MODEL=""' in env
    assert 'dossier = "08-video/projets"' in texte("scripts/build-inventory.toml")
    assert "`video`" in texte("_templates/inventory.md")


def test_role_08_video():
    role = texte("08-video/CLAUDE.md")
    readme = texte("08-video/README.md")
    for terme in ("video-production", "hyperframes", "qa-video.py", "brand-frame.py", "08-video/projets/<slug>/"):
        assert terme in role, terme
    for skill in ("video-production", "motion-design", "video-editing", "captions", "reel-talking-head",
                  "video-generation", "video-matting", "video-repurpose", "video-documentary", "manim-composer",
                  "manim-ce"):
        assert skill in readme, skill
    for terme in ("inspiration.py", "inspiration.md", "references.md"):
        assert terme in role and terme in readme, terme
    for script in ("qa-video.py", "brand-frame.py", "bvh2clip.py", "corpus.py", "inspiration.py"):
        assert f"`{script}`" in readme, script
    assert ANCIEN_EDITEUR not in (role + readme).lower()
    assert "—" not in role + readme


# ------------------------------------------------------------------ correctifs de revue (tâches 11 et 12)

import importlib.util


def _charger(nom: str, chemin: Path):
    spec = importlib.util.spec_from_file_location(nom, chemin)
    module = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[nom] = module    # les dataclasses ont besoin du module enregistré
    spec.loader.exec_module(module)
    return module


def _modele_script() -> str:
    """Le modèle de script.md tel que le donne video-production."""
    production = texte(".claude/skills/video-production/SKILL.md")
    section = production.split("### `script.md`")[1].split("## Choisir la filière")[0]
    return section.split("```markdown\n")[1].split("```")[0]


def test_script_du_modele_entre_a_l_inventaire(tmp_path):
    inventaire = _charger("build_inventory_video", REPO / "scripts" / "build-inventory.py")
    inventaire.charger_config(REPO / "scripts" / "build-inventory.toml")
    contenu = (_modele_script()
               .replace("<AAAA-MM-JJ>", "2026-10-12")
               .replace("<sujet de la vidéo, 5 à 10 mots>", "Explainer sur le reporting hebdomadaire")
               .replace("<titre de travail>", "Le reporting en 45 secondes"))
    rel = Path("08-video/projets/2026-10-12-exemple/script.md")
    (tmp_path / rel).parent.mkdir(parents=True)
    (tmp_path / rel).write_text(contenu, encoding="utf-8")
    livrable = inventaire.extraire(tmp_path, rel)
    assert livrable is not None
    assert (livrable.date, livrable.canal, livrable.type) == ("2026-10-12", "video", "video")
    assert livrable.sujet == "Explainer sur le reporting hebdomadaire"
    assert livrable.statut == "brouillon"
    qa = _charger("qa_video_modele", REPO / "08-video" / "scripts" / "qa-video.py")
    assert qa.texte_attendu(contenu, ".md") == "<texte dit>", "la colonne Voix reste lisible sous le frontmatter"


def test_slug_date_et_frontmatter_documentes():
    for rel in (".claude/skills/video-production/SKILL.md", "08-video/CLAUDE.md",
                ".claude/skills/reel-talking-head/SKILL.md", ".claude/skills/video-repurpose/SKILL.md",
                ".claude/skills/video-documentary/SKILL.md"):
        contenu = texte(rel)
        assert "AAAA-MM-JJ-<sujet>" in contenu, rel
    for rel in ("08-video/CLAUDE.md", ".claude/skills/video-production/SKILL.md"):
        assert "subject" in texte(rel) and "statut" in texte(rel), rel
    assert "sous-titres/" in texte(".claude/skills/video-production/SKILL.md").split("### `brief.md`")[0]


def test_transcription_hyperframes_toujours_en_francais():
    chemins = [*(REPO / "08-video").glob("*.md"), *SKILLS.glob("*/SKILL.md")]
    for chemin in chemins:
        for ligne in chemin.read_text(encoding="utf-8").splitlines():
            if "hyperframes transcribe <" in ligne or "hyperframes transcribe rushes" in ligne:
                assert "--model small" in ligne and "--language fr" in ligne, f"{chemin} : {ligne}"


def test_livrable_sous_titre_est_l_export_controle():
    captions = texte(".claude/skills/captions/SKILL.md")
    assert "tiktok-sous-titres.mp4" not in captions and "<video>-sous-titres" not in captions
    assert "rushes/tmp/<slug>-<plateforme>-sans-sous-titres.mp4" in captions
    assert "exports/<slug>-<plateforme>.mp4" in captions


def test_generation_sans_echo_openmontage():
    generation = texte(".claude/skills/video-generation/SKILL.md")
    for echo in ("trois à six", "mot pour mot", "le même personnage", "comment tout cela change"):
        assert echo not in generation, echo


def test_mineurs_de_revue():
    modules = texte(".claude/commands/modules.md")
    activation = modules.split("#### Activation du module `video`")[1].split("### Étape 4")[0]
    assert activation.index("npx --yes hyperframes doctor") < activation.index("claude plugin install")
    assert "claude plugin uninstall hyperframes@hyperframes --scope local" in activation
    reviewer = texte(".claude/agents/video-reviewer.md")
    assert "Sortie 2" in reviewer and "tokens eux-mêmes sont invalides" in reviewer
    editing = texte(".claude/skills/video-editing/SKILL.md")
    assert "tâche de fond" in editing and "cd 08-video/projets/<slug>" in editing
    assert "~ is expanded" in texte(".env.example")
    reel = texte(".claude/skills/reel-talking-head/SKILL.md")
    assert "passe la séquence telle quelle" in reel and "rushes/tmp/" in reel
    assert "08-video/projets/<slug>/hyperframes-sous-titres/" in texte(".claude/skills/captions/SKILL.md")


# ------------------------------------------------------------------ documentation (tâche 13)

def test_plus_d_ancien_editeur_hors_changelog():
    """Fichiers suivis ou à suivre par git (pas les fichiers locaux ignorés comme .mcp.json).

    Seuls l'historique (CHANGELOG.md), l'archive de la v0.1 et les specs locales sont exclus.
    """
    liste = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                           cwd=REPO, capture_output=True, text=True, check=True).stdout.splitlines()
    suffixes = {".md", ".json", ".toml", ".py", ".yml", ".yaml", ".html", ".txt", ".example", ".js", ".sh", ".css"}
    fautifs = []
    for rel in liste:
        chemin = REPO / rel
        if rel == "CHANGELOG.md" or rel.startswith((".setup-archive/", "docs/superpowers/")) or not chemin.is_file():
            continue
        if chemin.suffix not in suffixes:
            continue
        if ANCIEN_EDITEUR in chemin.read_text(encoding="utf-8", errors="ignore").lower():
            fautifs.append(rel)
    assert not fautifs, fautifs


def test_claude_md_racine():
    racine = texte("CLAUDE.md")
    for terme in ("video-production", "motion-design", "video-repurpose", "video-documentary", "manim-composer",
                  "video-reviewer", "qa-video.py", "brand-frame.py --check", "hyperframes@hyperframes"):
        assert terme in racine, terme


def test_registre_complet():
    registre = texte("docs/vendored-video.md")
    for terme in ("9327439db69021ab4b0e2776729bf3b58fdb5a87", "AGPL", "Apache-2.0", "salle blanche",
                  "hyperframes@hyperframes", "Patrick Hand", "mocap.cs.cmu.edu", "cef0450"):
        assert terme in registre, terme
    for terme in ("yihui-dev/awesome-opus5-5-videos", "e6c7eee870cbd6d40825d6348a0c5782b3721fe9",
                  "08-video/scripts/inspiration.py", ".cache/inspiration/"):
        assert terme in registre, terme


def test_changelog_non_publie():
    changelog = texte("CHANGELOG.md")
    non_publie = changelog.split("## [Unreleased]")[1].split("\n## [")[0]
    for terme in ("HyperFrames", ANCIEN_EDITEUR.capitalize(), "OpenMontage", "qa-video.py", "Migration"):
        assert terme in non_publie, terme
    for terme in ("gemini-nano-banana-2.1", "GOOGLE_AI_IMAGE_MODEL", "awesome-opus5-5-videos", "`gemini-3-pro-image`",
                  "sync-template", "build-inventory.toml", "`08-video/projets` source"):
        assert terme in non_publie, terme
    migration = non_publie.split("**Migration (configured forks).**")[1]
    video, image = migration.split("Every fork that uses image generation")
    assert "GOOGLE_AI_IMAGE_MODEL" not in video and "GOOGLE_AI_IMAGE_MODEL" in image


def test_etat_de_l_art_et_architecture():
    ecosysteme = texte("docs/etat-de-lart/ecosysteme-skills.md")
    assert "hyperframes@hyperframes" in ecosysteme
    assert "calesthio/OpenMontage" in ecosysteme and "adithya-s-k/manim_skill" in ecosysteme
    sans_precision = [ligne for ligne in ecosysteme.splitlines()
                      if re.search(r"\bhyperframes\b", ligne) and "hyperframes@hyperframes" not in ligne]
    assert not sans_precision, "hyperframes : préciser qu'il est installé par le module vidéo"
    architecture = texte("docs/architecture.md")
    assert "video-editing + captions skills" not in architecture
    assert "video-production" in architecture


def test_readme_video_et_comptes():
    readme = texte("README.md")
    for terme in ("HyperFrames", "video-production", "video-reviewer", "qa-video.py", "OpenMontage"):
        assert terme in readme, terme
    competences = len(list(SKILLS.glob("*/SKILL.md")))
    agents = len(list((REPO / ".claude" / "agents").glob("*.md")))
    tableau = readme.split("organized by function")[1].split("**Brand-as-code tooling.**")[0]
    assert sum(int(n) for n in re.findall(r"\| (\d+) \|", tableau)) == competences
    assert f"**{competences} skills**" in readme and f"**{agents} agents**" in readme


def test_reviewer_porte_de_la_charte():
    reviewer = texte(".claude/agents/video-reviewer.md")
    etape = reviewer.split("### 3.")[1].split("### 4.")[0]
    assert "projet HyperFrames qui contient un `frame.md`" in etape
    assert "toile « … » non prise en charge" in etape and "dossier absent" not in etape


def test_projet_de_sous_titres_toujours_a_part():
    captions = texte(".claude/skills/captions/SKILL.md")
    assert "si la vidéo n'en a pas encore" not in captions
    assert "toujours `08-video/projets/<slug>/hyperframes-sous-titres/`" in captions
    role = texte("08-video/CLAUDE.md")
    ligne = _ligne(role, "| `hyperframes-sous-titres/` |")
    assert "frames_fg/" in ligne and "frames_bg/" in ligne
    arbre = texte(".claude/skills/video-production/SKILL.md").split("### `brief.md`")[0]
    assert "hyperframes-sous-titres/" in arbre


def test_matting_sans_editeur():
    matting = texte(".claude/skills/video-matting/SKILL.md")
    assert "éditeur" not in matting
    for terme in ("hyperframes", "video-editing", "chromakey"):
        assert terme in matting, terme


def test_manim_registre_et_pieds_de_page():
    registre = texte("docs/vendored-video.md")
    assert "(5 exemples)" not in registre and "attention/" in registre
    composer = (SKILLS / "manim-composer" / "SKILL.md").read_text(encoding="utf-8").rstrip().splitlines()[-1]
    ce = (SKILLS / "manim-ce" / "SKILL.md").read_text(encoding="utf-8").rstrip().splitlines()[-1]
    assert "Adaptations : nom" not in composer and "exemples Python" not in composer
    assert "description" in composer and "note d'intégration" in composer
    assert "manimce-best-practices" in ce and "description" in ce and "exemples Python" in ce


def test_pieds_de_page_openmontage_exacts():
    pied = ("Méthode inspirée d'OpenMontage (calesthio/OpenMontage, AGPLv3), réécrite pour le template : "
            "aucun texte ni code repris. Registre : docs/vendored-video.md.")
    porteurs = set(subprocess.run(["git", "grep", "-l", "-F", pied], cwd=REPO, capture_output=True, text=True,
                                  check=True).stdout.split()) - {"docs/vendored-video.md"}
    attendus = {*(f".claude/skills/{nom}/SKILL.md" for nom in ("video-production", "motion-design", "video-repurpose",
                                                              "video-documentary", "video-generation",
                                                              "reel-talking-head")),
                *(f".claude/skills/motion-design/references/{nom}.md" for nom in ("3d", "personnages", "encre")),
                *(f"08-video/{nom}.md" for nom in ("formats", "montage", "narration", "motion", "documentaire"))}
    assert porteurs == attendus, sorted(porteurs ^ attendus)
    phrase = _ligne(texte("docs/vendored-video.md"), "Les fichiers qui reprennent une de ces méthodes")
    for chemin in attendus:
        nom = chemin.split("/")[2] if chemin.endswith("SKILL.md") else chemin.split("/", 1)[1].replace("skills/motion-design/", "")
        assert nom in phrase, nom


def test_modules_ne_relance_pas_doctor_apres_installation():
    modules = texte(".claude/commands/modules.md")
    activation = modules.split("#### Activation du module `video`")[1].split("### Étape 4")[0]
    assert activation.count("npx --yes hyperframes doctor") == 1
    controle = _ligne(activation, "3. **Contrôler après l'installation**")
    assert "claude plugin list" in controle and "lanceur du plugin" in controle


# ------------------------------------------------------------------ revue finale de la branche

def test_doctor_montre_a_l_utilisateur_avant_de_tourner():
    modules = texte(".claude/commands/modules.md")
    activation = modules.split("#### Activation du module `video`")[1].split("### Étape 4")[0]
    accord = activation.split("2. **Montrer à l'utilisateur")[1].split("3. **Contrôler après l'installation**")[0]
    assert "npx --yes hyperframes doctor" in accord and "attendre son accord" in accord
    assert "npx --yes hyperframes doctor" not in activation.split("2. **Montrer à l'utilisateur")[0]


def test_validations_par_filiere_et_routage_du_reel():
    production = texte(".claude/skills/video-production/SKILL.md")
    table = production.split("### Validations et passage de main par filière")[1].split("## Passer la main")[0]
    for filiere in ("reel-talking-head", "video-repurpose", "video-documentary", "motion-graphics", "manim-composer",
                    "music-to-video"):
        assert filiere in table, filiere
    assert "`storyboard: no`" in table and "`storyboard: yes`" in table
    routage = _ligne(production, "| Rushes face caméra → reel |")
    assert routage.index("hyperframes:general-video") < routage.index("hyperframes:talking-head-recut")
    assert "voie ordinaire" in routage and "déjà coupée et étalonnée" in routage
    assert "(validation 3), mettre `voice:`" not in production and "après la validation 3, mettre `voice:`" in production
    assert "Pick the brand" in production and "STORYBOARD.md" in _ligne(production, "- **`hyperframes:music-to-video`.**")
    for rel in (".claude/skills/reel-talking-head/SKILL.md", ".claude/skills/video-repurpose/SKILL.md"):
        validations = texte(rel).split("## Où se placent les validations")[1].split("\n## ")[0]
        for objet in ("**Concept** (validation 1)", "**Script** (validation 2)", "**Storyboard** (validation 3)",
                      "`storyboard: no`"):
            assert objet in validations, (rel, objet)
    assert "`storyboard: no`" in texte(".claude/skills/video-documentary/SKILL.md")


def test_talking_head_recut_en_francais_et_a_la_marque():
    editing = texte(".claude/skills/video-editing/SKILL.md")
    for terme in ("« Transcribe »", "--model small.en", "--model small --language fr", "transcript.json",
                  "« Decide Render Strategy »", "brand.css", "decisions.md"):
        assert terme in editing, terme
    assert "video-editing`, voie A" in texte(".claude/skills/reel-talking-head/SKILL.md")


def test_plans_longs_alignes_sur_montage_et_qa():
    editing = texte(".claude/skills/video-editing/SKILL.md")
    assert "plus de 5 s" not in editing and "jamais plus de 4 s" in editing and "plan-long" in editing
    assert "Jamais plus de 4 s sans rupture" in texte("08-video/montage.md")


def test_transcriptions_au_mot_coherentes():
    reel = texte(".claude/skills/reel-talking-head/SKILL.md")
    assert "-ar 16000 rushes/audio.wav" in reel and "-ml 1 -sow" in reel
    repurpose = texte(".claude/skills/video-repurpose/SKILL.md")
    etape4 = repurpose.split("## Étape 4")[1].split("## Étape 5")[0]
    assert "rushes/transcription.json" in etape4 and "rushes/transcript.json" in etape4
    assert "-d rushes" in repurpose


def test_mineurs_de_la_revue_finale():
    motion = texte(".claude/skills/motion-design/SKILL.md")
    assert "../exports/<slug>-<plateforme>.mp4" in motion and "<fichier>.mp4" not in motion
    documentaire = texte(".claude/skills/video-documentary/SKILL.md")
    assert "champ `nom`" in documentaire and 'nom = "savoir-faire"' in documentaire
    for skill in ("manim-composer", "manim-ce"):
        note = texte(f".claude/skills/{skill}/SKILL.md")
        assert "-r 1080,1920" in note and "1920 × 1080" in note, skill
    unreleased = texte("CHANGELOG.md").split("## [Unreleased]")[1].split("\n## [")[0]
    migration = unreleased.split("**Migration (configured forks).**")[1]
    assert "AAAA-MM-JJ-<sujet>" in migration and "`statut`" in migration
    assert "install and version-tracking path" in texte("README.md")
    inspiration = texte("08-video/inspiration.md")
    assert "hyperframes:product-launch-video" in _ligne(inspiration, "| `motion` |")
    for terme in ("`--source`", "`--cache`", "4 lettres"):
        assert terme in inspiration, terme

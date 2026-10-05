"""Tests de scripts/lint-brand.py (linter de marque déterministe).

Toutes les données de marque sont fictives : une palette et des polices de
démonstration écrites par la fixture dans une racine jetable, et une
configuration dérivée de scripts/lint-brand.toml (la configuration livrée)
où seuls les emplacements propres à la marque sont remplis.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "lint-brand.py"
CONFIG_LIVREE = REPO / "scripts" / "lint-brand.toml"
TOKENS = "01-brand/tokens.json"


def _load_module():
    """Charge lint-brand.py par chemin : son nom contient un tiret."""
    spec = importlib.util.spec_from_file_location("lint_brand", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lint_brand = _load_module()


# Palette fictive. « illustration.shadow » est à ΔE 1.4 de l'accent mais
# restreinte à un dossier : elle sert à vérifier que la tolérance ne
# court-circuite pas la portée.
TOKENS_FICTIFS = {
    "color": {
        "$type": "color",
        "primary": {"$value": "#1E40AF", "$extensions": {"cockpit": {"deltaE_max": 2.0}}},
        "accent": {"$value": "#F59E0B", "$extensions": {"cockpit": {"deltaE_max": 2.0}}},
        "dark": {"$value": "#0F172A"},
        "light": {"$value": "#F8FAFC"},
        "white": {"$value": "#FFFFFF"},
        "illustration": {
            "shadow": {
                "$value": "#F7A10B",
                "$extensions": {"cockpit": {"scope": ["06-graphic-design/illustrations"]}},
            },
        },
        "derived": {
            "primary-deep": {
                "$value": "#1A3690",
                "$extensions": {"cockpit": {"scope": ["06-graphic-design/presentations"]}},
            },
        },
    },
    "font": {
        "$type": "fontFamily",
        "display": {"$value": ["Inter", "system-ui", "sans-serif"]},
        "mono": {"$value": ["ui-monospace", "Menlo", "monospace"]},
    },
}


def config_fictive() -> str:
    """La configuration livrée, avec des valeurs de marque fictives.

    Chaque remplacement vérifie que son ancre existe : si la configuration
    livrée change de forme, le test le dit au lieu de tester autre chose.
    """
    texte = CONFIG_LIVREE.read_text(encoding="utf-8")
    remplacements = [
        ("[forbidden-words.charter]\nwords = []\nphrases = []",
         '[forbidden-words.charter]\nwords = ["synergie", "disruption"]\n'
         'phrases = ["offre premium", "leader incontesté"]'),
        ("[forbidden-words.tolerated]\nwords = []\nphrases = []",
         '[forbidden-words.tolerated]\nwords = ["premium"]\nphrases = []'),
        ("[hashtags]\n# Désactivée par défaut", "[hashtags]\n# Activée par le test"),
        ("enabled = false\nlevel = \"error\"\nextensions = [\".md\"]",
         "enabled = true\nlevel = \"error\"\nextensions = [\".md\"]"),
        ("mail_warn = []\nmail_warn_dirs = []",
         'mail_warn = ["ancienne-police"]\nmail_warn_dirs = ["04-email"]'),
    ]
    for ancre, remplacement in remplacements:
        assert ancre in texte, f"ancre introuvable dans lint-brand.toml : {ancre!r}"
        texte = texte.replace(ancre, remplacement, 1)
    return texte


@pytest.fixture()
def racine(tmp_path: Path) -> Path:
    """Racine jetable : une palette fictive et la configuration fictive."""
    root = tmp_path / "repo"
    dst = root / TOKENS
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(TOKENS_FICTIFS, indent=2), encoding="utf-8")
    (root / "lint-brand.toml").write_text(config_fictive(), encoding="utf-8")
    return root


def ecrire(racine: Path, rel: str, contenu: str) -> Path:
    chemin = racine / rel
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")
    return chemin


def lancer(racine: Path, *args: str, config: Path | None = None) -> subprocess.CompletedProcess:
    config = config or (racine / "lint-brand.toml")
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(racine), "--config", str(config), *args],
        capture_output=True, text=True,
    )


def constats(racine: Path, *args: str, config: Path | None = None) -> list[dict]:
    """Lance le linter en JSON et rend la liste brute des constats."""
    result = lancer(racine, "--format", "json", *args, config=config)
    assert result.returncode in (0, 1), result.stderr
    return json.loads(result.stdout)["findings"]


def par_regle(racine: Path, regle: str, *args: str, config: Path | None = None) -> list[dict]:
    return [c for c in constats(racine, *args, config=config) if c["rule"] == regle]


# ---------------------------------------------------------------------------
# Configuration livrée
# ---------------------------------------------------------------------------

def test_config_livree_se_charge_et_ne_porte_aucune_marque(tmp_path):
    """La configuration du template est valide et laisse vides les listes de marque."""
    root = tmp_path / "repo"
    (root / "01-brand").mkdir(parents=True)
    (root / TOKENS).write_text(json.dumps(TOKENS_FICTIFS), encoding="utf-8")
    config = lint_brand.charger_config(CONFIG_LIVREE, root)
    assert config["forbidden-words"]["charter"] == {"words": [], "phrases": []}
    assert config["forbidden-words"]["tolerated"] == {"words": [], "phrases": []}
    assert lint_brand.regle_active(config, "hashtags") is False
    assert lint_brand.regle_active(config, "dashes") is True


def test_config_livree_hashtags_desactives_par_defaut(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Un post utile #Exemple\n")
    assert par_regle(racine, "hashtags", config=CONFIG_LIVREE) == []


def test_only_relance_une_regle_desactivee(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Un post utile #Exemple\n")
    trouves = par_regle(racine, "hashtags", "--only", "hashtags", config=CONFIG_LIVREE)
    assert [c["match"] for c in trouves] == ["#Exemple"]


# ---------------------------------------------------------------------------
# 1. forbidden-words
# ---------------------------------------------------------------------------

def test_forbidden_words_charte_est_une_erreur(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Notre synergie annonce une disruption.\n")
    trouves = par_regle(racine, "forbidden-words")
    assert {c["level"] for c in trouves} == {"error"}
    assert {c["match"].lower() for c in trouves} == {"synergie", "disruption"}


def test_forbidden_words_texte_propre_ne_remonte_rien(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Nos équipes livrent des projets solides.\n")
    assert par_regle(racine, "forbidden-words") == []


def test_forbidden_words_ai_erreur_en_contenu_avertissement_ailleurs(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "We delve into the topic.\n")
    ecrire(racine, "02-strategy/note.md", "We delve into the topic.\n")
    niveaux = {c["file"]: c["level"] for c in par_regle(racine, "forbidden-words")}
    assert niveaux["03-social-media/linkedin/post.md"] == "error"
    assert niveaux["02-strategy/note.md"] == "warning"


def test_forbidden_words_doctrine_avertit_la_ou_le_contenu_bloque(racine):
    """La doctrine cite les mots qu'elle interdit : avertissement, pas erreur."""
    ecrire(racine, "01-brand/voice.md", "Ne jamais écrire « synergie ».\n")
    ecrire(racine, ".claude/skills/social-content/SKILL.md", "Mot banni : synergie.\n")
    ecrire(racine, "03-social-media/linkedin/post.md", "Notre synergie change tout.\n")
    niveaux = {c["file"]: c["level"] for c in par_regle(racine, "forbidden-words")}
    assert niveaux["01-brand/voice.md"] == "warning"
    assert niveaux[".claude/skills/social-content/SKILL.md"] == "warning"
    assert niveaux["03-social-media/linkedin/post.md"] == "error"


def test_forbidden_words_doctrine_avertit_aussi_sur_la_liste_ia(racine):
    ecrire(racine, "01-brand/style-guide.md", "Le mot « seamless » est proscrit.\n")
    trouves = par_regle(racine, "forbidden-words")
    assert [c["level"] for c in trouves] == ["warning"]


def test_forbidden_words_flexions_des_verbes(racine):
    ecrire(racine, "05-web-content/page.md", "This leverages the platform and we leveraged it.\n")
    trouves = par_regle(racine, "forbidden-words")
    assert {c["match"].lower() for c in trouves} == {"leverages", "leveraged"}


def test_forbidden_words_liste_francaise(racine):
    ecrire(racine, "04-email/promo.md", "Un rendez-vous incontournable, à l’ère de l'IA.\n")
    trouves = par_regle(racine, "forbidden-words")
    assert {c["match"].lower() for c in trouves} == {"incontournable", "à l'ère de"}
    assert {c["level"] for c in trouves} == {"error"}


def test_forbidden_words_mot_entier_seulement(racine):
    ecrire(racine, "05-web-content/page.md", "Realmente, le realmgate reste aligné.\n")
    assert par_regle(racine, "forbidden-words") == []


def test_forbidden_words_doctrine_anti_ia_exclue(racine):
    ecrire(racine, "01-brand/anti-ai-writing-style.md", "delve, realm, harness, leverage\n")
    ecrire(racine, "_templates/brand/anti-ai-writing-style.md", "delve, realm, harness, leverage\n")
    assert par_regle(racine, "forbidden-words") == []


def test_forbidden_words_ne_lit_ni_le_css_ni_le_balisage(racine):
    """« align » et « transparent » sont des mots-clés de mise en page, pas du vocabulaire."""
    contenu = (
        "<style>.a{vertical-align:top;background:transparent}</style>\n"
        "<td align=\"center\" class=\"dynamic\">Un texte propre.</td>\n"
    )
    ecrire(racine, "05-web-content/page.html", contenu)
    ecrire(racine, "05-web-content/feuille.css", ".a{vertical-align:top;background:transparent}\n")
    assert par_regle(racine, "forbidden-words") == []


def test_forbidden_words_un_chevron_orphelin_n_avale_pas_la_prose(racine):
    """Une balise ne franchit pas une ligne vide : sinon un « < » éteindrait la règle."""
    contenu = "<img src=x\n\nA seamless experience.\n\n>\n"
    ecrire(racine, "05-web-content/page.html", contenu)
    trouves = par_regle(racine, "forbidden-words")
    assert [(c["match"].lower(), c["line"]) for c in trouves] == [("seamless", 3)]


def test_forbidden_words_une_balise_ne_contient_jamais_de_chevron_ouvrant(racine):
    """Sans ligne vide pour l'arrêter, c'est le « < » suivant qui borne la balise."""
    contenu = "<img src=x\nA seamless experience.\n<p>un paragraphe</p>\n"
    ecrire(racine, "05-web-content/page.html", contenu)
    trouves = par_regle(racine, "forbidden-words")
    assert [(c["match"].lower(), c["line"]) for c in trouves] == [("seamless", 2)]


def test_forbidden_words_ne_lit_pas_les_scripts(racine):
    contenu = "<script>const seamless = optimize(delve);</script>\n<p>Un texte propre.</p>\n"
    ecrire(racine, "05-web-content/page.html", contenu)
    assert par_regle(racine, "forbidden-words") == []


def test_forbidden_words_lit_la_prose_des_attributs_visibles(racine):
    """Un texte alternatif est lu par un humain : il reste contrôlé."""
    ecrire(racine, "05-web-content/page.html",
           "<img src=\"x.png\" alt=\"A seamless experience\">\n")
    trouves = par_regle(racine, "forbidden-words")
    assert [c["match"].lower() for c in trouves] == ["seamless"]


def test_forbidden_words_tolere_est_un_avertissement(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Une gamme premium reste une option.\n")
    trouves = par_regle(racine, "forbidden-words")
    assert [c["level"] for c in trouves] == ["warning"]


def test_forbidden_words_pas_de_doublon_erreur_avertissement(racine):
    """« offre premium » est une erreur : le mot « premium », toléré seul, ne la double pas."""
    ecrire(racine, "03-social-media/linkedin/post.md", "Découvrez notre offre premium dès lundi.\n")
    trouves = par_regle(racine, "forbidden-words")
    assert len(trouves) == 1
    assert trouves[0]["level"] == "error"


# ---------------------------------------------------------------------------
# 2. dashes
# ---------------------------------------------------------------------------

def test_dashes_signale_le_cadratin(racine):
    ecrire(racine, "02-strategy/note.md", "Un texte — une suite.\nUne plage 2024–2025.\n")
    trouves = par_regle(racine, "dashes")
    assert [c["line"] for c in trouves] == [1]
    assert {c["level"] for c in trouves} == {"error"}


def test_dashes_le_demi_cadratin_se_bannit_par_configuration(racine):
    config = racine / "lint-brand.toml"
    texte = config.read_text(encoding="utf-8")
    config.write_text(texte.replace('characters = ["—"]', 'characters = ["—", "–"]', 1),
                      encoding="utf-8")
    ecrire(racine, "02-strategy/note.md", "Un texte — une suite.\nUne plage 2024–2025.\n")
    assert [c["line"] for c in par_regle(racine, "dashes")] == [1, 2]


def test_dashes_compte_chaque_occurrence(racine):
    """Trois tirets sur une ligne font trois constats : le compte guide la correction."""
    ecrire(racine, "02-strategy/note.md", "Un — deux — trois — quatre.\n")
    trouves = [c for c in par_regle(racine, "dashes") if c["level"] == "error"]
    assert len(trouves) == 3
    assert {c["line"] for c in trouves} == {1}
    assert [c["column"] for c in trouves] == [4, 11, 19]


def test_dashes_situe_la_colonne_dans_la_sortie_texte(racine):
    ecrire(racine, "02-strategy/note.md", "Un — deux.\n")
    assert "02-strategy/note.md:1:4: [dashes] erreur:" in lancer(racine).stdout


def test_fence_non_refermee_signalee_et_plus_rien_n_est_ignore(racine):
    """La clôture ouverte est un diagnostic de fichier, comme un fichier illisible."""
    contenu = "```\nun bloc jamais refermé\n```\n```\nUn texte — fautif.\n"
    ecrire(racine, "02-strategy/note.md", contenu)
    fences = par_regle(racine, "fence")
    assert len(fences) == 1
    assert fences[0]["level"] == "warning"
    assert fences[0]["line"] == 4
    assert [c["line"] for c in par_regle(racine, "dashes")] == [5]


def test_fence_refermee_ne_signale_rien(racine):
    ecrire(racine, "02-strategy/note.md", "```\nun bloc refermé\n```\n")
    assert par_regle(racine, "fence") == []


def test_dashes_ignore_fences_frontmatter_tableaux_et_traits_simples(racine):
    contenu = (
        "---\n"
        "titre: Un — titre de frontmatter\n"
        "---\n"
        "\n"
        "| Colonne | Valeur |\n"
        "|---------|--------|\n"
        "| a       | b      |\n"
        "\n"
        "Un trait - simple reste permis.\n"
        "\n"
        "```\n"
        "echo \"un — tiret dans du code\"\n"
        "```\n"
    )
    ecrire(racine, "02-strategy/note.md", contenu)
    assert par_regle(racine, "dashes") == []


# ---------------------------------------------------------------------------
# 3. title-period
# ---------------------------------------------------------------------------

def test_title_period_markdown_et_html(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n\nUne phrase normale.\n")
    ecrire(racine, "05-web-content/page.html", "<h2>Un titre fautif.</h2>\n")
    trouves = par_regle(racine, "title-period")
    assert sorted(c["file"] for c in trouves) == [
        "02-strategy/note.md", "05-web-content/page.html",
    ]
    assert {c["level"] for c in trouves} == {"error"}


def test_title_period_bloque_avec_la_config_livree(racine):
    """La règle par défaut de voice.md : aucun point final sur un titre."""
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n")
    trouves = par_regle(racine, "title-period", config=CONFIG_LIVREE)
    assert [c["level"] for c in trouves] == ["error"]


def test_title_period_html_dans_une_fence_ignore(racine):
    ecrire(racine, "02-strategy/note.md", "Un exemple :\n\n```html\n<h2>Un titre fautif.</h2>\n```\n")
    assert par_regle(racine, "title-period") == []


def test_title_period_titres_corrects(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre correct\n\n## Une question ?\n\nUne phrase normale.\n")
    ecrire(racine, "05-web-content/page.html", "<h2>Un titre correct</h2>\n<p>Une phrase.</p>\n")
    assert par_regle(racine, "title-period") == []


# ---------------------------------------------------------------------------
# 4. hashtags
# ---------------------------------------------------------------------------

def test_hashtags_signale_un_hashtag_social(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Un post utile #Exemple\n")
    trouves = par_regle(racine, "hashtags")
    assert [c["match"] for c in trouves] == ["#Exemple"]
    assert trouves[0]["level"] == "error"


def test_hashtags_hors_social_titres_et_hex_ignores(racine):
    ecrire(racine, "04-email/newsletter.md", "Une newsletter #Exemple\n")
    ecrire(racine, "03-social-media/linkedin/autre.md", "# Un titre\n\nCouleur #1E40AF et #F8FAFC.\n")
    assert par_regle(racine, "hashtags") == []


# ---------------------------------------------------------------------------
# 5. placeholders
# ---------------------------------------------------------------------------

def test_placeholders_signale_un_residu(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Bienvenue chez {{COMPANY_NAME}}.\n")
    trouves = par_regle(racine, "placeholders")
    assert [c["level"] for c in trouves] == ["error"]
    assert "COMPANY_NAME" in trouves[0]["message"]


def test_placeholders_dossiers_de_gabarits_exclus(racine):
    ecrire(racine, "_templates/post.md", "Bienvenue chez {{COMPANY_NAME}}.\n")
    ecrire(racine, "_examples/post.md", "Bienvenue chez {{COMPANY_NAME}}.\n")
    ecrire(racine, "docs/post.md", "Bienvenue chez {{COMPANY_NAME}}.\n")
    ecrire(racine, ".claude/skills/x/SKILL.md", "Bienvenue chez {{COMPANY_NAME}}.\n")
    ecrire(racine, "05-web-content/templates/page.html", "<p>{{COMPANY_NAME}}</p>\n")
    ecrire(racine, "02-strategy/briefs/brief-campagne.md", "Brief {{SLUG_CAMPAGNE}}\n")
    assert par_regle(racine, "placeholders") == []


def test_placeholders_marqueurs_toleres(racine):
    """Les marqueurs remplis à la production (liste de lint-placeholders.py) passent."""
    ecrire(racine, "02-strategy/calendar/calendar.md", "Semaine du {{DATE_LUNDI_ISO}}\n")
    assert par_regle(racine, "placeholders") == []


# ---------------------------------------------------------------------------
# 6. off-palette
# ---------------------------------------------------------------------------

def test_off_palette_plus_de_trois_hex_distincts_est_une_erreur(racine):
    ecrire(racine, "06-graphic-design/a.css", ".a{color:#FF0000;background:#00FF00;border-color:#0000FF;outline-color:#FF00FF}\n")
    trouves = par_regle(racine, "off-palette")
    assert len(trouves) == 4
    assert {c["level"] for c in trouves} == {"error"}


def test_off_palette_trois_hex_ou_moins_est_un_avertissement(racine):
    ecrire(racine, "06-graphic-design/a.css", ".a{color:#FF0000;background:#00FF00}\n")
    trouves = par_regle(racine, "off-palette")
    assert len(trouves) == 2
    assert {c["level"] for c in trouves} == {"warning"}


def test_off_palette_palette_noir_blanc_gris_et_tolerance(racine):
    contenu = (
        ".a{color:#1E40AF;background:#F8FAFC;border-color:#000000}\n"
        ".b{color:#FFFFFF;background:#888888;outline-color:#1E40B0}\n"
        ".c{color:#fff}\n"
    )
    ecrire(racine, "06-graphic-design/a.css", contenu)
    assert par_regle(racine, "off-palette") == []


def test_off_palette_respecte_le_scope_des_tokens(racine):
    """La nuance dérivée est admise dans les decks, nulle part ailleurs."""
    ecrire(racine, "06-graphic-design/presentations/deck.html", "<style>.a{color:#1A3690}</style>\n")
    ecrire(racine, "05-web-content/landing/page.html", "<style>.a{color:#1A3690}</style>\n")
    fichiers = [c["file"] for c in par_regle(racine, "off-palette")]
    assert fichiers == ["05-web-content/landing/page.html"]


def test_off_palette_la_tolerance_ne_court_circuite_pas_la_portee(racine):
    """L'ombre d'illustration est à ΔE 1.4 de l'accent : la tolérance ne l'absout pas.

    Chercher le token le plus proche parmi les seuls tokens admis ferait passer
    cette couleur pour l'accent partout. Le plus proche se cherche dans toute la
    palette, et c'est sa portée à lui qui tranche.
    """
    ecrire(racine, "05-web-content/landing/page.html", "<style>.a{color:#F7A10B}</style>\n")
    ecrire(racine, "06-graphic-design/illustrations/scene.html", "<style>.a{color:#F7A10B}</style>\n")
    trouves = par_regle(racine, "off-palette")
    assert [c["file"] for c in trouves] == ["05-web-content/landing/page.html"]
    assert "illustration.shadow" in trouves[0]["message"]


def test_off_palette_l_accent_exact_reste_admis_partout(racine):
    ecrire(racine, "05-web-content/landing/page.html", "<style>.a{color:#F59E0B}</style>\n")
    assert par_regle(racine, "off-palette") == []


def test_off_palette_hex_court_developpe(racine):
    ecrire(racine, "06-graphic-design/a.css", ".a{color:#f00}\n")
    trouves = par_regle(racine, "off-palette")
    assert len(trouves) == 1
    assert "#FF0000" in trouves[0]["message"]


def test_off_palette_ignore_les_data_uri(racine):
    """Les hex enfermés dans une data: URI décrivent une image, pas la charte."""
    ecrire(racine, "06-graphic-design/a.html",
           "<img src=\"data:image/svg+xml,<svg fill='#FF0000' stroke='#00FF00' "
           "opacity='#0000FF' color='#FF00FF'/>\">\n")
    assert par_regle(racine, "off-palette") == []


def test_off_palette_dossiers_exclus(racine):
    fautif = ".a{color:#FF0000;background:#00FF00;border-color:#0000FF;outline-color:#FF00FF}\n"
    ecrire(racine, "05-web-content/templates/a.css", fautif)
    ecrire(racine, "_examples/a.css", fautif)
    assert par_regle(racine, "off-palette") == []


def test_hex_vers_lab_valeurs_de_reference():
    """Valeurs canoniques sRGB vers Lab D65, observateur 2 degrés."""
    assert lint_brand.hex_vers_lab("#FFFFFF")[0] == pytest.approx(100.0, abs=0.05)
    assert lint_brand.hex_vers_lab("#000000")[0] == pytest.approx(0.0, abs=0.05)
    rouge = lint_brand.hex_vers_lab("#FF0000")
    assert rouge[0] == pytest.approx(53.24, abs=0.05)
    assert rouge[1] == pytest.approx(80.09, abs=0.05)
    assert rouge[2] == pytest.approx(67.20, abs=0.05)


def test_delta_e76_est_nul_pour_deux_couleurs_identiques():
    assert lint_brand.delta_e76("#1E40AF", "#1E40AF") == pytest.approx(0.0, abs=1e-9)


def test_delta_e76_accent_contre_ombre_d_illustration():
    """Les deux jaunes de la palette fictive se tiennent à 1.4 : sous la tolérance de 2."""
    assert lint_brand.delta_e76("#F59E0B", "#F7A10B") == pytest.approx(1.40, abs=0.05)


def test_delta_e76_separe_deux_couleurs_franchement_differentes():
    assert lint_brand.delta_e76("#FF0000", "#00FF00") > 50


# ---------------------------------------------------------------------------
# Palette indisponible (avant /brand-discover)
# ---------------------------------------------------------------------------

def test_sans_tokens_les_regles_graphiques_se_taisent_et_le_disent(racine):
    (racine / TOKENS).unlink()
    ecrire(racine, "06-graphic-design/a.css",
           ".a{color:#FF0000;background:#00FF00;border-color:#0000FF;outline-color:#FF00FF;"
           "font-family:'Comic Sans MS'}\n")
    ecrire(racine, "02-strategy/note.md", "Un texte — fautif.\n")
    tous = constats(racine)
    regles = {c["rule"] for c in tous}
    assert "off-palette" not in regles and "font-family" not in regles
    assert "dashes" in regles    # les règles de texte, elles, s'appliquent
    palette = [c for c in tous if c["rule"] == "palette"]
    assert len(palette) == 1
    assert palette[0]["level"] == "warning"
    assert "introuvable" in palette[0]["message"]


def test_tokens_encore_tokenises_valent_palette_indisponible(racine):
    tokens = json.loads((racine / TOKENS).read_text(encoding="utf-8"))
    tokens["color"]["primary"]["$value"] = "{{BRAND_COLOR_PRIMARY}}"
    (racine / TOKENS).write_text(json.dumps(tokens), encoding="utf-8")
    ecrire(racine, "06-graphic-design/a.css", ".a{color:#FF0000}\n")
    palette = par_regle(racine, "palette")
    assert len(palette) == 1
    assert "placeholders" in palette[0]["message"]


def test_sans_tokens_aucun_diagnostic_sur_un_texte_seul(racine):
    """Un brouillon markdown ne lit pas la palette : rien à signaler."""
    (racine / TOKENS).unlink()
    ecrire(racine, "03-social-media/linkedin/post.md", "Un texte propre.\n")
    assert constats(racine) == []


def test_tokens_illisible_sort_en_deux(racine):
    (racine / TOKENS).write_text("{ pas du json", encoding="utf-8")
    ecrire(racine, "02-strategy/note.md", "Un texte propre.\n")
    result = lancer(racine)
    assert result.returncode == 2
    assert "JSON" in result.stderr


# ---------------------------------------------------------------------------
# 7. font-family
# ---------------------------------------------------------------------------

def test_font_family_premiere_famille_hors_marque(racine):
    ecrire(racine, "06-graphic-design/a.css", "body{font-family: 'Comic Sans MS', sans-serif}\n")
    trouves = par_regle(racine, "font-family")
    assert [c["level"] for c in trouves] == ["error"]
    assert "Comic Sans MS" in trouves[0]["message"]
    assert "inter" in trouves[0]["message"]    # la police de marque vient de tokens.json


def test_font_family_familles_admises(racine):
    contenu = (
        "body{font-family:'Inter', system-ui, sans-serif}\n"
        "code{font-family: ui-monospace, monospace}\n"
        "p{font-family: var(--font-display)}\n"
        "td{font-family: inherit !important}\n"
    )
    ecrire(racine, "06-graphic-design/a.css", contenu)
    assert par_regle(racine, "font-family") == []


def test_font_family_tolere_arial_en_avertissement_dans_les_mails(racine):
    ecrire(racine, "04-email/newsletter.html", "<style>td{font-family: Arial, sans-serif}</style>\n")
    ecrire(racine, "06-graphic-design/mail-signatures/sig.html",
           "<style>td{font-family: Helvetica, sans-serif}</style>\n")
    trouves = par_regle(racine, "font-family")
    assert len(trouves) == 2
    assert {c["level"] for c in trouves} == {"warning"}


def test_font_family_famille_inconnue_reste_une_erreur_en_messagerie(racine):
    """La tolérance des mails vaut pour Arial et consorts, pas pour n'importe quoi."""
    ecrire(racine, "04-email/newsletter.html", "<style>td{font-family: 'Comic Sans MS', sans-serif}</style>\n")
    trouves = par_regle(racine, "font-family")
    assert [c["level"] for c in trouves] == ["error"]


def test_font_family_police_en_sursis_dans_son_dossier_seulement(racine):
    """Le sursis vaut pour le dossier déclaré, pas pour le reste du dépôt."""
    ecrire(racine, "04-email/newsletter.html", "<style>td{font-family: ancienne-police, sans-serif}</style>\n")
    ecrire(racine, "06-graphic-design/carte.html", "<style>td{font-family: ancienne-police, sans-serif}</style>\n")
    niveaux = {c["file"]: c["level"] for c in par_regle(racine, "font-family")}
    assert niveaux["04-email/newsletter.html"] == "warning"
    assert niveaux["06-graphic-design/carte.html"] == "error"


# ---------------------------------------------------------------------------
# 8. negative-parallelism
# ---------------------------------------------------------------------------

def test_negative_parallelism_signale_un_patron(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "It's not about the tool. It's about the team.\n")
    trouves = par_regle(racine, "negative-parallelism")
    assert [c["level"] for c in trouves] == ["warning"]
    assert trouves[0]["line"] == 1


def test_negative_parallelism_patron_francais(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "Ce n'est pas un outil, c'est une méthode.\n")
    assert len(par_regle(racine, "negative-parallelism")) == 1


def test_negative_parallelism_phrase_affirmative_ignoree(racine):
    ecrire(racine, "03-social-media/linkedin/post.md", "It's about the team. The tool follows.\n")
    assert par_regle(racine, "negative-parallelism") == []


# ---------------------------------------------------------------------------
# Parcours, options et sortie
# ---------------------------------------------------------------------------

def test_fichier_illisible_signale_en_avertissement(racine):
    """Un fichier qu'on ne sait pas lire est un trou dans le contrôle : le dire."""
    chemin = ecrire(racine, "02-strategy/note.md", "texte\n")
    chemin.write_bytes(b"\xff\xfe\x00binaire mal encod\xe9\n")
    trouves = [c for c in constats(racine) if c["rule"] == "io"]
    assert len(trouves) == 1
    assert trouves[0]["level"] == "warning"
    assert trouves[0]["file"] == "02-strategy/note.md"


def test_data_uri_non_refermee_n_eteint_pas_la_regle(racine):
    """Une quote manquante ne doit pas mettre la fin du fichier à l'abri."""
    contenu = (
        "<img src=\"data:image/png;base64,AAAA>\n"
        "<style>.a{color:#FF0000;background:#00FF00;border-color:#0000FF;outline-color:#FF00FF}</style>\n"
        "<a href=\"ailleurs\">la quote fermante est plus bas, elle n'appartient plus à l'URI</a>\n"
    )
    ecrire(racine, "06-graphic-design/a.html", contenu)
    trouves = par_regle(racine, "off-palette")
    assert len(trouves) == 4
    assert {c["line"] for c in trouves} == {2}


def test_extensions_hors_liste_ignorees(racine):
    ecrire(racine, "scripts/outil.py", "# un — tiret dans du Python\n")
    assert par_regle(racine, "dashes") == []


def test_dossiers_exclus_du_parcours(racine):
    ecrire(racine, "node_modules/paquet/readme.md", "Un texte — exclu.\n")
    ecrire(racine, ".setup-archive/vieux.md", "Un texte — exclu.\n")
    assert constats(racine) == []


def test_only_restreint_aux_regles_demandees(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n\nUn texte — fautif.\n")
    assert {c["rule"] for c in constats(racine, "--only", "dashes")} == {"dashes"}


def test_skip_retire_la_regle(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n\nUn texte — fautif.\n")
    assert {c["rule"] for c in constats(racine, "--skip", "dashes")} == {"title-period"}


def test_only_refuse_une_regle_inconnue(racine):
    result = lancer(racine, "--only", "regle-imaginaire")
    assert result.returncode == 2
    assert "regle-imaginaire" in result.stderr


def test_chemin_inexistant_sort_en_deux(racine):
    result = lancer(racine, str(racine / "nulle-part.md"))
    assert result.returncode == 2
    assert "chemin inexistant" in result.stderr


def test_chemin_trop_long_sort_en_deux_sans_trace(racine):
    """5000 caractères : le système de fichiers lève, le linter doit le dire."""
    result = lancer(racine, "a" * 5000)
    assert result.returncode == 2
    assert "chemin illisible" in result.stderr
    assert "Traceback" not in result.stderr


def test_code_de_sortie_zero_sans_erreur(racine):
    ecrire(racine, "02-strategy/note.md", "Un texte propre.\n")
    assert lancer(racine).returncode == 0


def test_code_de_sortie_un_avec_erreur(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n")
    assert lancer(racine).returncode == 1


def test_warnings_as_errors(racine):
    ecrire(racine, "02-strategy/note.md", "We delve into the topic.\n")
    assert lancer(racine).returncode == 0
    assert lancer(racine, "--warnings-as-errors").returncode == 1


def test_format_texte_une_ligne_par_constat(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n")
    sortie = lancer(racine).stdout
    assert "02-strategy/note.md:1: [title-period] erreur:" in sortie
    assert "1 erreur" in sortie


def test_format_json_porte_le_resume(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n")
    charge = json.loads(lancer(racine, "--format", "json").stdout)
    assert charge["summary"]["errors"] == 1
    assert charge["summary"]["warnings"] == 0
    assert charge["summary"]["by_rule"]["title-period"] == 1


def test_chemin_explicite_restreint_le_parcours(racine):
    ecrire(racine, "02-strategy/note.md", "# Un titre fautif.\n")
    ecrire(racine, "03-social-media/post.md", "# Un autre titre fautif.\n")
    trouves = constats(racine, str(racine / "03-social-media"))
    assert [c["file"] for c in trouves] == ["03-social-media/post.md"]


def test_help_disponible(racine):
    result = lancer(racine, "--help")
    assert result.returncode == 0
    assert "--warnings-as-errors" in result.stdout

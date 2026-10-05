"""Tests de 06-graphic-design/presentations/scripts/qa.py sur un deck minimal.

Ces tests pilotent un vrai Chromium : ils sont ignorés proprement si Playwright
ou le navigateur ne sont pas installés sur la machine. La logique de calcul, elle,
est couverte sans navigateur par `test_qa_common.py`.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
QA = REPO / "06-graphic-design" / "presentations" / "scripts" / "qa.py"


def _chromium_disponible() -> bool:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as playwright:
            playwright.chromium.launch().close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not _chromium_disponible(), reason="Playwright ou Chromium indisponible sur cette machine"
)


# Le gabarit reproduit le mécanisme du moteur de slides : un cadre natif 1920x1080
# amené à la fenêtre par un `transform: scale()`. C'est ce qui permet de tester
# que les géométries sont bien ramenées au cadre natif et que les tailles de
# police, elles, ne le sont pas.
SQUELETTE = """<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
  body {{ margin: 0; font-family: Inter, sans-serif; overflow: hidden; }}
  #stage-frame {{ position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px;
                  background: #F8FAFC; }}
  .plate {{ display: none; position: absolute; inset: 0; background: #F8FAFC; }}
  .plate.active {{ display: block; }}
  .chrome-row.bottom {{ position: absolute; left: 40px; right: 40px; bottom: 0; height: 40px; }}
  .corps {{ position: absolute; left: 80px; top: 200px; font-size: 28px; color: #0F172A; }}
  {styles}
</style></head><body><div id="stage-frame">{plates}</div>
<script>
  const cadre = document.getElementById('stage-frame');
  const ajuster = () => {{
    const f = Math.min(innerWidth / 1920, innerHeight / 1080);
    cadre.style.transform = 'translate(-50%, -50%) scale(' + f + ')';
  }};
  addEventListener('resize', ajuster); ajuster();
</script></body></html>"""

PLATE = """<section class="plate {actif}">
  <div class="chrome"><div class="chrome-row bottom">
    <span class="tag-folio"><strong>{folio:02d}</strong> / {total}</span>
  </div></div>
  <p class="corps">Un texte de contenu lisible</p>
  {extra}
</section>"""


# Le deck minimal n'embarque pas le moteur complet : la parité est testée à part.
# La police attendue est passée explicitement, pour ne dépendre d'aucun tokens.json.
DEFAUTS = ("--no-engine-check", "--police", "Inter")


def ecrire_deck(dossier: Path, nom: str, extras: list[str], styles: str = "") -> Path:
    plates = "".join(
        PLATE.format(actif="active" if i == 0 else "", folio=i + 1, total=len(extras), extra=extra)
        for i, extra in enumerate(extras)
    )
    chemin = dossier / nom
    chemin.write_text(SQUELETTE.format(plates=plates, styles=styles), encoding="utf-8")
    return chemin


def lancer(deck: Path, *options: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(QA), str(deck), "--attente", "200", *DEFAUTS, *options],
        capture_output=True, text=True, cwd=str(REPO), timeout=180,
    )


def constats(deck: Path, *options: str) -> tuple[subprocess.CompletedProcess, list[dict]]:
    resultat = lancer(deck, "--format", "json", *options)
    rapport = json.loads(resultat.stdout)
    return resultat, [c for slide in rapport["slides"] for c in slide["constats"]]


def test_deck_propre(tmp_path):
    deck = ecrire_deck(tmp_path, "propre.html", ["", ""])
    resultat = lancer(deck)
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "All slides clean" in resultat.stdout


def test_plancher_typographique(tmp_path):
    deck = ecrire_deck(
        tmp_path, "petit.html",
        ['<p class="menu">Une note trop petite</p>'],
        styles=".menu { position: absolute; left: 80px; top: 400px; font-size: 12px; color: #0F172A; }",
    )
    resultat, trouves = constats(deck)
    assert resultat.returncode == 1
    assert any(c["type"] == "plancher-typo" and "12px" in c["message"] for c in trouves)


def test_plancher_relevé_par_option(tmp_path):
    deck = ecrire_deck(
        tmp_path, "corps20.html",
        ['<p class="note">Une note de vingt pixels</p>'],
        styles=".note { position: absolute; left: 80px; top: 400px; font-size: 20px; color: #0F172A; }",
    )
    _, defaut = constats(deck)
    assert not [c for c in defaut if c["type"] == "plancher-typo"]

    _, releve = constats(deck, "--min-font", "24")
    assert any(c["type"] == "plancher-typo" for c in releve)


def test_contraste_insuffisant(tmp_path):
    deck = ecrire_deck(
        tmp_path, "contraste.html",
        ['<p class="pale">Un texte trop pâle sur crème</p>'],
        styles=".pale { position: absolute; left: 80px; top: 400px; font-size: 28px; color: #F59E0B; }",
    )
    resultat, trouves = constats(deck)
    assert resultat.returncode == 1
    assert any(c["type"] == "contraste" and "sous 3.0:1" in c["message"] for c in trouves)


def test_fond_non_uni_en_avertissement(tmp_path):
    deck = ecrire_deck(
        tmp_path, "gradient.html",
        ['<div class="bandeau"><p class="dessus">Sur un dégradé</p></div>'],
        styles=(
            ".bandeau { position: absolute; left: 80px; top: 400px; width: 900px; height: 120px;"
            " background: linear-gradient(90deg, #1E40AF 0%, #F59E0B 100%); }"
            ".dessus { font-size: 28px; color: #0F172A; margin: 0; }"
        ),
    )
    resultat, trouves = constats(deck)
    assert any(
        c["type"] == "contraste" and c["niveau"] == "avertissement" and "fond non uni" in c["message"]
        for c in trouves
    )
    assert resultat.returncode == 0


def test_texte_en_gradient_liste_a_part(tmp_path):
    deck = ecrire_deck(
        tmp_path, "gradient-text.html",
        ['<h2 class="gradient-text">Titre en dégradé</h2>'],
        styles=(
            ".gradient-text { position: absolute; left: 80px; top: 400px; font-size: 60px;"
            " background: linear-gradient(90deg, #1E40AF, #F59E0B);"
            " -webkit-background-clip: text; background-clip: text; color: transparent; }"
        ),
    )
    resultat = lancer(deck, "--format", "json")
    rapport = json.loads(resultat.stdout)
    assert any("gradient-text" in entree for entree in rapport["gradient_text"])
    assert not [c for slide in rapport["slides"] for c in slide["constats"] if c["type"] == "contraste"]


def test_police_hors_charte(tmp_path):
    deck = ecrire_deck(
        tmp_path, "police.html",
        ['<p class="etranger">Un texte en Helvetica</p>'],
        styles=(
            ".etranger { position: absolute; left: 80px; top: 400px; font-size: 28px;"
            ' color: #0F172A; font-family: "Helvetica Neue", sans-serif; }'
        ),
    )
    resultat, trouves = constats(deck)
    assert resultat.returncode == 1
    assert any(c["type"] == "police" and "Helvetica Neue" in c["message"] for c in trouves)


def test_monospace_toleree_sur_du_code(tmp_path):
    deck = ecrire_deck(
        tmp_path, "code.html",
        ['<code class="extrait">python3 qa.py deck.html</code>'],
        styles=(
            ".extrait { position: absolute; left: 80px; top: 400px; font-size: 28px;"
            " color: #0F172A; font-family: ui-monospace, monospace; }"
        ),
    )
    _, trouves = constats(deck)
    assert not [c for c in trouves if c["type"] == "police"]


def test_monospace_hors_chrome_en_avertissement(tmp_path):
    deck = ecrire_deck(
        tmp_path, "mono.html",
        ['<p class="kicker">Un chapeau en monospace</p>'],
        styles=(
            ".kicker { position: absolute; left: 80px; top: 400px; font-size: 28px;"
            " color: #0F172A; font-family: 'JetBrains Mono', ui-monospace, monospace; }"
        ),
    )
    resultat, trouves = constats(deck)
    police = [c for c in trouves if c["type"] == "police"]
    assert police and all(c["niveau"] == "avertissement" for c in police)
    assert resultat.returncode == 0


def test_echelle_gap_chrome_a_petit_viewport(tmp_path):
    """Un élément à 20px natifs du chrome passe le seuil, même à 1024x600."""
    deck = ecrire_deck(
        tmp_path, "gap-natif.html",
        ['<div class="pied"></div>'],
        styles=".pied { position: absolute; left: 80px; top: 1000px; width: 400px; height: 20px; background: #1E40AF; }",
    )
    resultat, trouves = constats(deck, "--viewport", "1024x600")
    assert not [c for c in trouves if c["type"] == "chrome-gap"], resultat.stdout
    assert resultat.returncode == 0, resultat.stdout


def test_echelle_debordement_de_trois_pixels(tmp_path):
    """Un débordement de 3px natifs est signalé, même à 1024x600."""
    deck = ecrire_deck(
        tmp_path, "over-natif.html",
        ['<div class="fine"></div>'],
        styles=".fine { position: absolute; left: 1800px; top: 300px; width: 123px; height: 100px; background: #1E40AF; }",
    )
    resultat, trouves = constats(deck, "--viewport", "1024x600")
    debordements = [c for c in trouves if c["type"] == "overflow"]
    assert debordements, resultat.stdout
    assert "R=3" in debordements[0]["message"]


def test_echelle_ne_touche_pas_la_taille_de_police(tmp_path):
    """`fontSize` calculé n'est pas affecté par le transform : ne pas le diviser."""
    deck = ecrire_deck(
        tmp_path, "typo-natif.html",
        ['<p class="menu">Une note trop petite</p>'],
        styles=".menu { position: absolute; left: 80px; top: 400px; font-size: 12px; color: #0F172A; }",
    )
    # Viewport volontairement plus large que le cadre rendu : si le facteur
    # d'échelle contaminait la taille de police, 12px remonterait à 18px et le
    # plancher ne serait pas franchi.
    _, trouves = constats(deck, "--viewport", "1600x600")
    plancher = [c for c in trouves if c["type"] == "plancher-typo"]
    assert plancher and "corps 12px" in plancher[0]["message"]


def test_debordement_detecte(tmp_path):
    deck = ecrire_deck(
        tmp_path, "overflow.html",
        ['<div class="large"></div>'],
        styles=".large { position: absolute; left: 1800px; top: 300px; width: 400px; height: 200px; background: #1E40AF; }",
    )
    resultat, trouves = constats(deck)
    assert resultat.returncode == 1
    assert any(c["type"] == "overflow" and ".large" in c["message"] for c in trouves)


def test_debordement_volontaire_ignore(tmp_path):
    deck = ecrire_deck(
        tmp_path, "bleed.html",
        ['<div class="large" data-bleed></div>'],
        styles=".large { position: absolute; left: 1800px; top: 300px; width: 400px; height: 200px; background: #1E40AF; }",
    )
    _, trouves = constats(deck)
    assert not [c for c in trouves if c["type"] == "overflow"]


def test_zone_de_securite_du_chrome(tmp_path):
    deck = ecrire_deck(
        tmp_path, "chrome.html",
        ['<div class="pied"></div>'],
        styles=".pied { position: absolute; left: 80px; top: 1030px; width: 400px; height: 20px; background: #1E40AF; }",
    )
    resultat, trouves = constats(deck)
    assert resultat.returncode == 1
    assert any(c["type"] == "chrome-gap" for c in trouves)


def test_folio_absent(tmp_path):
    deck = ecrire_deck(tmp_path, "sans-folio.html", [""])
    deck.write_text(deck.read_text(encoding="utf-8").replace("tag-folio", "tag-muet"), encoding="utf-8")
    resultat, trouves = constats(deck)
    assert resultat.returncode == 1
    assert any(c["type"] == "folio" and "absent" in c["message"] for c in trouves)


def test_folio_non_croissant(tmp_path):
    deck = ecrire_deck(tmp_path, "folios.html", ["", "", ""])
    deck.write_text(
        deck.read_text(encoding="utf-8").replace("<strong>03</strong>", "<strong>01</strong>"),
        encoding="utf-8",
    )
    resultat, trouves = constats(deck)
    assert resultat.returncode == 1
    assert any(c["type"] == "folio" and "non croissant" in c["message"] for c in trouves)


def test_deck_sans_slide_sort_en_deux(tmp_path):
    vide = tmp_path / "vide.html"
    vide.write_text("<!doctype html><html><body><p>rien</p></body></html>", encoding="utf-8")
    assert lancer(vide).returncode == 2


def test_fichier_absent_sort_en_deux(tmp_path):
    assert lancer(tmp_path / "inexistant.html").returncode == 2


def test_classe_mono_est_un_token_exact(tmp_path):
    """`.monogram` n'est pas le registre mono : la classe doit être le token `mono`."""
    deck = ecrire_deck(
        tmp_path, "monogram.html",
        ['<p class="monogram">Un monogramme</p>'],
        styles=(
            ".monogram { position: absolute; left: 80px; top: 400px; font-size: 28px;"
            " color: #0F172A; font-family: ui-monospace, monospace; }"
        ),
    )
    _, trouves = constats(deck)
    assert [c for c in trouves if c["type"] == "police"]


def test_classe_mono_exacte_est_toleree(tmp_path):
    deck = ecrire_deck(
        tmp_path, "mono-token.html",
        ['<p class="tick mono">42</p>'],
        styles=(
            ".mono { position: absolute; left: 80px; top: 400px; font-size: 28px;"
            " color: #0F172A; font-family: ui-monospace, monospace; }"
        ),
    )
    _, trouves = constats(deck)
    assert not [c for c in trouves if c["type"] == "police"]


def test_plancher_du_chrome_a_son_propre_seuil(tmp_path):
    """Le texte du chrome est soumis au plancher, avec un seuil propre plus bas."""
    deck = ecrire_deck(tmp_path, "chrome-typo.html", [""], styles=".tag-folio { font-size: 10px; }")
    resultat, trouves = constats(deck)
    plancher = [c for c in trouves if c["type"] == "plancher-typo"]
    assert plancher and "plancher du chrome 12px" in plancher[0]["message"]
    assert resultat.returncode == 1


def test_chrome_a_douze_pixels_passe(tmp_path):
    deck = ecrire_deck(tmp_path, "chrome-ok.html", [""], styles=".tag-folio { font-size: 12px; }")
    _, trouves = constats(deck)
    assert not [c for c in trouves if c["type"] == "plancher-typo"]


def test_seuil_du_chrome_reglable(tmp_path):
    deck = ecrire_deck(tmp_path, "chrome-seuil.html", [""], styles=".tag-folio { font-size: 12px; }")
    _, trouves = constats(deck, "--min-font-chrome", "14")
    assert [c for c in trouves if c["type"] == "plancher-typo"]


def test_troncature_des_debordements_signalee(tmp_path):
    """Au-delà de 20 débordements par slide, le rapport dit ce qu'il n'a pas listé."""
    blocs = "".join(f'<div class="d{i} deb"></div>' for i in range(25))
    deck = ecrire_deck(
        tmp_path, "troncature.html", [blocs],
        styles=".deb { position: absolute; left: 1850px; top: 100px; width: 200px; height: 20px; background: #1E40AF; }",
    )
    _, trouves = constats(deck)
    troncatures = [c for c in trouves if c["type"] == "troncature"]
    assert troncatures, [c["type"] for c in trouves]
    assert "5 débordements non listés" in troncatures[0]["message"]
    assert troncatures[0]["niveau"] == "avertissement"


def test_monospace_du_chrome_est_exemptee(tmp_path):
    """Le registre mono du chrome est déclaré par le système de slides."""
    deck = ecrire_deck(
        tmp_path, "chrome-mono.html", [""],
        styles=".tag-folio { font-family: 'JetBrains Mono', ui-monospace, monospace; }",
    )
    resultat, trouves = constats(deck)
    assert not [c for c in trouves if c["type"] == "police"], resultat.stdout
    assert resultat.returncode == 0


def test_langue_basculee_avant_audit(tmp_path):
    """`--lang fr` appelle `window.__setLang` : le texte français est audité."""
    deck = ecrire_deck(
        tmp_path, "bilingue.html",
        ['<p class="fine">short</p>'
         '<script>window.__setLang = l => { '
         'document.querySelector(".fine").textContent = l === "fr" ? "version française" : "short";'
         ' };</script>'],
        styles=".fine { position: absolute; left: 80px; top: 400px; font-size: 14px; color: #0F172A; }",
    )
    _, sans = constats(deck)
    assert not [c for c in sans if c["type"] == "lang"]

    _, avec = constats(deck, "--lang", "fr")
    assert not [c for c in avec if c["type"] == "lang"]
    plancher = [c for c in avec if c["type"] == "plancher-typo"]
    assert plancher and "corps 14px" in plancher[0]["message"]


def test_deck_sans_bascule_de_langue_est_signale(tmp_path):
    deck = ecrire_deck(tmp_path, "monolingue.html", [""])
    resultat, trouves = constats(deck, "--lang", "fr")
    lang = [c for c in trouves if c["type"] == "lang"]
    assert lang and "__setLang absente" in lang[0]["message"]
    assert lang[0]["niveau"] == "avertissement"
    assert resultat.returncode == 0


def test_les_lignes_de_resume_ne_gonflent_pas_le_bilan(tmp_path):
    """Le plafond de lisibilité ne doit pas faire grossir `summary`."""
    blocs = "".join(f'<p class="p{i} fine">note</p>' for i in range(12))
    deck = ecrire_deck(
        tmp_path, "plafond.html", [blocs],
        styles=".fine { position: relative; font-size: 10px; color: #0F172A; }",
    )
    resultat = lancer(deck, "--format", "json")
    rapport = json.loads(resultat.stdout)
    listees = [c for slide in rapport["slides"] for c in slide["constats"]]
    resumes = [c for c in listees if c["niveau"] == "resume"]
    assert resumes, resultat.stdout
    assert rapport["summary"]["errors"] == sum(1 for c in listees if c["niveau"] == "erreur")
    assert rapport["summary"]["errors_total"] > rapport["summary"]["errors"]


# --------------------------------------------------------------------------
# Parité du moteur (docs/engine-parity.md), contrôlée avant tout navigateur
# --------------------------------------------------------------------------

def lancer_brut(deck: Path, *options: str) -> subprocess.CompletedProcess:
    """Sans les options par défaut : le contrôle de parité est actif."""
    return subprocess.run(
        [sys.executable, str(QA), str(deck), "--attente", "200", "--police", "Inter", *options],
        capture_output=True, text=True, cwd=str(REPO), timeout=180,
    )


def test_parite_moteur_manquante_echoue(tmp_path):
    deck = ecrire_deck(tmp_path, "sans-moteur.html", [""])
    resultat = lancer_brut(deck)
    assert resultat.returncode == 1, resultat.stdout + resultat.stderr
    assert "parité du moteur" in resultat.stdout
    assert "body.presenting" in resultat.stdout


def test_parite_moteur_manquante_en_json(tmp_path):
    deck = ecrire_deck(tmp_path, "sans-moteur.html", [""])
    resultat = lancer_brut(deck, "--format", "json")
    rapport = json.loads(resultat.stdout)
    assert resultat.returncode == 1
    manquants = {m["marker"] for m in rapport["engine"]["missing"]}
    assert {"nav-peek", "SLIDE_COUNT", "window.print"} <= manquants


def test_parite_moteur_complete_passe(tmp_path):
    # Les marqueurs canoniques, posés en commentaire : le contrôle est textuel.
    marqueurs = ("<!-- body.presenting nav-peek requestFullscreen SLIDE_COUNT "
                 "printing-pdf window.print --brand-pattern overview -->")
    deck = ecrire_deck(tmp_path, "moteur.html", [marqueurs])
    resultat = lancer_brut(deck)
    assert resultat.returncode == 0, resultat.stdout + resultat.stderr
    assert "All slides clean" in resultat.stdout


# --------------------------------------------------------------------------
# Folios du moteur, et formats sans folio
# --------------------------------------------------------------------------

def test_folio_du_moteur_nav_num(tmp_path):
    """Le moteur numérote `.nav-num` ; le sélecteur par défaut le reconnaît."""
    deck = ecrire_deck(tmp_path, "nav-num.html", ["", ""])
    deck.write_text(deck.read_text(encoding="utf-8").replace("tag-folio", "nav-num"), encoding="utf-8")
    _, trouves = constats(deck)
    assert not [c for c in trouves if c["type"] == "folio"]


def test_sans_folio_saute_le_controle(tmp_path):
    deck = ecrire_deck(tmp_path, "carrousel.html", [""])
    deck.write_text(deck.read_text(encoding="utf-8").replace("tag-folio", "tag-muet"), encoding="utf-8")
    resultat, trouves = constats(deck, "--sans-folio")
    assert not [c for c in trouves if c["type"] == "folio"]
    assert resultat.returncode == 0, resultat.stdout


# --------------------------------------------------------------------------
# Source des familles de police : --police, tokens.json, variables du deck
# --------------------------------------------------------------------------

def lancer_sans_police(deck: Path, *options: str) -> tuple[subprocess.CompletedProcess, dict]:
    resultat = subprocess.run(
        [sys.executable, str(QA), str(deck), "--attente", "200", "--no-engine-check",
         "--format", "json", *options],
        capture_output=True, text=True, cwd=str(REPO), timeout=180,
    )
    return resultat, json.loads(resultat.stdout)


def test_familles_lues_dans_tokens(tmp_path):
    tokens = tmp_path / "tokens.json"
    tokens.write_text(json.dumps({"font": {"primary": {"$value": ["Fictive Sans", "sans-serif"]}}}),
                      encoding="utf-8")
    deck = ecrire_deck(tmp_path, "tokens.html", [""])
    resultat, rapport = lancer_sans_police(deck, "--tokens", str(tokens))
    assert rapport["summary"]["fonts"] == ["Fictive Sans"]
    trouves = [c for slide in rapport["slides"] for c in slide["constats"]]
    assert any(c["type"] == "police" and "Inter" in c["message"] for c in trouves)
    assert resultat.returncode == 1


def test_familles_lues_dans_les_variables_du_deck(tmp_path):
    """Sans tokens.json, le deck déclare lui-même sa police (--font-display)."""
    deck = ecrire_deck(tmp_path, "variables.html", [""],
                       styles=":root { --font-display: 'Inter', system-ui, sans-serif; }")
    resultat, rapport = lancer_sans_police(deck, "--tokens", str(tmp_path / "absent.json"))
    assert rapport["summary"]["fonts"] == ["Inter"]
    assert "variables" in rapport["summary"]["fonts_source"]
    assert resultat.returncode == 0, resultat.stdout


def test_aucune_famille_connue_est_signalee(tmp_path):
    deck = ecrire_deck(tmp_path, "inconnue.html", [""])
    resultat, rapport = lancer_sans_police(deck, "--tokens", str(tmp_path / "absent.json"))
    trouves = [c for slide in rapport["slides"] for c in slide["constats"]]
    assert any(c["type"] == "police" and c["niveau"] == "avertissement" for c in trouves)
    assert resultat.returncode == 0

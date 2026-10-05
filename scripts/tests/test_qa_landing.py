"""Tests de 05-web-content/scripts/qa-landing.py (QA des landing pages statiques).

Deux familles : les règles d'audit, en pur Python sur des relevés fabriqués à la
main, et les contrôles de bout en bout, qui pilotent un vrai Chromium et sont
ignorés proprement si Playwright ou le navigateur manquent.

Les pages sont écrites dans `tmp_path`, jamais dans le dépôt. Marque fictive
(« Acme », les exemples de docs/placeholders.json) : couleurs et textes
inventés, jamais ceux d'un client.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
QA = REPO / "05-web-content" / "scripts" / "qa-landing.py"


def _charger():
    spec = importlib.util.spec_from_file_location("qa_landing", QA)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


qa = _charger()

MOBILE = {"width": 375, "height": 812}
BUREAU = {"width": 1440, "height": 900}
PLANCHERS = {"etiquette": 12.0, "courant": 16.0, "courant_bureau": 18.0, "mots_texte_courant": 12}


def types(constats: list[dict], niveau: str = "erreur") -> list[str]:
    return [c["type"] for c in constats if c["niveau"] == niveau]


# --------------------------------------------------------------------------
# Textes : planchers, contraste, opacité, texture
# --------------------------------------------------------------------------

def texte(fs=18.0, mots=4, couleur="rgb(15, 23, 42)", fonds=None, niv=None, **autres) -> dict:
    fonds = fonds if fonds is not None else [{"c": "rgb(248, 250, 252)", "i": "none"}]
    niv = niv if niv is not None else [{"o": 1.0, "r": "repeat", "s": "auto"} for _ in fonds]
    base = {"nom": "p.test", "tag": "P", "texte": "un texte", "fs": fs, "mots": mots, "poids": 400,
            "police": "Inter, sans-serif", "couleur": couleur, "fonds": fonds, "niv": niv, "gradient": False}
    base.update(autres)
    return base


def test_etiquette_sous_douze_pixels():
    constats, _ = qa.auditer_textes([texte(fs=11.5)], MOBILE, PLANCHERS, [])
    assert types(constats) == ["plancher-typo"]


def test_etiquette_courte_a_quatorze_pixels_passe():
    constats, _ = qa.auditer_textes([texte(fs=14, mots=5)], MOBILE, PLANCHERS, [])
    assert constats == []


def test_texte_courant_sous_seize_pixels_sur_mobile():
    constats, _ = qa.auditer_textes([texte(fs=15, mots=20)], MOBILE, PLANCHERS, [])
    assert types(constats) == ["plancher-typo"]
    assert "16px" in constats[0]["message"]


def test_texte_courant_a_seize_pixels_passe_sur_mobile_avertit_sur_bureau():
    mobile, _ = qa.auditer_textes([texte(fs=16, mots=20)], MOBILE, PLANCHERS, [])
    bureau, _ = qa.auditer_textes([texte(fs=16, mots=20)], BUREAU, PLANCHERS, [])
    assert mobile == []
    assert types(bureau) == [] and types(bureau, "avertissement") == ["plancher-typo"]
    assert "18px" in bureau[0]["message"]


def test_texte_courant_sous_seize_pixels_est_une_erreur_partout():
    for vp in (MOBILE, BUREAU):
        constats, _ = qa.auditer_textes([texte(fs=15, mots=20)], vp, PLANCHERS, [])
        assert types(constats) == ["plancher-typo"] and "16px" in constats[0]["message"]


def test_contraste_compose_avec_l_opacite():
    # #0F172A sur #F8FAFC passe largement ; à 30 % d'opacité, plus du tout
    net, _ = qa.auditer_textes([texte()], MOBILE, PLANCHERS, [])
    estompe, _ = qa.auditer_textes(
        [texte(niv=[{"o": 0.3, "r": "repeat", "s": "auto"}, {"o": 1.0, "r": "repeat", "s": "auto"}],
               fonds=[{"c": "rgba(0, 0, 0, 0)", "i": "none"}, {"c": "rgb(248, 250, 252)", "i": "none"}])],
        MOBILE, PLANCHERS, [])
    assert net == []
    assert types(estompe) == ["contraste"] and "opacité 0.30" in estompe[0]["message"]


def test_texture_sur_aplat_ramenee_a_l_aplat():
    fonds = [{"c": "rgb(248, 250, 252)", "i": 'url("grain.svg")'}]
    constats, _ = qa.auditer_textes(
        [texte(fonds=fonds, niv=[{"o": 1.0, "r": "repeat", "s": "auto"}])], MOBILE, PLANCHERS, [])
    assert constats == []


def test_photo_ou_degrade_non_calculable_en_avertissement():
    photo = [{"c": "rgb(15, 23, 42)", "i": 'url("hero.jpg")'}]
    constats, _ = qa.auditer_textes(
        [texte(couleur="rgb(255, 255, 255)", fonds=photo, niv=[{"o": 1, "r": "no-repeat", "s": "cover"}])],
        MOBILE, PLANCHERS, [])
    assert types(constats, "avertissement") == ["contraste"]


def test_degrade_juge_au_pire_et_au_meilleur_point():
    blanc = "rgb(255, 255, 255)"
    sombre_vers_clair = [{"c": "rgba(0, 0, 0, 0)", "i": "linear-gradient(rgb(15, 23, 42), rgb(248, 250, 252))"},
                         {"c": "rgb(248, 250, 252)", "i": "none"}]
    clair_vers_clair = [{"c": "rgba(0, 0, 0, 0)", "i": "linear-gradient(rgb(248, 250, 252), rgb(226, 232, 240))"},
                        {"c": "rgb(248, 250, 252)", "i": "none"}]
    niv = [{"o": 1, "r": "repeat", "s": "auto", "b": "section.bande"}, {"o": 1, "r": "repeat", "s": "auto"}]
    doute, _ = qa.auditer_textes([texte(couleur=blanc, fonds=sombre_vers_clair, niv=niv),
                                  texte(couleur=blanc, fonds=sombre_vers_clair, niv=niv)],
                                 MOBILE, PLANCHERS, [])
    echec, _ = qa.auditer_textes([texte(couleur=blanc, fonds=clair_vers_clair, niv=niv)], MOBILE, PLANCHERS, [])
    assert types(doute, "avertissement") == ["contraste"]          # un seul constat pour le fond
    assert "2 texte(s)" in doute[0]["message"] and "section.bande" in doute[0]["message"]
    assert types(echec) == ["contraste"] and "tous les arrêts du dégradé" in echec[0]["message"]


def test_police_hors_marque_si_familles_connues():
    constats, _ = qa.auditer_textes([texte(police="Comic Sans MS, cursive")], MOBILE, PLANCHERS, ["Inter"])
    assert types(constats) == ["police"]


def test_decor_et_scene_masquee():
    decor, _ = qa.auditer_textes([texte(fs=9, couleur="rgb(240, 240, 240)", decor=True)], MOBILE, PLANCHERS, [])
    scene, _ = qa.auditer_textes([texte(fs=9, couleur="rgb(240, 240, 240)", cache=True)], MOBILE, PLANCHERS, [])
    assert decor == []                       # data-qa-decor : rien n'est jugé
    assert types(scene) == ["contraste"]     # aria-hidden : pas de plancher, mais le contraste reste


def test_texte_en_degrade_liste_a_part():
    constats, gradients = qa.auditer_textes([texte(gradient=True)], MOBILE, PLANCHERS, [])
    assert constats == [] and len(gradients) == 1


@pytest.mark.parametrize("image, repetition, taille, attendu", [
    ('url("dots.svg")', "repeat", "auto", True),
    ('url("photo.jpg")', "no-repeat", "auto", False),
    ('url("photo.jpg")', "repeat", "cover", False),
    ("linear-gradient(red, blue)", "repeat", "auto", False),
])
def test_est_texture(image, repetition, taille, attendu):
    assert qa.est_texture(image, repetition, taille) is attendu


# --------------------------------------------------------------------------
# Débordement, cibles, orphelins
# --------------------------------------------------------------------------

def test_debordement_reel():
    releve = {"client_width": 375, "scroll_width": 520, "overflow_html": "visible",
              "overflow_body": "visible", "debordants": [{"nom": "div.mockup", "droite": 145}]}
    constats = qa.auditer_debordement(releve)
    assert types(constats) == ["debordement"] and "div.mockup" in constats[0]["message"]


def test_debordement_masque_par_body():
    releve = {"client_width": 375, "scroll_width": 375, "overflow_html": "visible",
              "overflow_body": "hidden", "debordants": [{"nom": "div.halo", "droite": 80}],
              "debordants_total": 1}
    assert types(qa.auditer_debordement(releve), "avertissement") == ["debordement-masque"]


def test_pas_de_debordement():
    releve = {"client_width": 375, "scroll_width": 375, "overflow_html": "visible",
              "overflow_body": "visible", "debordants": []}
    assert qa.auditer_debordement(releve) == []


def test_cibles_tactiles():
    cibles = [
        {"nom": "a.petit", "libelle": "x", "cta": False, "l": 20, "h": 20},
        {"nom": "a.moyen", "libelle": "x", "cta": False, "l": 120, "h": 32},
        {"nom": "a.btn", "libelle": "Réserver", "cta": True, "l": 160, "h": 36},
        {"nom": "a.ok", "libelle": "x", "cta": True, "l": 200, "h": 48},
    ]
    constats = qa.auditer_cibles(cibles)
    assert [(c["niveau"], c["cible"]) for c in constats] == [
        ("erreur", "a.petit"), ("avertissement", "a.moyen"), ("erreur", "a.btn")]


# --------------------------------------------------------------------------
# CTA
# --------------------------------------------------------------------------

def cta(chemin, genre="ancre", dest="#offre", **autres) -> dict:
    base = {"chemin": chemin, "nom": chemin, "libelle": "Réserver", "genre": genre, "dest": dest,
            "cta": "", "position": "", "crochet": "", "dans_main": True, "visible": True,
            "fixe": False, "pli": True, "cible_existe": True, "formulaires": []}
    base.update(autres)
    return base


def test_cta_absent():
    constats, cles, primaire, _ = qa.auditer_ctas([])
    assert types(constats) == ["cta-absent"] and primaire is None


def test_primaire_explicite_l_emporte():
    ctas = [cta("a1", dest="#ailleurs"), cta("a2", cta="primaire", dest="#offre")]
    _, _, primaire, regle = qa.auditer_ctas(ctas)
    assert primaire["chemin"] == "a2" and "data-cta" in regle


def test_ancre_et_envoi_du_meme_formulaire_sont_la_meme_conversion():
    ctas = [
        cta("hero", dest="#offre", formulaires=["form1"], position="hero"),
        cta("envoi", genre="envoi", dest="https://example.test/lead", formulaire="form1", ancetres=["offre"]),
        cta("autre", dest="#temoignages"),
    ]
    constats, _, _, _ = qa.auditer_ctas(ctas)
    assert [c["primaire"] for c in ctas] == [True, True, False]
    # une ancre de la page guide la lecture : pas de « hors objectif »
    assert types(constats, "avertissement") == []


def test_lien_sortant_reste_hors_objectif():
    ctas = [
        cta("hero", dest="#offre", formulaires=["form1"], position="hero"),
        cta("envoi", genre="envoi", dest="https://example.test/lead", formulaire="form1", ancetres=["offre"]),
        cta("sortie", genre="lien", dest="https://example.test/blog"),
    ]
    constats, _, _, _ = qa.auditer_ctas(ctas)
    assert types(constats, "avertissement") == ["cta-hors-objectif"]


@pytest.mark.parametrize("defaut", [
    {"dest": "#", "defaut": "href vide ou factice"},
    {"dest": None, "defaut": "sans href"},
    {"dest": "#nulle-part", "cible_existe": False},
])
def test_cta_sans_destination(defaut):
    constats, _, _, _ = qa.auditer_ctas([cta("a", **defaut)])
    assert "cta-destination" in types(constats)


def test_endpoint_en_placeholder_avertit():
    constats, _, _, _ = qa.auditer_ctas([cta("b", genre="envoi", dest="{{FORM_ENDPOINT}}",
                                             formulaire="f", ancetres=[])])
    assert types(constats, "avertissement") == ["cta-destination"]


def test_suivi_declare_sans_evenement_est_une_erreur():
    primaires = [cta("a", genre="ancre"), cta("b", genre="envoi", formulaire="f")]
    clics = {"a": {"trouve": True, "evenements": []}, "b": {"trouve": True, "evenements": []}}
    constats = qa.auditer_suivi("gtag.js / GTM", primaires, clics)
    assert types(constats) == ["tracking"]
    assert types(constats, "avertissement") == ["tracking"]  # l'envoi peut partir après le serveur


def test_suivi_declare_avec_evenement():
    primaires = [cta("a")]
    assert qa.auditer_suivi("gtag.js / GTM", primaires, {"a": {"evenements": ["cta_click"]}}) == []
    assert primaires[0]["evenements"] == ["cta_click"]


def envoi(**autres) -> dict:
    base = {"trouve": True, "envoi": True, "attendu": "generate_lead", "demo": False, "crochet": True,
            "rempli": ["email"], "refus": [], "evenements": [], "requetes": []}
    base.update(autres)
    return base


def test_formulaire_rempli_evenement_attendu():
    primaires = [cta("b", genre="envoi", formulaire="f")]
    clics = {"b": envoi(evenements=["generate_lead"], requetes=[{"methode": "POST", "url": "https://example.test/lead"}])}
    assert qa.auditer_suivi("dataLayer initialisé", primaires, clics) == []
    assert primaires[0]["evenements"] == ["generate_lead"] and primaires[0]["requetes"]


def test_formulaire_de_demo_attend_form_demo_submit():
    primaires = [cta("b", genre="envoi", formulaire="f")]
    bon = {"b": envoi(demo=True, attendu="form_demo_submit", evenements=["form_demo_submit"])}
    assert qa.auditer_suivi("dataLayer initialisé", primaires, bon) == []
    compte = {"b": envoi(demo=True, attendu="form_demo_submit", evenements=["generate_lead"])}
    constats = qa.auditer_suivi("dataLayer initialisé", primaires, compte)
    assert types(constats) == ["tracking"] and "jamais compter comme un lead" in constats[0]["message"]


def test_formulaire_de_demo_qui_part_sur_le_reseau():
    primaires = [cta("b", genre="envoi", formulaire="f")]
    clics = {"b": envoi(demo=True, attendu="form_demo_submit", evenements=["form_demo_submit"],
                        requetes=[{"methode": "POST", "url": "https://example.test/lead"}])}
    constats = qa.auditer_suivi("dataLayer initialisé", primaires, clics)
    assert types(constats) == ["tracking"] and "requête POST" in constats[0]["message"]


def test_formulaire_avec_crochet_sans_evenement_est_une_erreur():
    primaires = [cta("b", genre="envoi", formulaire="f")]
    assert types(qa.auditer_suivi("gtag.js / GTM", primaires, {"b": envoi()})) == ["tracking"]
    # refusé par le remplissage de test : avertissement, à vérifier à la main
    refuse = qa.auditer_suivi("gtag.js / GTM", primaires, {"b": envoi(refus=["siret"])})
    assert types(refuse) == [] and types(refuse, "avertissement") == ["tracking"]
    # mauvais événement
    autre = qa.auditer_suivi("gtag.js / GTM", primaires, {"b": envoi(evenements=["cta_click"])})
    assert types(autre) == ["tracking"]


def test_suivi_non_declare_exige_un_crochet():
    assert types(qa.auditer_suivi("", [cta("a")], None), "avertissement") == ["tracking"]
    assert qa.auditer_suivi("", [cta("a", crochet="data-track=cta_click")], None) == []


# --------------------------------------------------------------------------
# Page : langue, titres, alternatives, noms, champs, placeholders
# --------------------------------------------------------------------------

def page(**autres) -> dict:
    base = {"lang": "fr", "titre": "Acme", "meta_viewport": True,
            "titres": [{"niveau": 1, "balise": "h1", "nom": "h1", "texte": "Livrer sans stress",
                        "rendu": True, "aria_hidden": False}],
            "images": [], "roles_img": [], "sans_nom": [], "champs": [], "placeholders": []}
    base.update(autres)
    return base


def titre(niveau, texte_="Un titre", rendu=True):
    return {"niveau": niveau, "balise": f"h{niveau}", "nom": f"h{niveau}", "texte": texte_,
            "rendu": rendu, "aria_hidden": False}


def test_page_propre():
    assert qa.auditer_page(page(), []) == []


@pytest.mark.parametrize("lang", [None, "", "{{BRAND_LANGUAGE}}", "français"])
def test_lang_absent_ou_invalide(lang):
    assert types(qa.auditer_page(page(lang=lang), [])) == ["lang"]


def test_deux_h1_et_niveau_saute():
    constats = qa.auditer_page(page(titres=[titre(1), titre(1, "Autre"), titre(2), titre(4)]), [])
    assert sorted(types(constats)) == ["titres-h1", "titres-ordre"]


def test_titre_masque_ignore():
    constats = qa.auditer_page(page(titres=[titre(1), titre(3, rendu=False), titre(2)]), [])
    assert constats == []


def test_ponctuation_des_titres_mais_pas_les_decimales():
    constats = qa.auditer_page(page(titres=[titre(1, "Livrer, enfin"), titre(2, "Une offre claire."),
                                            titre(2, "1,5 jour gagné par semaine")]), [])
    assert types(constats, "avertissement") == ["titre-ponctuation", "titre-ponctuation"]


def test_images_noms_champs_placeholders():
    constats = qa.auditer_page(page(
        images=[{"nom": "img.a", "alt": None, "src": "a.webp", "aria_hidden": False, "presentation": False},
                {"nom": "img.b", "alt": "", "src": "b.webp", "aria_hidden": False, "presentation": False},
                {"nom": "img.c", "alt": "IMG_2041.jpg", "src": "c.jpg", "aria_hidden": False,
                 "presentation": False}],
        sans_nom=[{"nom": "button.icone", "href": ""}],
        champs=[{"nom": "input#email", "type": "email", "label": False, "placeholder": "vous@acme.test"}],
        placeholders=["{{FORM_ENDPOINT}}"],
    ), [])
    assert sorted(types(constats)) == ["champ-sans-label", "image-alt", "nom-accessible"]
    assert sorted(types(constats, "avertissement")) == ["image-alt", "placeholder"]


def test_pastille_de_surtitre():
    constats = qa.auditer_page(page(), [{"nom": "span.pill", "texte": "Nouveau", "titre": "Un titre"}])
    assert types(constats, "avertissement") == ["surtitre-pastille"]


# --------------------------------------------------------------------------
# Mouvement réduit
# --------------------------------------------------------------------------

def test_mouvement_reduit():
    masque = {"chemin": "p1", "nom": "p.reveal", "texte": "Bloc"}
    apparu = {"chemin": "p2", "nom": "p.reveal2", "texte": "Bloc 2"}
    menu = {"chemin": "p3", "nom": "li.menu", "texte": "Menu"}
    constats = qa.auditer_mouvement(
        masques_charge=[masque, apparu, menu], masques_apres=[masque, menu], masques_normal={"p3"},
        anims={"animations": [{"nom": "span.dot", "genre": "animation pulse", "iterations": "infinie"}],
               "videos": []},
        avant={"c1": {"nom": "span.compteur", "t": "none|none|none|none", "o": "1", "x": "12 j 04:10:09"},
               "c2": {"nom": "span.mot", "t": "none|none|none|none", "o": "1", "x": "agences"}},
        apres={"c1": {"nom": "span.compteur", "t": "none|none|none|none", "o": "1", "x": "12 j 04:10:08"},
               "c2": {"nom": "span.mot", "t": "none|none|none|none", "o": "1", "x": "équipes"}},
    )
    assert sorted(types(constats)) == ["mouvement-reduit-anime", "mouvement-reduit-anime",
                                       "mouvement-reduit-masque"]
    assert sorted(types(constats, "avertissement")) == ["compte-a-rebours", "mouvement-reduit-apparition"]


def test_plafond_et_totaux():
    constats = [qa.constat("erreur", "contraste", f"c{i}") for i in range(10)]
    plafonnes = qa.plafonner(constats, 8)
    assert qa.compter(plafonnes, "erreur") == 8
    assert plafonnes[-1]["niveau"] == "resume" and plafonnes[-1]["masques"] == 2
    assert qa.par_type(constats) == {"contraste": {"errors": 10, "warnings": 0}}


# --------------------------------------------------------------------------
# Bout en bout, dans Chromium
# --------------------------------------------------------------------------

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


CHROMIUM = pytest.mark.skipif(
    not _chromium_disponible(), reason="Playwright ou Chromium indisponible sur cette machine"
)

# Page propre de référence : marque fictive, texte courant à 18 px, CTA de 52 px,
# apparitions au défilement coupées par prefers-reduced-motion.
PAGE = """<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Acme · livrer sans stress</title>
<style>
  :root {{ --ink: #0F172A; --paper: #F8FAFC; --primary: #1E40AF; }}
  body {{ margin: 0; font: 18px/1.6 Inter, system-ui, sans-serif; color: var(--ink); background: var(--paper); }}
  main {{ max-width: 960px; margin: 0 auto; padding: 0 20px; }}
  section {{ padding: 48px 0; }}
  h1 {{ font-size: 40px; line-height: 1.15; }}
  .btn {{ display: inline-block; padding: 14px 24px; min-height: 52px; box-sizing: border-box;
          background: var(--primary); color: #fff; border-radius: 12px; text-decoration: none; }}
  label {{ display: block; font-size: 14px; }}
  input {{ font: inherit; padding: 12px; min-height: 48px; box-sizing: border-box; width: 100%; }}
  html.anime [data-reveal] {{ opacity: 0; transform: translateY(16px); transition: opacity .6s, transform .6s; }}
  html.anime [data-reveal].vu {{ opacity: 1; transform: none; }}
  {styles}
</style>
{tete}
</head><body>
<main>
  <section id="hero">
    <h1>Livrer chaque semaine sans nuit blanche</h1>
    <p>La plateforme fictive qui range vos mises en production, vos tests et vos retours au même endroit pour toute l'équipe.</p>
    <a class="btn" href="#offre" data-cta="primaire" data-track="cta_click">Essayer gratuitement</a>
  </section>
  {corps}
  <section id="offre" data-reveal>
    <h2>Commencer aujourd'hui</h2>
    <form action="https://example.test/lead" method="post" data-track="generate_lead">
      <label for="email">Adresse email</label>
      <input id="email" name="email" type="email" autocomplete="email" required>
      <p><button class="btn" type="submit">Essayer gratuitement</button></p>
    </form>
  </section>
</main>
<script>
  if (!matchMedia('(prefers-reduced-motion: reduce)').matches && 'IntersectionObserver' in window) {{
    document.documentElement.classList.add('anime');
    const io = new IntersectionObserver(es => es.forEach(e => {{
      if (e.isIntersecting) {{ e.target.classList.add('vu'); io.unobserve(e.target); }} }}));
    document.querySelectorAll('[data-reveal]').forEach(el => io.observe(el));
  }}
  {script}
</script>
</body></html>"""


def ecrire(dossier: Path, corps: str = "", styles: str = "", tete: str = "", script: str = "",
           lang: str = "fr", nom: str = "page.html") -> Path:
    chemin = dossier / nom
    chemin.write_text(PAGE.format(corps=corps, styles=styles, tete=tete, script=script, lang=lang),
                      encoding="utf-8")
    return chemin


def lancer(cible: Path, *options: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(QA), str(cible), "--attente", "150", *options],
        capture_output=True, text=True, cwd=str(REPO), timeout=240,
    )


def rapport(cible: Path, *options: str) -> tuple[subprocess.CompletedProcess, dict]:
    resultat = lancer(cible, "--format", "json", *options)
    assert resultat.stdout, f"aucune sortie JSON : {resultat.stderr}"
    return resultat, json.loads(resultat.stdout)


def tous(donnees: dict, niveau: str = "erreur") -> list[str]:
    constats = list(donnees["page"]) + list(donnees["mouvement_reduit"]["constats"])
    for vue in donnees["viewports"]:
        constats += vue["constats"]
    return sorted(c["type"] for c in constats if c["niveau"] == niveau)


def test_fichier_absent_sort_en_deux(tmp_path):
    assert lancer(tmp_path / "absente.html").returncode == 2


def test_viewport_invalide_sort_en_deux(tmp_path):
    assert lancer(ecrire(tmp_path), "--viewports", "375").returncode == 2


@CHROMIUM
def test_page_propre_sur_les_trois_ecrans(tmp_path):
    resultat, donnees = rapport(ecrire(tmp_path))
    assert resultat.returncode == 0, tous(donnees) + tous(donnees, "avertissement")
    assert donnees["summary"]["errors"] == 0
    assert donnees["summary"]["ctas_primaires"] == 2   # l'ancre et l'envoi du même formulaire
    assert all(c["primaire"] for c in donnees["ctas"])
    assert "Landing clean" in lancer(ecrire(tmp_path, nom="b.html")).stdout


@CHROMIUM
def test_defauts_de_structure(tmp_path):
    corps = """
    <section><h1>Un second titre principal</h1><h4>Niveau sauté</h4>
      <img src="capture.webp" width="40" height="40">
      <button class="icone" type="button"><svg width="20" height="20"></svg></button>
      <input type="text" placeholder="Votre société"></section>"""
    _, donnees = rapport(ecrire(tmp_path, corps=corps, lang=""), "--viewports", "1440x900")
    for attendu in ("lang", "titres-h1", "titres-ordre", "image-alt", "nom-accessible", "champ-sans-label"):
        assert attendu in tous(donnees), attendu


@CHROMIUM
def test_debordement_et_petits_textes_sur_mobile(tmp_path):
    corps = """<section><div style="width: 640px; height: 20px; background: #1E40AF"></div>
      <p style="font-size: 14px">Ce paragraphe de démonstration compte bien plus de douze mots pour être lu comme du texte courant.</p>
      <p><a href="#hero" style="font-size: 11px">mentions</a></p></section>"""
    _, donnees = rapport(ecrire(tmp_path, corps=corps), "--viewports", "375x812")
    erreurs = tous(donnees)
    assert "debordement" in erreurs
    assert erreurs.count("plancher-typo") >= 2


@CHROMIUM
def test_cta_primaire_sous_le_pli_mobile(tmp_path):
    styles = "#hero { padding-top: 1200px; }"
    _, donnees = rapport(ecrire(tmp_path, styles=styles), "--viewports", "375x812")
    assert "cta-pli" in tous(donnees)


@CHROMIUM
def test_cible_tactile_trop_petite(tmp_path):
    styles = "#hero .btn { min-height: 0; padding: 4px 8px; font-size: 14px; }"
    _, donnees = rapport(ecrire(tmp_path, styles=styles), "--viewports", "375x812")
    assert "cible-tactile" in tous(donnees)


@CHROMIUM
def test_apparition_qui_ignore_le_mouvement_reduit(tmp_path):
    # le CSS masque sans condition, et le script se tait sous prefers-reduced-motion
    styles = """[data-cache] { opacity: 0; } [data-cache].vu { opacity: 1; }
      .pouls { display: inline-block; width: 12px; height: 12px; background: #F59E0B;
               animation: pouls 1.2s infinite; }
      @keyframes pouls { 50% { transform: scale(1.6); } }"""
    corps = """<section><h2 data-cache>Ce que vous gagnez</h2><span class="pouls" aria-hidden="true"></span></section>"""
    script = """if (!matchMedia('(prefers-reduced-motion: reduce)').matches)
      document.querySelectorAll('[data-cache]').forEach(el => el.classList.add('vu'));"""
    _, donnees = rapport(ecrire(tmp_path, corps=corps, styles=styles, script=script),
                         "--viewports", "1440x900")
    erreurs = [c["type"] for c in donnees["mouvement_reduit"]["constats"] if c["niveau"] == "erreur"]
    assert "mouvement-reduit-masque" in erreurs
    assert "mouvement-reduit-anime" in erreurs


@CHROMIUM
def test_suivi_declare_sans_evenement(tmp_path):
    tete = "<script>window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);}" \
           " gtag('js', new Date()); gtag('config', 'G-TEST');</script>"
    _, donnees = rapport(ecrire(tmp_path, tete=tete), "--viewports", "1440x900")
    assert donnees["summary"]["tracking"]
    assert "tracking" in tous(donnees)


@CHROMIUM
def test_suivi_declare_avec_evenement(tmp_path):
    tete = "<script>window.dataLayer = window.dataLayer || []; function gtag(){dataLayer.push(arguments);}" \
           " gtag('config', 'G-TEST');</script>"
    script = """document.addEventListener('click', e => {
      const el = e.target.closest('[data-track="cta_click"]');
      if (el) gtag('event', 'cta_click', { cta_position: 'hero' }); });
      document.addEventListener('submit', () => gtag('event', 'generate_lead'));"""
    resultat, donnees = rapport(ecrire(tmp_path, tete=tete, script=script), "--viewports", "1440x900")
    assert "tracking" not in tous(donnees) + tous(donnees, "avertissement")
    assert any(c.get("evenements") == ["cta_click"] for c in donnees["ctas"])
    assert resultat.returncode == 0


# --------------------------------------------------------------------------
# Suivi des formulaires de la bibliothèque : remplis, envoyés, réseau intercepté
# --------------------------------------------------------------------------

def _charger_assembleur():
    chemin = REPO / "05-web-content" / "scripts" / "assemble-landing.py"
    spec = importlib.util.spec_from_file_location("assemble_landing_qa", chemin)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _page_capture(dossier: Path, action: str, nom: str) -> Path:
    al = _charger_assembleur()
    spec = {"title": "Acme · guide", "page": "test", "samples": True, "tracking": {"mode": "datalayer"},
            "sections": [{"use": "hero", "slots": {"cta_href": "#guide"}},
                         {"use": "lead-capture", "id": "guide", "slots": {"action": action}}]}
    sortie = dossier / nom
    sortie.write_text(al.assembler(spec, sortie=sortie).html, encoding="utf-8")
    return sortie


def _envoi(donnees: dict) -> dict:
    return next(c for c in donnees["ctas"] if c["genre"] == "envoi")


@CHROMIUM
def test_suivi_formulaire_de_demo_compte_form_demo_submit(tmp_path):
    _, donnees = rapport(_page_capture(tmp_path, "{{FORM_ENDPOINT}}", "demo.html"), "--viewports", "1440x900")
    assert "tracking" not in tous(donnees)
    cta_envoi = _envoi(donnees)
    assert "form_demo_submit" in cta_envoi["evenements"] and "generate_lead" not in cta_envoi["evenements"]
    assert not [r for r in cta_envoi["requetes_interceptees"] or [] if r["methode"] == "POST"]


@CHROMIUM
def test_suivi_vrai_endpoint_generate_lead_intercepte(tmp_path):
    _, donnees = rapport(_page_capture(tmp_path, "https://forms.example.test/lead", "vrai.html"),
                         "--viewports", "1440x900")
    assert "tracking" not in tous(donnees) + tous(donnees, "avertissement")
    cta_envoi = _envoi(donnees)
    assert "generate_lead" in cta_envoi["evenements"]
    assert {"methode": "POST", "url": "https://forms.example.test/lead"} in cta_envoi["requetes_interceptees"]


@CHROMIUM
def test_cta_d_un_autre_etat_de_l_offre_ignore(tmp_path):
    """Un lien réservé à l'état clos (data-offer-show="closed") n'est pas un CTA de l'état ouvert."""
    corps = """<section><p data-offer-show="closed" hidden><a class="btn" href="https://example.test/alerte"
      data-track="cta_click">Être prévenu</a></p>
      <p data-offer-show="open waitlist"><a class="btn" href="https://example.test/ailleurs">Ailleurs</a></p></section>"""
    _, donnees = rapport(ecrire(tmp_path, corps=corps), "--viewports", "1440x900")
    destinations = [c["destination"] for c in donnees["ctas"]]
    assert "https://example.test/alerte" not in destinations
    assert "https://example.test/ailleurs" in destinations      # visible en état ouvert : inventorié

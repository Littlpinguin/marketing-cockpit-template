"""Tests de 05-web-content/scripts/assemble-landing.py et de la bibliothèque de sections.

Quatre familles :
  - le sous-ensemble Mustache (rendu, échappement, sections, erreurs) ;
  - l'intégrité de la bibliothèque livrée (05-web-content/templates/sections/) :
    chaque fragment se charge, documente ses slots, rend ses exemples sans
    balise orpheline, respecte la charte (titres, marqueurs, couleurs, CTA) ;
  - l'assemblage et ses garde-fous (avertissements, dossier pilotage/,
    page retouchée à la main, --check, --strict), dans tmp_path seulement ;
  - le rendu réel dans Chromium (mesure, mouvement réduit, état de l'offre),
    ignoré proprement si Playwright ou le navigateur manquent.

Marque fictive (« Meridian », exemples de docs/placeholders.json) : aucun
contenu client.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "05-web-content" / "scripts" / "assemble-landing.py"
LIBRARY = REPO / "05-web-content" / "templates" / "sections"
ASSETS = REPO / "05-web-content" / "templates" / "assets"


def _charger():
    spec = importlib.util.spec_from_file_location("assemble_landing", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module      # les dataclasses du script résolvent leur module
    spec.loader.exec_module(module)
    return module


al = _charger()


def run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True,
                          cwd=str(cwd or REPO))


# --------------------------------------------------------------------------
# Mustache
# --------------------------------------------------------------------------

def test_variable_echappee_et_brute():
    assert al.rendre_texte("<p>{{t}}</p>", {"t": "<b>&\"'"}) == "<p>&lt;b&gt;&amp;&quot;&#x27;</p>"
    assert al.rendre_texte("<p>{{{t}}}</p>", {"t": "<b>ok</b>"}) == "<p><b>ok</b></p>"


def test_section_liste_et_variables_de_boucle():
    gab = "{{#items}}[{{@index}}/{{@count}} {{name}}{{#@last}}!{{/@last}}]{{/items}}"
    assert al.rendre_texte(gab, {"items": [{"name": "a"}, {"name": "b"}]}) == "[1/2 a][2/2 b!]"


def test_section_valeur_simple_et_point():
    assert al.rendre_texte("{{#tags}}<i>{{.}}</i>{{/tags}}", {"tags": ["x", "y"]}) == "<i>x</i><i>y</i>"
    assert al.rendre_texte("{{#note}}<p>{{note}}</p>{{/note}}", {"note": "ici"}) == "<p>ici</p>"


def test_section_inverse_et_faux():
    gab = "{{#img}}IMG{{/img}}{{^img}}OBJET{{/img}}"
    for vide in (None, False, "", [], {}):
        assert al.rendre_texte(gab, {"img": vide}) == "OBJET"
    assert al.rendre_texte(gab, {"img": {"src": "a.webp"}}) == "IMG"


def test_recherche_dans_le_contexte_parent_et_noms_pointes():
    gab = "{{#plans}}{{name}}:{{toggle.unit}}:{{label}};{{/plans}}{{plans.length}}"
    ctx = {"plans": [{"name": "A"}, {"name": "B"}], "toggle": {"unit": "an"}, "label": "L"}
    assert al.rendre_texte(gab, ctx) == "A:an:L;B:an:L;2"


def test_marqueurs_du_depot_en_majuscules_intacts():
    assert al.rendre_texte('<form action="{{FORM_ENDPOINT}}">{{x}}', {"x": "1"}) == \
        '<form action="{{FORM_ENDPOINT}}">1'


@pytest.mark.parametrize("gabarit", ["{{#a}}x", "{{#a}}x{{/b}}", "x{{/a}}"])
def test_sections_mal_formees_refusees(gabarit):
    with pytest.raises(al.ErreurAssemblage):
        al.analyser(gabarit, "test")


# --------------------------------------------------------------------------
# Fragments fictifs
# --------------------------------------------------------------------------

def fragment(nom="demo", meta=None, corps=None) -> str:
    meta = meta or {"id": nom, "name": "Démo", "slots": {
        "title": {"type": "text", "doc": "titre", "example": "Titre d'exemple"}}}
    corps = corps or ('<!-- section:{{id}} -->\n<section id="{{id}}" class="s-demo section" '
                      'aria-labelledby="{{id}}-titre"><h2 id="{{id}}-titre">{{title}}</h2></section>\n'
                      '<!-- /section:{{id}} -->')
    return (f'<script type="application/json" data-section-meta>{json.dumps(meta, ensure_ascii=False)}</script>\n'
            f'<style data-section-style="{nom}">.s-demo {{ padding: 1px; }}</style>\n{corps}\n'
            f'<script data-section-script="{nom}">window.__demo = (window.__demo || 0) + 1;</script>\n')


def ecrire(dossier: Path, nom: str, texte: str) -> Path:
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / f"{nom}.html"
    chemin.write_text(texte, encoding="utf-8")
    return chemin


def test_fragment_valide_decoupe(tmp_path):
    f = al.charger_fragment(ecrire(tmp_path, "demo", fragment()))
    assert f.region == "main" and "padding" in f.style and "__demo" in f.script
    assert "<style" not in f.balisage and "<script" not in f.balisage


@pytest.mark.parametrize("meta, corps, motif", [
    ({"id": "autre", "slots": {}}, None, "meta.id"),
    ({"id": "demo", "slots": {"title": {"doc": "sans exemple"}}}, None, "example"),
    ({"id": "demo", "slots": {}}, None, "non déclaré"),
    ({"id": "demo", "slots": {"title": {"doc": "d", "example": "e"}}}, "<section>{{title}}</section>", "marqueurs"),
    ({"id": "demo", "region": "aside", "slots": {}}, "<!-- section:{{id}} --><!-- /section:{{id}} -->", "région"),
    ({"id": "demo", "engines": ["gsap"], "slots": {}}, "<!-- section:{{id}} --><!-- /section:{{id}} -->", "moteur"),
])
def test_fragments_mal_formes_refuses(tmp_path, meta, corps, motif):
    chemin = ecrire(tmp_path, "demo", fragment(meta=meta, corps=corps))
    with pytest.raises(al.ErreurAssemblage, match=motif):
        al.charger_fragment(chemin)


def test_fragment_sans_meta_refuse(tmp_path):
    chemin = ecrire(tmp_path, "demo", "<!-- section:{{id}} --><!-- /section:{{id}} -->")
    with pytest.raises(al.ErreurAssemblage, match="data-section-meta"):
        al.charger_fragment(chemin)


# --------------------------------------------------------------------------
# Bibliothèque livrée
# --------------------------------------------------------------------------

BIBLIOTHEQUE = al.bibliotheque(LIBRARY)
NOMS = sorted(BIBLIOTHEQUE)
CONVERSION = ["topbar", "hero", "final-cta", "sticky-bar", "offer-ticket", "lead-capture", "form",
              "pricing-table"]
RE_COULEUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\(|hsla?\(")


def test_la_bibliotheque_couvre_les_mecaniques_attendues():
    attendues = {"topbar", "hero", "proof-band", "logos", "problem-pinned", "pivot", "choice-gate",
                 "benefits", "journey", "program", "showcase-dark", "map-pinned", "people",
                 "testimonials", "outcomes", "for-whom", "process", "comparison", "pricing-table",
                 "offer-ticket", "lead-capture", "form", "faq", "legal", "final-cta", "footer",
                 "sticky-bar"}
    assert attendues <= set(NOMS)


@pytest.mark.parametrize("nom", NOMS)
def test_fiche_complete(nom):
    meta = BIBLIOTHEQUE[nom].meta
    for cle in ("name", "objection", "when", "avoid", "reduced_motion"):
        assert meta.get(cle), f"{nom} : « {cle} » manquant"
    for slot, spec in meta["slots"].items():
        assert spec["doc"].strip(), f"{nom}.{slot} : doc vide"


@pytest.mark.parametrize("nom", NOMS)
def test_exemples_rendus_sans_balise_orpheline(nom):
    f = BIBLIOTHEQUE[nom]
    contexte = {k: v["example"] for k, v in f.slots.items()}
    contexte["id"] = nom
    rendu = al.rendre(f.arbre, [contexte])
    assert al.RE_RESTE.findall(rendu) == []
    assert rendu.count(f"<!-- section:{nom} -->") == 1 and rendu.count(f"<!-- /section:{nom} -->") == 1
    assert f'id="{nom}"' in rendu
    if f.region == "main":
        assert f'aria-labelledby="{nom}-titre"' in rendu and f'id="{nom}-titre"' in rendu


@pytest.mark.parametrize("nom", NOMS)
def test_titres_sans_virgule_ni_point(nom):
    """Les exemples de titres (h1 à h4) ne portent ni virgule ni point final."""
    f = BIBLIOTHEQUE[nom]
    contexte = {k: v["example"] for k, v in f.slots.items()}
    contexte["id"] = nom
    rendu = al.rendre(f.arbre, [contexte])
    for titre in re.findall(r"<h([1-4])[^>]*>(.*?)</h\1>", rendu, re.S):
        texte = re.sub(r"<span class=\"sr-only\">.*?</span>", "", titre[1])
        texte = re.sub(r"<[^>]+>", " ", texte).strip()
        assert "," not in texte, f"{nom} : virgule dans « {texte} »"
        assert not texte.endswith("."), f"{nom} : point final dans « {texte} »"


@pytest.mark.parametrize("nom", NOMS)
def test_aucune_couleur_en_dur_ni_pastille(nom):
    f = BIBLIOTHEQUE[nom]
    assert RE_COULEUR.findall(f.style) == [], f"{nom} : couleur en dur dans le style"
    assert "eyebrow" not in f.balisage.lower() and "eyebrow" not in f.style.lower()
    assert "—" not in f.chemin.read_text(encoding="utf-8"), f"{nom} : tiret cadratin"


def test_assets_sans_couleur_en_dur():
    for nom in ("base.css", "catalogue.css"):
        css = (ASSETS / nom).read_text(encoding="utf-8")
        assert RE_COULEUR.findall(css) == [], nom


@pytest.mark.parametrize("nom", CONVERSION)
def test_cta_primaire_pilote_par_slot(nom):
    f = BIBLIOTHEQUE[nom]
    par_plan = (f.slots.get("plans") or {}).get("fields", {})
    assert "primary" in f.slots or "primary" in par_plan
    assert '{{#primary}} data-cta="primaire"{{/primary}}' in f.balisage


# Variables écrites par les moteurs ou en style en ligne, jamais déclarées en CSS.
VARIABLES_DYNAMIQUES = {"--p", "--q", "--steps", "--rail", "--read", "--exit", "--enter", "--rv-i",
                        "--i", "--n", "--k", "--v", "--w", "--at", "--cols", "--rx", "--ry"}
RE_DECLARATION = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
RE_LECTURE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(,)?")


def test_variables_lues_toutes_declarees():
    """Toute variable lue sans repli par base.css ou une section existe quelque part."""
    sources = [(ASSETS / n).read_text(encoding="utf-8") for n in ("tokens.css", "base.css", "catalogue.css")]
    sources += [f.style + f.balisage for f in BIBLIOTHEQUE.values()]
    sources = [re.sub(r"/\*.*?\*/", "", s, flags=re.S) for s in sources]
    declarees = set().union(*(RE_DECLARATION.findall(s) for s in sources))
    lues = set().union(*({n for n, repli in RE_LECTURE.findall(s) if not repli} for s in sources))
    assert sorted(lues - declarees - VARIABLES_DYNAMIQUES) == []


def test_moteurs_declares_existent():
    for nom in al.ENGINES:
        assert (ASSETS / f"{nom}.js").is_file()


# --------------------------------------------------------------------------
# Assemblage
# --------------------------------------------------------------------------

def spec_minimale(**autres) -> dict:
    base = {"title": "Page de test", "page": "test", "samples": True,
            "sections": [{"use": "topbar"}, {"use": "hero"}, {"use": "final-cta", "id": "final"},
                         {"use": "footer"}]}
    base.update(autres)
    return base


def test_assemblage_structure_de_page():
    html = al.assembler(spec_minimale()).html
    assert html.startswith("<!DOCTYPE html>") and '<html lang="fr">' in html
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html
    assert html.index('class="s-topbar"') < html.index('<main id="contenu">') < \
        html.index('class="s-hero') < html.index("</main>") < html.index('class="s-footer"')
    for sid in ("topbar", "hero", "final", "footer"):
        assert html.count(f"<!-- section:{sid} -->") == 1
    assert 'class="skip-link" href="#contenu"' in html
    assert 'window.LANDING_CONFIG = {"page": "test"' in html
    assert "window.dataLayer = window.dataLayer || [];" in html
    assert "/* ---- reveal.js ---- */" in html and "/* ---- tracking.js ---- */" in html
    assert "/* ---- scroll.js ---- */" not in html
    assert al.RE_GENERATEUR.search(html)


def test_avertissement_pour_chaque_slot_non_rempli():
    resultat = al.assembler({"title": "T", "sections": [{"use": "hero", "slots": {"title": "Mon titre"}}]})
    manquants = [a for a in resultat.avertissements if "non rempli" in a]
    assert len(manquants) == len(BIBLIOTHEQUE["hero"].slots) - 1
    assert not any("« title »" in a for a in manquants)


def test_samples_et_slot_inconnu():
    resultat = al.assembler(spec_minimale(sections=[{"use": "hero", "slots": {"titre": "x"}}]))
    assert resultat.avertissements == ["hero (hero) : slot « titre » inconnu du fragment hero (ignoré)"]


def test_valeurs_echappees_dans_la_page():
    html = al.assembler(spec_minimale(sections=[{"use": "hero", "slots": {"lede": "<script>alert(1)</script>"}}])).html
    assert "<script>alert(1)</script>" not in html and "&lt;script&gt;alert(1)&lt;/script&gt;" in html


@pytest.mark.parametrize("sections, motif", [
    ([{"use": "hero"}, {"use": "hero"}], "en double"),
    ([{"use": "hero", "id": "Hero 1"}], "invalide"),
    ([{"use": "inconnu"}], "introuvable"),
    ([{"id": "x"}], "use"),
])
def test_plans_invalides(sections, motif):
    with pytest.raises(al.ErreurAssemblage, match=motif):
        al.assembler(spec_minimale(sections=sections))


def test_meme_fragment_deux_fois_style_et_script_uniques():
    html = al.assembler(spec_minimale(sections=[
        {"use": "faq"}, {"use": "faq", "id": "faq-2"}])).html
    assert html.count("/* ---- section : faq ---- */") == 2   # une fois dans <style>, une fois dans <script>
    assert html.count('data-section="faq"') == 2


def test_sections_gated_enveloppees_et_noscript():
    html = al.assembler(spec_minimale(sections=[
        {"use": "hero"}, {"use": "choice-gate"}, {"use": "benefits", "gated": True},
        {"use": "faq", "gated": True}, {"use": "final-cta"}])).html
    assert html.count('<div class="gated" data-gated hidden>') == 1
    assert html.index("data-gated hidden") < html.index('data-section="benefits"') < \
        html.index('data-section="faq"') < html.index("</div>\n<!-- section:final-cta -->")
    assert "[data-gated][hidden]{display:block !important}" in html


def test_gated_sans_porte_signale():
    resultat = al.assembler(spec_minimale(sections=[{"use": "hero"}, {"use": "faq", "gated": True}]))
    assert any("porte de choix" in a for a in resultat.avertissements)


def test_moteurs_selon_les_sections():
    html = al.assembler(spec_minimale(sections=[{"use": "journey"}, {"use": "offer-ticket", "id": "offre"},
                                                {"use": "lead-capture"}])).html
    for moteur in ("reveal.js", "scroll.js", "offer.js", "forms.js", "tracking.js"):
        assert f"/* ---- {moteur} ---- */" in html


@pytest.mark.parametrize("mode, present, absent", [
    ("off", [], ["window.dataLayer = window.dataLayer"]),
    ("gtag", ["googletagmanager.com/gtag/js?id=G-TEST123", "gtag('config', 'G-TEST123')"], []),
    ("gtm", ["googletagmanager.com/gtm.js?id=", "'GTM-TEST'"], []),
])
def test_modes_de_suivi(mode, present, absent):
    html = al.assembler(spec_minimale(tracking={"mode": mode, "ga4": "G-TEST123", "gtm": "GTM-TEST"})).html
    for motif in present:
        assert motif in html
    for motif in absent:
        assert motif not in html


def test_assets_en_liens_relatifs(tmp_path):
    sortie = tmp_path / "landing-pages" / "demo" / "index.html"
    html = al.assembler(spec_minimale(assets="link"), sortie=sortie).html
    assert '<link rel="stylesheet" href="' in html and "base.css" in html
    assert re.search(r'<script src="[^"]*reveal\.js"></script>', html)
    assert "/* ---- base.css ---- */" not in html


def test_section_sur_mesure_inseree_telle_quelle(tmp_path):
    """Un fragment de builder (pilotage/sections/…) entre tel quel entre ses marqueurs."""
    (tmp_path / "sections").mkdir()
    (tmp_path / "sections" / "05-demo.html").write_text(
        '<section id="demo" aria-labelledby="demo-titre"><h2 id="demo-titre">Démo</h2>'
        '<style>#demo h2 { margin: 0; }</style></section>', encoding="utf-8")
    spec = spec_minimale(sections=[{"use": "hero"}, {"file": "sections/05-demo.html", "id": "demo"}])
    resultat = al.assembler(spec, spec_dir=tmp_path)
    assert resultat.avertissements == []
    assert '<!-- section:demo -->\n<section id="demo"' in resultat.html
    assert "#demo h2 { margin: 0; }" in resultat.html


@pytest.mark.parametrize("entree, motif", [
    ({"file": "sections/x.html"}, "id"),
    ({"file": "sections/absent.html", "id": "x"}, "introuvable"),
    ({"file": "sections/x.html", "id": "x", "use": "hero"}, "exclusifs"),
])
def test_section_sur_mesure_invalide(tmp_path, entree, motif):
    (tmp_path / "sections").mkdir()
    (tmp_path / "sections" / "x.html").write_text('<section id="x"></section>', encoding="utf-8")
    with pytest.raises(al.ErreurAssemblage, match=motif):
        al.assembler(spec_minimale(sections=[entree]), spec_dir=tmp_path)


def test_section_provisoire_hors_catalogue():
    assert "_placeholder" not in BIBLIOTHEQUE
    html = al.assembler(spec_minimale(sections=[{"use": "hero"}, {"use": "_placeholder", "id": "a-venir"}])).html
    assert '<section id="a-venir" class="s-placeholder section"' in html


def test_annotations_catalogue():
    html = al.assembler(spec_minimale(annotate=True, intro={"title": "Cat", "text": "Texte"})).html
    assert html.count('class="lib-note"') == 4
    assert '<nav class="lib-intro__toc"' in html and "/* ---- catalogue.css ---- */" in html


# --------------------------------------------------------------------------
# Spec et ligne de commande (tmp_path seulement)
# --------------------------------------------------------------------------

def ecrire_spec(tmp_path: Path, spec: dict, nom: str = "spec.json") -> Path:
    chemin = tmp_path / nom
    chemin.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return chemin


def test_spec_json_invalide_ou_incomplete(tmp_path):
    with pytest.raises(al.ErreurAssemblage, match="title"):
        al.lire_spec(ecrire_spec(tmp_path, {"sections": [{"use": "hero"}]}))
    with pytest.raises(al.ErreurAssemblage, match="sections"):
        al.lire_spec(ecrire_spec(tmp_path, {"title": "T", "sections": []}))
    autre = tmp_path / "spec.txt"
    autre.write_text("title: x", encoding="utf-8")
    with pytest.raises(al.ErreurAssemblage, match="format"):
        al.lire_spec(autre)


def test_spec_markdown_front_matter(tmp_path):
    pytest.importorskip("yaml")
    chemin = tmp_path / "page.md"
    chemin.write_text("---\ntitle: Page\nsamples: true\nsections:\n  - use: hero\n    slots:\n"
                      "      title: Un titre\n---\n\nNotes libres.\n", encoding="utf-8")
    spec = al.lire_spec(chemin)
    assert spec["sections"][0]["slots"]["title"] == "Un titre"
    sans = tmp_path / "vide.md"
    sans.write_text("# rien\n", encoding="utf-8")
    with pytest.raises(al.ErreurAssemblage, match="front matter"):
        al.lire_spec(sans)


def test_cli_ecrit_puis_check(tmp_path):
    spec = ecrire_spec(tmp_path, spec_minimale())
    sortie = tmp_path / "out" / "index.html"
    r = run(str(spec), "-o", str(sortie))
    assert r.returncode == 0, r.stderr
    assert sortie.is_file()
    assert run(str(spec), "-o", str(sortie), "--check").returncode == 0
    ecrire_spec(tmp_path, spec_minimale(title="Autre titre"))
    assert run(str(spec), "-o", str(sortie), "--check").returncode == 1


def test_cli_refuse_un_dossier_pilotage(tmp_path):
    spec = ecrire_spec(tmp_path, spec_minimale())
    sortie = tmp_path / "landing-pages" / "demo" / "pilotage" / "index.html"
    r = run(str(spec), "-o", str(sortie))
    assert r.returncode == 2 and "pilotage" in r.stderr
    assert not sortie.parent.exists()


def test_cli_refuse_une_page_retouchee_ou_etrangere(tmp_path):
    spec = ecrire_spec(tmp_path, spec_minimale())
    sortie = tmp_path / "index.html"
    sortie.write_text("<!DOCTYPE html><p>page écrite à la main</p>", encoding="utf-8")
    r = run(str(spec), "-o", str(sortie))
    assert r.returncode == 2 and "--force" in r.stderr
    assert "écrite à la main" in sortie.read_text(encoding="utf-8")
    assert run(str(spec), "-o", str(sortie), "--force").returncode == 0
    # assemblée puis retouchée : refus, la retouche reste
    texte = sortie.read_text(encoding="utf-8").replace("Page de test", "Page retouchée", 1)
    sortie.write_text(texte, encoding="utf-8")
    ecrire_spec(tmp_path, spec_minimale(title="Nouveau titre"))
    r = run(str(spec), "-o", str(sortie))
    assert r.returncode == 2 and "modifié à la main" in r.stderr
    assert "Page retouchée" in sortie.read_text(encoding="utf-8")


def test_cli_strict_n_ecrit_rien(tmp_path):
    spec = ecrire_spec(tmp_path, {"title": "T", "sections": [{"use": "hero"}]})
    sortie = tmp_path / "index.html"
    r = run(str(spec), "-o", str(sortie), "--strict")
    assert r.returncode == 1 and not sortie.exists()
    assert "non rempli" in r.stderr


def test_cli_list_et_describe():
    r = run("--list")
    assert r.returncode == 0 and "offer-ticket" in r.stdout
    r = run("--describe", "offer-ticket")
    assert r.returncode == 0 and "formulas (list)" in r.stdout
    assert run("--describe", "inconnu").returncode == 2


def test_empreinte():
    html = al.assembler(spec_minimale()).html
    assert al.empreinte_valide(html) is True
    assert al.empreinte_valide(html.replace("Page de test", "Autre", 1)) is False
    assert al.empreinte_valide("<html></html>") is None


def test_catalogue_a_jour():
    """catalogue.html est exactement ce que produit catalogue.json avec les fragments actuels."""
    r = run("05-web-content/templates/sections/catalogue.json", "--check")
    assert r.returncode == 0, r.stdout + r.stderr


# --------------------------------------------------------------------------
# Rendu réel (Chromium)
# --------------------------------------------------------------------------

def _navigateur():
    playwright = pytest.importorskip("playwright.sync_api")
    try:
        p = playwright.sync_playwright().start()
        navigateur = p.chromium.launch()
    except Exception as err:  # navigateur absent
        pytest.skip(f"Chromium indisponible : {err}")
    return p, navigateur


@pytest.fixture(scope="module")
def chromium():
    p, navigateur = _navigateur()
    yield navigateur
    navigateur.close()
    p.stop()


def page_assemblee(tmp_path: Path, **autres) -> str:
    sortie = tmp_path / "index.html"
    spec = spec_minimale(sections=[{"use": "topbar"}, {"use": "hero"}, {"use": "benefits"},
                                   {"use": "choice-gate"},
                                   {"use": "offer-ticket", "id": "offre", "slots": {
                                       "action": "https://shop.example.com/checkout",
                                       "action_waitlist": "https://shop.example.com/waitlist"}},
                                   {"use": "footer"}], **autres)
    sortie.write_text(al.assembler(spec, sortie=sortie).html, encoding="utf-8")
    return sortie.as_uri()


def test_clic_cta_et_choix_mesures(chromium, tmp_path):
    page = chromium.new_page(viewport={"width": 1280, "height": 900})
    page.goto(page_assemblee(tmp_path) + "?utm_source=newsletter")
    page.wait_for_timeout(300)
    page.evaluate("document.addEventListener('click', e => e.preventDefault(), true)")
    page.click("#hero a[data-cta]")
    page.click('[data-gate-choice="equipe"]')
    evenements = page.evaluate("window.dataLayer.filter(e => e.event).map(e => [e.event, e.cta_position || e.content_id, e.utm_source])")
    assert ["cta_click", "hero", "newsletter"] in evenements
    assert ["select_content", "equipe", "newsletter"] in evenements
    assert page.evaluate("document.querySelector('#offre-billet input[name=formule]:checked').value") == "equipe"
    assert page.evaluate("document.querySelector('#offre-billet input[name=utm_source]').value") == "newsletter"
    page.close()


def test_mouvement_reduit_tout_visible(chromium, tmp_path):
    contexte = chromium.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
    page = contexte.new_page()
    page.goto(page_assemblee(tmp_path))
    page.wait_for_timeout(300)
    assert page.evaluate("document.documentElement.classList.contains('rv-on')") is False
    masques = page.evaluate("Array.from(document.querySelectorAll('[data-reveal]')).filter(e => getComputedStyle(e).opacity === '0').length")
    assert masques == 0
    contexte.close()


def test_etat_de_l_offre_calcule_dans_le_navigateur(chromium, tmp_path):
    page = chromium.new_page()
    page.goto(page_assemblee(tmp_path, offer={"state": "open", "closes_at": "2020-01-01T00:00:00Z"}))
    page.wait_for_timeout(300)
    assert page.evaluate("document.documentElement.dataset.offerState") == "waitlist"
    bouton = page.evaluate("document.querySelector('#offre-billet button[type=submit]').textContent.trim()")
    assert bouton == BIBLIOTHEQUE["offer-ticket"].slots["cta_waitlist"]["example"]
    assert page.evaluate("document.querySelector('#offre-billet').getAttribute('action')") == \
        "https://shop.example.com/waitlist"
    page.close()

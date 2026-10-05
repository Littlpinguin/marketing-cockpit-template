"""Tests de 06-graphic-design/scripts/genmeta.py (provenance des images générées).

Aucun appel réseau, aucune génération : tout se joue sur des fichiers jetables
écrits dans `tmp_path`. Les fichiers réels du dépôt ne sont jamais touchés.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MODULE = REPO / "06-graphic-design" / "scripts" / "genmeta.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("genmeta", MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


genmeta = _load_module()

def ecrire_png(chemin: Path) -> Path:
    """Un vrai PNG minimal, écrit par PIL pour rester lisible par PIL."""
    from PIL import Image

    chemin.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (4, 4), (30, 64, 175)).save(chemin, format="PNG")
    return chemin


def ecrire_jpeg(chemin: Path) -> Path:
    """Un vrai JPEG, quel que soit le nom qu'on lui donne."""
    from PIL import Image

    chemin.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (4, 4), (245, 158, 11)).save(chemin, format="JPEG")
    return chemin


META = {
    "model": "gemini-3-pro-image-preview",
    "prompt": "Une scène de marque fictive, fond clair, trait bleu nuit",
    "prompt_file": "06-graphic-design/prompts/exemple.md",
    "input_images": ["06-graphic-design/outputs/reference.jpg"],
    "temperature": 0.4,
    "aspect_ratio": "3:4",
    "image_size": "2K",
    "script": "generation-exemple.py",
}


# --- Sidecar -----------------------------------------------------------------

def test_sidecar_ecrit_puis_relu(tmp_path):
    img = ecrire_png(tmp_path / "visuel.png")
    genmeta.write_sidecar(img, META)
    relu = genmeta.read_sidecar(img)
    assert relu["model"] == META["model"]
    assert relu["prompt"] == META["prompt"]
    assert relu["input_images"] == META["input_images"]
    assert relu["temperature"] == 0.4


def test_sidecar_porte_toutes_les_cles_attendues(tmp_path):
    img = ecrire_png(tmp_path / "visuel.png")
    genmeta.write_sidecar(img, {"model": "m", "prompt": "p"})
    relu = genmeta.read_sidecar(img)
    for cle in ("model", "prompt", "prompt_file", "input_images", "temperature",
                "aspect_ratio", "image_size", "timestamp", "script",
                "script_version", "sha256"):
        assert cle in relu, f"clé absente du sidecar : {cle}"


def test_sidecar_est_ecrit_a_cote_de_l_image(tmp_path):
    img = ecrire_png(tmp_path / "visuel.png")
    chemin = genmeta.write_sidecar(img, META)
    assert chemin == tmp_path / "visuel.png.gen.json"
    assert chemin.exists()
    assert json.loads(chemin.read_text(encoding="utf-8"))["script"] == "generation-exemple.py"


def test_sha256_correspond_aux_octets_de_l_image(tmp_path):
    import hashlib

    img = ecrire_png(tmp_path / "visuel.png")
    genmeta.write_sidecar(img, META)
    attendu = hashlib.sha256(img.read_bytes()).hexdigest()
    assert genmeta.read_sidecar(img)["sha256"] == attendu


def test_timestamp_iso_porte_un_fuseau(tmp_path):
    import datetime

    img = ecrire_png(tmp_path / "visuel.png")
    genmeta.write_sidecar(img, META)
    horodatage = genmeta.read_sidecar(img)["timestamp"]
    assert datetime.datetime.fromisoformat(horodatage).tzinfo is not None


def test_sidecar_absent_retourne_none(tmp_path):
    img = ecrire_png(tmp_path / "visuel.png")
    assert genmeta.read_sidecar(img) is None


def test_sidecar_illisible_retourne_none(tmp_path):
    img = ecrire_png(tmp_path / "visuel.png")
    genmeta.sidecar_path(img).write_text("{ pas du json", encoding="utf-8")
    assert genmeta.read_sidecar(img) is None


# --- Extension réelle --------------------------------------------------------

def test_jpeg_deguise_en_png_est_renomme(tmp_path):
    menteur = ecrire_jpeg(tmp_path / "visuel.png")
    final = genmeta.fix_extension(menteur)
    assert final == tmp_path / "visuel.jpg"
    assert final.exists()
    assert not menteur.exists()


def test_le_renommage_ne_touche_pas_aux_octets(tmp_path):
    menteur = ecrire_jpeg(tmp_path / "visuel.png")
    avant = menteur.read_bytes()
    final = genmeta.fix_extension(menteur)
    assert final.read_bytes() == avant, "fix_extension ne doit jamais réencoder les pixels"


def test_png_reel_reste_en_place(tmp_path):
    img = ecrire_png(tmp_path / "visuel.png")
    avant = img.read_bytes()
    assert genmeta.fix_extension(img) == img
    assert img.read_bytes() == avant


def test_extension_jpeg_acceptee_telle_quelle(tmp_path):
    img = ecrire_jpeg(tmp_path / "visuel.jpeg")
    assert genmeta.fix_extension(img) == img


def test_webp_deguise_en_png_est_renomme(tmp_path):
    from PIL import Image

    menteur = tmp_path / "visuel.png"
    Image.new("RGB", (4, 4), (16, 185, 129)).save(menteur, format="WEBP")
    assert genmeta.fix_extension(menteur) == tmp_path / "visuel.webp"


def test_le_sidecar_suit_le_renommage(tmp_path):
    menteur = ecrire_jpeg(tmp_path / "visuel.png")
    genmeta.write_sidecar(menteur, META)
    final = genmeta.fix_extension(menteur)
    assert genmeta.read_sidecar(final)["model"] == META["model"]
    assert not genmeta.sidecar_path(menteur).exists()


def test_pas_de_renommage_si_la_destination_est_occupee(tmp_path):
    occupant = ecrire_jpeg(tmp_path / "visuel.jpg")
    menteur = ecrire_jpeg(tmp_path / "visuel.png")
    assert genmeta.fix_extension(menteur) == menteur, "aucun écrasement silencieux"
    assert menteur.exists() and occupant.exists()


def test_format_inconnu_laisse_le_fichier_tranquille(tmp_path):
    svg = tmp_path / "visuel.svg"
    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
    assert genmeta.fix_extension(svg) == svg


def test_detect_format(tmp_path):
    assert genmeta.detect_format(ecrire_png(tmp_path / "a.png")) == "png"
    assert genmeta.detect_format(ecrire_jpeg(tmp_path / "b.bin")) == "jpeg"
    vide = tmp_path / "vide.png"
    vide.write_bytes(b"")
    assert genmeta.detect_format(vide) is None


# --- Manifeste C2PA ----------------------------------------------------------

def test_has_c2pa_vrai_si_la_chaine_est_presente(tmp_path):
    f = tmp_path / "signe.jpg"
    f.write_bytes(b"\xff\xd8\xff" + b"\x00" * 64 + b"jumdc2pa" + b"\x00" * 64)
    assert genmeta.has_c2pa(f) is True


def test_has_c2pa_faux_sur_une_image_nue(tmp_path):
    assert genmeta.has_c2pa(ecrire_png(tmp_path / "nu.png")) is False


def test_has_c2pa_trouve_la_chaine_a_cheval_sur_deux_blocs(tmp_path):
    f = tmp_path / "gros.bin"
    bloc = genmeta.CHUNK
    f.write_bytes(b"\x00" * (bloc - 2) + b"c2pa" + b"\x00" * 32)
    assert genmeta.has_c2pa(f) is True


# --- Tag tEXt ----------------------------------------------------------------

def test_tag_png_relu_par_pil(tmp_path):
    from PIL import Image

    img = ecrire_png(tmp_path / "visuel.png")
    assert genmeta.tag_png(img, genmeta.TAG_KEY, "gemini-3-pro-image-preview") is True
    with Image.open(img) as im:
        assert im.text[genmeta.TAG_KEY] == "gemini-3-pro-image-preview"


def test_tag_png_conserve_les_tags_deja_presents(tmp_path):
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo

    img = tmp_path / "visuel.png"
    info = PngInfo()
    info.add_text("Software", "Fictive Studio")
    Image.new("RGB", (4, 4), (248, 250, 252)).save(img, format="PNG", pnginfo=info)

    genmeta.tag_png(img, genmeta.TAG_KEY, "modele-x")
    with Image.open(img) as im:
        assert im.text["Software"] == "Fictive Studio"
        assert im.text[genmeta.TAG_KEY] == "modele-x"


def test_tag_png_preserve_les_pixels(tmp_path):
    from PIL import Image

    img = ecrire_png(tmp_path / "visuel.png")
    with Image.open(img) as im:
        avant = im.convert("RGB").tobytes()
    genmeta.tag_png(img, genmeta.TAG_KEY, "modele-x")
    with Image.open(img) as im:
        assert im.convert("RGB").tobytes() == avant


def test_tag_png_refuse_un_jpeg_sans_y_toucher(tmp_path):
    jpg = ecrire_jpeg(tmp_path / "visuel.jpg")
    avant = jpg.read_bytes()
    assert genmeta.tag_png(jpg, genmeta.TAG_KEY, "modele-x") is False
    assert jpg.read_bytes() == avant


# --- Enchaînement complet ----------------------------------------------------

def test_finalize_output_renomme_et_documente(tmp_path):
    menteur = ecrire_jpeg(tmp_path / "visuel.png")
    final = genmeta.finalize_output(menteur, META)
    assert final == tmp_path / "visuel.jpg"
    assert genmeta.read_sidecar(final)["model"] == META["model"]
    assert genmeta.read_sidecar(final)["sha256"]


def test_finalize_output_pose_le_tag_sur_un_png(tmp_path):
    from PIL import Image

    img = ecrire_png(tmp_path / "visuel.png")
    final = genmeta.finalize_output(img, META)
    assert final == img
    with Image.open(final) as im:
        assert im.text[genmeta.TAG_KEY] == META["model"]
    assert genmeta.read_sidecar(final)["sha256"], "le sha256 suit le fichier taggé"


def test_finalize_output_sha256_calcule_apres_le_tag(tmp_path):
    import hashlib

    img = ecrire_png(tmp_path / "visuel.png")
    final = genmeta.finalize_output(img, META)
    attendu = hashlib.sha256(final.read_bytes()).hexdigest()
    assert genmeta.read_sidecar(final)["sha256"] == attendu


# --- Extrait de prompt pour les fiches ---------------------------------------

def test_extrait_de_prompt_tient_sur_une_ligne(tmp_path):
    extrait = genmeta.prompt_excerpt("Première ligne\nDeuxième ligne\n\nTroisième")
    assert "\n" not in extrait
    assert extrait == "Première ligne Deuxième ligne Troisième"


def test_extrait_de_prompt_est_coupe_a_120_caracteres():
    extrait = genmeta.prompt_excerpt("a" * 400)
    assert extrait.startswith("a" * 120)
    assert len(extrait) <= 121


def test_extrait_de_prompt_sans_tiret_long():
    extrait = genmeta.prompt_excerpt("Un style maison — chaleureux – et net")
    assert "—" not in extrait and "–" not in extrait


def test_extrait_de_prompt_vide():
    assert genmeta.prompt_excerpt(None) == ""
    assert genmeta.prompt_excerpt("   ") == ""


# --- Garde C2PA sur les PNG ---------------------------------------------------

def ecrire_png_signe(chemin: Path) -> Path:
    """Un PNG qui porte un marqueur `c2pa`, comme certaines sorties du modèle."""
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()
    info.add_text("c2pa", "manifeste simulé")
    Image.new("RGB", (4, 4), (15, 23, 42)).save(chemin, format="PNG", pnginfo=info)
    return chemin


def test_finalize_output_ne_tague_pas_un_png_signe(tmp_path, capsys):
    """PIL resauvegarde et jette les chunks qu'il ne connaît pas : taguer un PNG
    signé détruirait son manifeste. On préfère le manifeste au tag."""
    img = ecrire_png_signe(tmp_path / "signe.png")
    avant = img.read_bytes()
    final = genmeta.finalize_output(img, META)
    assert final.read_bytes() == avant, "un PNG signé ne doit pas être resauvegardé"
    assert "C2PA" in capsys.readouterr().err


def test_finalize_output_documente_quand_meme_un_png_signe(tmp_path):
    img = ecrire_png_signe(tmp_path / "signe.png")
    genmeta.finalize_output(img, META)
    assert genmeta.read_sidecar(img)["model"] == META["model"]


def test_finalize_output_ecrit_le_sidecar_meme_si_le_tag_echoue(tmp_path, capsys):
    """PNG tronqué : PIL échoue, la provenance doit tout de même être déposée."""
    casse = tmp_path / "casse.png"
    casse.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32)
    final = genmeta.finalize_output(casse, META)
    assert genmeta.read_sidecar(final)["model"] == META["model"]
    assert "tag" in capsys.readouterr().err.lower()


# --- Avertissements de fix_extension -----------------------------------------

def test_fix_extension_avertit_si_la_cible_est_occupee(tmp_path, capsys):
    ecrire_jpeg(tmp_path / "visuel.jpg")
    menteur = ecrire_jpeg(tmp_path / "visuel.png")
    assert genmeta.fix_extension(menteur) == menteur
    erreurs = capsys.readouterr().err
    assert "visuel.jpg" in erreurs and "occup" in erreurs.lower()


# --- Recherche d'une sortie déjà produite ------------------------------------

def test_existing_variant_trouve_le_meme_radical_sous_une_autre_extension(tmp_path):
    deja = ecrire_jpeg(tmp_path / "portrait-a.jpg")
    assert genmeta.existing_variant(tmp_path / "portrait-a.png") == deja


def test_existing_variant_prefere_le_chemin_demande(tmp_path):
    demande = ecrire_png(tmp_path / "portrait-a.png")
    ecrire_jpeg(tmp_path / "portrait-a.jpg")
    assert genmeta.existing_variant(demande) == demande


def test_existing_variant_rien_a_trouver(tmp_path):
    assert genmeta.existing_variant(tmp_path / "portrait-a.png") is None

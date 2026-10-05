#!/usr/bin/env python3
"""Provenance des images générées : fiche de génération, extension réelle, tag PNG.

Un visuel sorti d'un modèle sans rien autour est un fichier muet : six mois plus
tard, personne ne sait avec quel modèle ni depuis quel prompt il a été fabriqué.
Ce module donne aux scripts de génération et à `promote-asset.py` trois gestes :

1. `write_sidecar` / `read_sidecar` : une fiche `<image>.gen.json` posée à côté de
   l'image, qui garde le modèle, le prompt intégral, les images d'entrée, les
   réglages, l'horodatage et l'empreinte sha256 du fichier.
2. `fix_extension` : l'API renvoie parfois du JPEG sous un nom `.png`. La
   fonction lit les octets, et si l'extension ment, elle RENOMME. Elle ne
   convertit jamais les pixels : un JPEG réencodé en PNG perdrait son manifeste
   C2PA et gagnerait du poids pour rien.
3. `tag_png` / `has_c2pa` : marquage et détection de provenance dans le fichier
   lui-même.

Ce que la provenance survit ou ne survit pas est documenté dans la skill
`image-generation`, sous-section « Provenance ».

Ce module ne fait aucun appel réseau et ne génère rien.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys
from pathlib import Path

SCRIPT_VERSION = "1.0"
SIDECAR_SUFFIX = ".gen.json"
CHUNK = 1 << 20  # 1 Mio, taille de lecture de `has_c2pa`
EXCERPT_LEN = 120  # longueur de l'extrait de prompt posé dans une fiche du catalogue
# Clé du chunk tEXt posé dans les PNG générés. Neutre : elle ne nomme aucune
# marque, et reste lisible par tout outil (`exiftool`, PIL, `pngcheck -t`).
TAG_KEY = "ai:generated_by"

# Ordre des clés du sidecar : les scripts qui le relisent y trouvent toujours la
# même chose, même quand le générateur n'a pas renseigné un réglage.
KEYS = ("model", "prompt", "prompt_file", "input_images", "temperature",
        "aspect_ratio", "image_size", "timestamp", "script", "script_version",
        "sha256")

# Signatures de fichier, lues sur les premiers octets.
MAGIC = {
    "jpeg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
}
# Extensions tolérées par format, la première étant la forme canonique.
EXTENSIONS = {
    "jpeg": (".jpg", ".jpeg"),
    "png": (".png",),
    "webp": (".webp",),
}


def warn(message: str) -> None:
    """Avertissement sur la sortie d'erreur : un module de bibliothèque ne doit
    pas polluer la sortie standard de ses appelants, mais il ne doit rien taire."""
    print(f"⚠ {message}", file=sys.stderr)


# --- Fiche de génération (sidecar) -------------------------------------------

def sidecar_path(image_path) -> Path:
    """Chemin de la fiche de génération d'une image : `<image>.gen.json`."""
    return Path(str(image_path) + SIDECAR_SUFFIX)


def sha256_file(path) -> str:
    """Empreinte sha256 des octets du fichier, lue par blocs."""
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for bloc in iter(lambda: f.read(CHUNK), b""):
            digest.update(bloc)
    return digest.hexdigest()


def write_sidecar(image_path, meta: dict) -> Path:
    """Écrit `<image>.gen.json` et renvoie son chemin.

    `timestamp`, `script_version` et `sha256` sont calculés ici si l'appelant ne
    les fournit pas. L'empreinte est celle du fichier tel qu'il est SUR LE DISQUE
    au moment de l'appel : écrire la fiche en dernier, après tout renommage ou
    marquage.
    """
    image_path = Path(image_path)
    fiche = {cle: meta.get(cle) for cle in KEYS}
    fiche["input_images"] = list(meta.get("input_images") or [])
    if not fiche["timestamp"]:
        fiche["timestamp"] = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
    if not fiche["script_version"]:
        fiche["script_version"] = SCRIPT_VERSION
    if not fiche["sha256"] and image_path.exists():
        fiche["sha256"] = sha256_file(image_path)
    for cle, valeur in meta.items():  # les clés en plus sont conservées
        fiche.setdefault(cle, valeur)

    chemin = sidecar_path(image_path)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(fiche, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return chemin


def read_sidecar(image_path):
    """Relit la fiche de génération d'une image, ou `None` si elle manque ou si
    elle n'est pas du JSON exploitable (une fiche cassée ne doit jamais faire
    tomber une promotion)."""
    chemin = sidecar_path(image_path)
    if not chemin.exists():
        return None
    try:
        donnees = json.loads(chemin.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None
    return donnees if isinstance(donnees, dict) else None


# --- Extension réelle ---------------------------------------------------------

def detect_format(path):
    """Format réel d'un fichier image d'après ses premiers octets.

    Renvoie `"jpeg"`, `"png"`, `"webp"` ou `None` (format non reconnu, fichier
    vide, SVG, illisible). WebP se reconnaît à `RIFF` puis `WEBP` en octets 8 à 12.
    """
    try:
        with open(path, "rb") as f:
            tete = f.read(16)
    except OSError:
        return None
    for nom, signatures in MAGIC.items():
        if any(tete.startswith(s) for s in signatures):
            return nom
    if tete[:4] == b"RIFF" and tete[8:12] == b"WEBP":
        return "webp"
    return None


def fix_extension(path) -> Path:
    """Renomme le fichier si son extension ment sur son format réel.

    Retourne le chemin final (inchangé si l'extension est juste, si le format
    n'est pas reconnu, ou si la destination est déjà prise : jamais d'écrasement
    silencieux). La fiche de génération éventuelle suit le renommage.

    Les octets ne sont pas touchés : on renomme, on ne convertit pas.
    """
    path = Path(path)
    reel = detect_format(path)
    if reel is None or path.suffix.lower() in EXTENSIONS[reel]:
        return path

    cible = path.with_suffix(EXTENSIONS[reel][0])
    if cible.exists():
        warn(f"{path.name} est un {reel}, mais {cible.name} est déjà occupé : "
             f"le fichier garde son extension trompeuse. Renommer à la main après "
             f"avoir vérifié lequel des deux garder.")
        return path
    path.rename(cible)
    fiche = sidecar_path(path)
    if fiche.exists() and not sidecar_path(cible).exists():
        fiche.rename(sidecar_path(cible))
    return cible


# --- Manifeste C2PA -----------------------------------------------------------

def existing_variant(path):
    """Cherche une sortie déjà produite pour ce radical, quelle que soit son
    extension d'image, et renvoie son chemin (ou `None`).

    Indispensable aux modes batch : `fix_extension` livre souvent un `.jpg` là
    où le script demandait un `.png`, et un garde qui ne teste que le nom demandé
    relancerait une génération facturée à chaque passage.
    """
    path = Path(path)
    if path.exists():
        return path
    for extension in (".png", ".jpg", ".jpeg", ".webp"):
        candidat = path.with_suffix(extension)
        if candidat.exists():
            return candidat
    return None


def has_c2pa(path) -> bool:
    """Vrai si la chaîne `c2pa` apparaît dans les octets du fichier.

    Heuristique assumée : on cherche le marqueur, pas une signature valide. Les
    sorties JPEG de Gemini portent un manifeste C2PA signé par Google
    (`digitalSourceType=trainedAlgorithmicMedia`), et ce marqueur y figure. Un
    faux positif reste possible sur un fichier qui contiendrait ces quatre
    octets par hasard ; pour une vérification réelle, il faut l'outil `c2patool`.
    """
    reste = b""
    try:
        with open(path, "rb") as f:
            for bloc in iter(lambda: f.read(CHUNK), b""):
                if b"c2pa" in reste + bloc:
                    return True
                reste = bloc[-3:]  # la chaîne peut être à cheval sur deux blocs
    except OSError:
        return False
    return False


# --- Marquage PNG -------------------------------------------------------------

def tag_png(path, key: str, value: str) -> bool:
    """Ajoute un chunk `tEXt` à un PNG et le resauvegarde sans perte.

    Renvoie `False` sans toucher au fichier si ce n'est pas un PNG (un JPEG
    resauvegardé par PIL serait réencodé, donc dégradé, et perdrait son
    manifeste C2PA). Les tags déjà présents sont conservés.

    À réserver aux fichiers de staging : un asset déjà promu dans
    `01-brand/assets/` ne se réécrit pas, le tag se pose avant la copie.
    """
    if detect_format(path) != "png":
        return False
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo

    path = Path(path)
    with Image.open(path) as im:
        im.load()
        info = PngInfo()
        for cle, valeur in (im.text or {}).items():
            if cle != key:
                info.add_text(cle, valeur)
        info.add_text(key, value)
        im.save(path, format="PNG", pnginfo=info)
    return True


# --- Enchaînement pour les scripts de génération ------------------------------

def finalize_output(image_path, meta: dict) -> Path:
    """Geste complet après l'écriture des octets renvoyés par le modèle.

    Remet l'extension d'aplomb, pose le tag `ai:generated_by` si le fichier est
    un PNG, puis écrit la fiche de génération (en dernier, pour que le sha256
    corresponde au fichier livré). Renvoie le chemin final.
    """
    chemin = fix_extension(image_path)
    modele = meta.get("model")
    if modele and detect_format(chemin) == "png":
        if has_c2pa(chemin):
            # PIL resauvegarde le PNG et jette les chunks qu'il ne connaît pas :
            # poser le tag effacerait le manifeste, qui vaut mieux que le tag.
            warn(f"{chemin.name} porte un manifeste C2PA : tag non posé "
                 f"(la resauvegarde PNG l'effacerait). La fiche de génération "
                 f"garde la provenance.")
        else:
            try:
                tag_png(chemin, TAG_KEY, str(modele))
            except Exception as erreur:  # PIL absent, PNG tronqué, disque plein…
                warn(f"tag {TAG_KEY} non posé sur {chemin.name} ({erreur}). "
                     f"La fiche de génération est écrite quand même.")
    write_sidecar(chemin, meta)
    return chemin


# --- Extrait de prompt pour une fiche du catalogue ----------------------------

def prompt_excerpt(prompt, longueur: int = EXCERPT_LEN) -> str:
    """Réduit un prompt à une ligne courte, posable dans `01-brand/assets/index.md`.

    Une fiche du catalogue ne tolère ni saut de ligne ni tiret long : les
    premiers sont écrasés en espaces, les seconds en tirets simples. Le prompt
    intégral reste dans la fiche de génération.
    """
    if not prompt:
        return ""
    texte = " ".join(str(prompt).replace("—", "-").replace("–", "-").split())
    if len(texte) <= longueur:
        return texte
    return texte[:longueur] + "…"

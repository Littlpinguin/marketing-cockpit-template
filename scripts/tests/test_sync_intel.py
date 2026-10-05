"""Tests de scripts/sync-intel.py sur des fixtures temporaires (aucun accès au Drive)."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "sync-intel.py"


def fixture(dossier, doc_id, titre, modifie, nom, corps="# notes\ncontenu\n"):
    (dossier / nom).write_text(
        f"---\nsource: drive-transcripts\ndoc_id: {doc_id}\ntitre: {json.dumps(titre, ensure_ascii=False)}\n"
        f"date_reunion: \"2026-09-30 15:32 CEST\"\nlien: https://docs.google.com/document/d/{doc_id}/edit\n"
        f"modifie: {modifie}\nexporte: 2026-10-02T06:00:00Z\n---\n\n{corps}",
        encoding="utf-8",
    )


def run(*args):
    env = {k: v for k, v in os.environ.items() if k != "INTEL_DRIVE_MD_DIR"}
    r = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, env=env)
    return r.returncode, r.stdout


class SyncIntelTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.src, self.intel = base / "src", base / "intel"
        self.src.mkdir()
        (self.intel / "inbox").mkdir(parents=True)
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        (self.src / "_etat.json").write_text(json.dumps({"derniere_execution": now, "erreurs": []}))
        (self.src / "_test.md").write_text("# test")
        fixture(self.src, "AAA111", "Comité projet - 2026/09/30 15:32 CEST - Notes by Gemini",
                "2026-09-30T14:00:00Z", "2026-09-30 1532 Comité projet - Notes by Gemini [AAA111].md")
        fixture(self.src, "BBB222", "Accounting Touchpoint - 2026/07/28 09:30 EDT - Transcript",
                "2026-07-28T14:00:00Z", "2026-07-28 0930 Accounting Touchpoint - Transcript [BBB222].md")
        fixture(self.src, "CCC333", "Café équipe - 2026/09/02 15:32 CEST - Notes by Gemini (French)",
                "2026-09-02T09:00:00Z", "2026-09-02 1532 Café équipe - Notes by Gemini (French) [CCC333].md")
        self.base = ["--source", str(self.src), "--intel", str(self.intel)]

    def tearDown(self):
        for f in self.src.glob("*"):
            f.chmod(0o644)
        self.tmp.cleanup()

    def inbox(self):
        return sorted(p.name for p in (self.intel / "inbox").iterdir())

    def test_dry_run_n_ecrit_rien(self):
        code, out = run(*self.base, "--dry-run")
        self.assertEqual(code, 0)
        self.assertIn("copies=2", out)
        self.assertIn("exclus=1", out)
        self.assertEqual(self.inbox(), [])
        self.assertFalse((self.intel / ".sync-state.json").exists())

    def test_copie_puis_jamais_de_reimport(self):
        code, out = run(*self.base)
        self.assertIn("copies=2", out)
        self.assertIn("alerte=aucune", out)
        # Classement simulé : le fichier quitte l'inbox sous un autre nom.
        classe = self.intel / "interne"
        classe.mkdir()
        nom = next(n for n in self.inbox() if "AAA111" in n)
        (self.intel / "inbox" / nom).rename(classe / "2026-09-30-comite-projet.md")
        code, out = run(*self.base)
        self.assertIn("copies=0", out)
        self.assertIn("deja=2", out)

    def test_fichier_deja_importe_jamais_rouvert(self):
        run(*self.base)
        for f in self.src.glob("*.md"):
            if not f.name.startswith("_"):
                f.chmod(0)  # l'ouvrir lèverait PermissionError
        code, out = run(*self.base)
        self.assertEqual(code, 0, out)
        self.assertIn("copies=0", out)

    def test_note_gemini_vide_ecartee(self):
        fixture(self.src, "EEE555", "Point - 2026/10/01 16:00 CEST - Notes by Gemini (English)",
                "2026-10-01T15:00:00Z", "2026-10-01 1600 Point - Notes by Gemini (English) [EEE555].md",
                corps="### Summary\n\nA summary wasn't produced for this meeting.\n")
        code, out = run(*self.base)
        self.assertIn("vides=1", out)
        self.assertFalse(any("EEE555" in n for n in self.inbox()))
        code, out = run(*self.base)
        self.assertIn("vides=0", out)  # reconnue à son nom au passage suivant

    def test_alertes_de_sante(self):
        (self.src / "_etat.json").write_text(json.dumps({
            "derniere_execution": "2026-01-01T00:00:00Z",
            "erreurs": [{"id": "x", "titre": "Doc", "message": "Drive API 403"}],
        }))
        code, out = run(*self.base)
        self.assertIn("apps-script-silencieux", out)
        self.assertIn("erreurs-export", out)

    def test_premier_passage_vide_ecrit_l_etat(self):
        vide = Path(self.tmp.name) / "vide"
        vide.mkdir()
        code, out = run("--source", str(vide), "--intel", str(self.intel))
        self.assertEqual(code, 0)
        self.assertTrue((self.intel / ".sync-state.json").exists())

    def test_source_absente(self):
        code, out = run("--source", str(Path(self.tmp.name) / "absent"), "--intel", str(self.intel))
        self.assertEqual(code, 2)
        self.assertIn("source-introuvable", out)


if __name__ == "__main__":
    unittest.main()

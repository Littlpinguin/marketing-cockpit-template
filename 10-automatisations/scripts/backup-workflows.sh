#!/usr/bin/env bash
#
# backup-workflows.sh — export quotidien de tous les workflows n8n via l'API.
#
# Usage :
#   N8N_API_URL="https://votre-instance/api/v1" N8N_API_KEY="..." ./backup-workflows.sh
#   ou, plus simple : renseigner N8N_API_URL et N8N_API_KEY dans le .env à la racine
#   du repo, puis planifier en cron :
#     0 3 * * *  cd /chemin/vers/le/repo && ./10-automatisations/scripts/backup-workflows.sh
#
# Variables d'environnement :
#   N8N_API_URL       (requis)  URL de l'API, ex. https://n8n.exemple.com/api/v1
#   N8N_API_KEY       (requis)  clé API n8n (Settings → n8n API)
#   N8N_BACKUP_DIR    (optionnel) dossier de destination
#                     (défaut : <ce module>/backups/<AAAA-MM-JJ>)
#   N8N_BACKUP_KEEP   (optionnel) nombre de jours de backups à conserver (défaut : 30)
#
# Sécurité : les exports contiennent les NOMS et IDs de credentials (jamais les
# secrets eux-mêmes), mais aussi vos emails/IDs de documents en paramètres de
# nodes. Le dossier backups/ est fait pour rester LOCAL — il est gitignoré,
# ne le committez pas.

set -euo pipefail

# --- Charger le .env à la racine du repo s'il existe (sans écraser l'existant) ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
if [[ -z "${N8N_API_URL:-}" || -z "${N8N_API_KEY:-}" ]] && [[ -f "${REPO_ROOT}/.env" ]]; then
  # shellcheck disable=SC1091
  set -a; source "${REPO_ROOT}/.env"; set +a
fi

# --- Vérifications : aucun défaut en dur pour l'instance ni la clé ---
: "${N8N_API_URL:?N8N_API_URL non défini (ex. https://votre-instance/api/v1)}"
: "${N8N_API_KEY:?N8N_API_KEY non défini (Settings → n8n API dans n8n)}"

command -v curl >/dev/null || { echo "ERREUR : curl est requis" >&2; exit 1; }
command -v jq   >/dev/null || { echo "ERREUR : jq est requis (https://jqlang.org)" >&2; exit 1; }

DATE_DIR="$(date +%Y-%m-%d)"
BACKUP_ROOT="${N8N_BACKUP_DIR:-${SCRIPT_DIR}/../backups}"
DEST="${BACKUP_ROOT}/${DATE_DIR}"
KEEP_DAYS="${N8N_BACKUP_KEEP:-30}"
API="${N8N_API_URL%/}"

mkdir -p "${DEST}"

echo "Backup des workflows n8n → ${DEST}"

# --- Récupérer la liste complète (pagination par curseur) ---
cursor=""
count=0
while :; do
  url="${API}/workflows?limit=100"
  [[ -n "${cursor}" ]] && url="${url}&cursor=${cursor}"

  page="$(curl -sS --fail -H "X-N8N-API-KEY: ${N8N_API_KEY}" "${url}")"

  # Sauvegarder chaque workflow de la page dans un fichier dédié
  while IFS=$'\t' read -r id name; do
    [[ -z "${id}" ]] && continue
    # Nom de fichier sûr : slug du nom + id
    slug="$(printf '%s' "${name}" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g' | cut -c1-60)"
    file="${DEST}/${slug:-workflow}--${id}.json"
    curl -sS --fail -H "X-N8N-API-KEY: ${N8N_API_KEY}" "${API}/workflows/${id}" \
      | jq '.' > "${file}"
    count=$((count + 1))
    echo "  ✓ ${name} (${id})"
  done < <(printf '%s' "${page}" | jq -r '.data[] | [.id, .name] | @tsv')

  cursor="$(printf '%s' "${page}" | jq -r '.nextCursor // empty')"
  [[ -z "${cursor}" ]] && break
done

echo "${count} workflow(s) exporté(s) dans ${DEST}"

# --- Rotation : supprimer les dossiers de backup plus vieux que KEEP_DAYS ---
if [[ -d "${BACKUP_ROOT}" ]]; then
  find "${BACKUP_ROOT}" -mindepth 1 -maxdepth 1 -type d -name '20*' -mtime "+${KEEP_DAYS}" \
    -exec rm -rf {} + 2>/dev/null || true
fi

echo "Terminé."

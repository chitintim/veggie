#!/usr/bin/env bash
# One-shot setup: init git in this folder and push to chitintin/veggie.
# Run from inside the Veggie/ directory: bash setup.sh
set -e

REMOTE_HTTPS="https://github.com/chitintin/veggie.git"
REMOTE_SSH="git@github.com:chitintin/veggie.git"

echo "🌱 Setting up Veggie repo at $(pwd)"

if [ -d .git ]; then
  echo "→ git already initialised here, skipping init"
else
  git init -b main
fi

git add .

if git rev-parse --verify HEAD >/dev/null 2>&1; then
  echo "→ commits already exist, adding incremental commit"
  git commit -m "Update HK Veg database + map" || echo "→ nothing to commit"
else
  git commit -m "Initial commit: HK Veg restaurant database + interactive map"
fi

# Add remote if missing
if ! git remote get-url origin >/dev/null 2>&1; then
  # Prefer SSH if a key looks usable, else HTTPS
  if [ -f "$HOME/.ssh/id_ed25519" ] || [ -f "$HOME/.ssh/id_rsa" ]; then
    echo "→ adding SSH remote"
    git remote add origin "$REMOTE_SSH"
  else
    echo "→ adding HTTPS remote"
    git remote add origin "$REMOTE_HTTPS"
  fi
fi

echo "→ pushing to origin/main"
git push -u origin main || {
  echo ""
  echo "❌ Push failed. Common causes:"
  echo "   1. The repo chitintin/veggie doesn't exist yet on GitHub. Create it (empty, no README) at:"
  echo "      https://github.com/new"
  echo "   2. SSH key not added to GitHub. See: https://github.com/settings/keys"
  echo "   3. HTTPS auth needs a personal access token: https://github.com/settings/tokens"
  echo ""
  echo "Once that's sorted, just run:  git push -u origin main"
  exit 1
}

echo ""
echo "✅ Done. Repo pushed to $REMOTE_HTTPS"
echo "   To enable GitHub Pages (so the map is live at chitintin.github.io/veggie):"
echo "   → Settings → Pages → Source: Deploy from branch → main / root → Save"

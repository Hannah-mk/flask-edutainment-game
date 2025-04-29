```bash
#!/usr/bin/env bash
set -euo pipefail

# Ensure script runs from project root
cd "$(dirname "$0")"

# Directories
SRC_ROOT="$(pwd)/game_src"
DEST_ROOT="$(pwd)/static/game/levels"

# Optional: build only specified level (pass folder name under game_src)
if [[ $# -gt 0 ]]; then
  LEVELS=("$1")
else
  # discover all subfolders with main.py
  LEVELS=()
  for d in "$SRC_ROOT"/*; do
    if [[ -f "$d/main.py" ]]; then
      LEVELS+=("$(basename "$d")")
    fi
  done
fi

echo "🚀 Building levels: ${LEVELS[*]}"

# Install pygbag if missing
pip install --no-cache-dir pygbag

for LEVEL_NAME in "${LEVELS[@]}"; do
  ENTRY="$SRC_ROOT/$LEVEL_NAME/main.py"

  if [[ ! -f "$ENTRY" ]]; then
    echo "⚠️  Skip '$LEVEL_NAME': main.py not found."
    continue
  fi

  echo "🛠️  Building level: $LEVEL_NAME"

  # Remove old output folder for this level only
  rm -rf "$DEST_ROOT/$LEVEL_NAME"

  # Build with pygbag directly into level folder
  pygbag --build "$ENTRY" \
         --output "$DEST_ROOT/$LEVEL_NAME/web" \
         --skip-web-build=false

  echo "✅ Level '$LEVEL_NAME' output → $DEST_ROOT/$LEVEL_NAME/web/index.html"
done

echo "🎉 All specified levels built successfully!"
```

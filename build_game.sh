#!/bin/bash

# Define paths
SRC_DIR="game_src"
DEST_DIR="static/game"
BUILD_DIR="build/web"

echo "🚀 Starting Pygbag game build..."

# Step 1: Clean previous builds
echo "🧹 Cleaning old game build..."
rm -rf "$BUILD_DIR"
rm -rf "$DEST_DIR"

# Step 2: Build using pygbag
echo "🛠️ Building game from $SRC_DIR/main.py..."
pygbag --build --archive "$SRC_DIR/main.py"

# Step 3: Move build output to static/game
echo "📦 Moving build to $DEST_DIR..."
mkdir -p "$DEST_DIR"
cp -r "$BUILD_DIR/"* "$DEST_DIR/"

# Step 4: Done
echo "✅ Game build complete! View at /static/game/index.html"

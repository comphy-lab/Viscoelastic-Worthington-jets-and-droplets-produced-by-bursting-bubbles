#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Initialize force_rebuild flag
FORCE_REBUILD=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --force-rebuild)
      FORCE_REBUILD="--force-rebuild"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

git clone https://github.com/comphy-lab/comphy-search.git
mkdir -p .github/assets/js
cp comphy-search/search_db.json .github/assets/js/search_db.json
rm -rf comphy-search

# Define the project root relative to the script location
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
PROJECT_ROOT=$(dirname $(dirname "$SCRIPT_DIR")) # Go two levels up from script dir
DOCS_DIR="$PROJECT_ROOT/docs"
PYTHON_SCRIPT="$PROJECT_ROOT/.github/scripts/generate_docs.py"

echo "Running documentation generation script..."
python3 "$PYTHON_SCRIPT" $FORCE_REBUILD

if [ $? -ne 0 ]; then
    echo "Documentation generation failed."
    exit 1
fi

echo "Documentation generated successfully in $DOCS_DIR"

# Check if docs directory exists
if [ ! -d "$DOCS_DIR" ]; then
    echo "Error: Docs directory '$DOCS_DIR' not found after generation."
    exit 1
fi

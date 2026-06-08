#!/bin/bash

set -euo pipefail

# Create a new GitHub repository under afrogdesign with GitHub CLI.
# Requirements:
# - git
# - gh: https://cli.github.com/
# - gh auth login must be completed before running this file.

OWNER="afrogdesign"

print_error() {
  echo "Error: $1" >&2
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    print_error "'$1' is not installed."
    exit 1
  fi
}

prompt_required() {
  local label="$1"
  local value=""

  while [ -z "$value" ]; do
    printf "%s: " "$label"
    read -r value
    if [ -z "$value" ]; then
      echo "$label cannot be empty."
    fi
  done

  printf "%s" "$value"
}

validate_repo_name() {
  local repo_name="$1"

  if [[ ! "$repo_name" =~ ^[A-Za-z0-9._-]+$ ]]; then
    print_error "Repository name may only contain letters, numbers, dots, underscores, and hyphens."
    exit 1
  fi
}

prompt_visibility() {
  local visibility=""

  while true; do
    printf "Visibility [public/private]: "
    read -r visibility

    case "$visibility" in
      public|private)
        printf "%s" "$visibility"
        return 0
        ;;
      *)
        echo "Please enter 'public' or 'private'."
        ;;
    esac
  done
}

require_command git
require_command gh

if ! gh auth status >/dev/null 2>&1; then
  print_error "GitHub CLI is not authenticated. Run: gh auth login"
  exit 1
fi

echo "Create a new GitHub repository under $OWNER"
echo "-------------------------------------------"

REPO_NAME=$(prompt_required "Repository name")
printf "Description: "
read -r DESCRIPTION
VISIBILITY=$(prompt_visibility)

validate_repo_name "$REPO_NAME"

FULL_REPO="$OWNER/$REPO_NAME"

if gh repo view "$FULL_REPO" >/dev/null 2>&1; then
  print_error "Repository already exists: $FULL_REPO"
  exit 1
fi

if [ -e "$REPO_NAME" ]; then
  print_error "Local path already exists: $REPO_NAME"
  exit 1
fi

mkdir "$REPO_NAME"
cd "$REPO_NAME"

git init -b main
cat > README.md <<EOF
# $REPO_NAME

$DESCRIPTION
EOF

git add README.md
git commit -m "Initial commit"

gh repo create "$FULL_REPO" \
  --description "$DESCRIPTION" \
  --"$VISIBILITY" \
  --source=. \
  --remote=origin \
  --push

echo "Created GitHub repository: https://github.com/$FULL_REPO"

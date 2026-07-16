#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source_root="$(cd "$script_dir/../skills" && pwd)"
target="${1:-${CODEX_HOME:-$HOME/.codex}/skills}"
force="${2:-}"
mkdir -p "$target"
target="$(cd "$target" && pwd)"
timestamp="$(date +%Y%m%d%H%M%S)"

for source in "$source_root"/*; do
  [ -d "$source" ] || continue
  name="$(basename "$source")"
  destination="$target/$name"
  case "$destination" in
    "$target"/*) ;;
    *) echo "Refusing destination outside target root: $destination" >&2; exit 1 ;;
  esac

  if [ -e "$destination" ]; then
    if [ "$force" != "--force" ]; then
      echo "Skill already exists: $destination. Pass --force as the second argument to back it up and replace it." >&2
      exit 1
    fi
    backup="$destination.bak.$timestamp"
    mv "$destination" "$backup"
    echo "Backed up $destination to $backup"
  fi

  cp -R "$source" "$destination"
  echo "Installed $name -> $destination"
done

echo "Agent Preflight installation complete. Restart or reload the agent if required."

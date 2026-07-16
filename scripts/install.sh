#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
target="${CODEX_HOME:-$HOME/.codex}/skills"
if [ "$#" -gt 0 ] && [[ "$1" != --* ]]; then
  target="$1"
  shift
fi

python_command=""
for candidate in python3 python; do
  if command -v "$candidate" >/dev/null 2>&1 \
    && "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 8))' >/dev/null 2>&1; then
    python_command="$candidate"
    break
  fi
done

if [ -n "$python_command" ]; then
  "$python_command" "$script_dir/install.py" --target "$target" "$@"
else
  echo "Python 3.8 or newer is required." >&2
  exit 1
fi

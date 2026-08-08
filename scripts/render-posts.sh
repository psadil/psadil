#!/bin/bash
# Render every post in its own pixi environment.
#
# posts/_metadata.yml sets `freeze: auto`, so the executed results land in the
# project-level _freeze/ and the root `quarto preview` reuses them without
# needing R or Python itself. A post's freeze goes stale whenever its source
# changes -- including reformatting by prek -- so re-run this after any such
# change, otherwise the root render tries to execute the post and fails.

set -uo pipefail

# run from the repo root regardless of where this was invoked from
cd "$(dirname "$0")/.."

status=0
for d in posts/*/; do
  printf '=== %s\n' "$(basename "$d")"
  if ! (cd "$d" && pixi run render); then
    printf 'FAILED: %s\n' "$d" >&2
    status=1
  fi
done

exit $status

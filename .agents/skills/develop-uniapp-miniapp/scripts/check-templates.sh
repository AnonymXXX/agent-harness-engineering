#!/bin/zsh
# Smoke-check the bundled templates: scaffold project-starter into a temp dir,
# drop the standalone templates into src/_tpl, then install, build, verify Tailwind output,
# type-check and lint.
# Usage: scripts/check-templates.sh [--keep]

set -euo pipefail

skill_root="${0:A:h:h}"
templates="$skill_root/assets/templates"
work_dir="$(mktemp -d "${TMPDIR:-/tmp}/uniapp-template-check.XXXXXX")"

if [[ "${1:-}" != "--keep" ]]; then
  trap 'rm -rf "$work_dir"' EXIT
fi

rsync -a --exclude node_modules --exclude dist "$templates/project-starter/" "$work_dir/"
mkdir -p "$work_dir/src/_tpl"
cp "$templates"/*.vue "$templates"/*.ts "$work_dir/src/_tpl/"
cp -R "$templates/page-with-local-hooks" "$work_dir/src/_tpl/"

cd "$work_dir"
echo "==> install ($work_dir)"
pnpm install --reporter=silent
echo "==> build:mp-weixin"
pnpm -s build:mp-weixin
echo "==> tailwind output"
# A green build is not enough: if Tailwind is not wired into Vite's css.postcss,
# app.wxss ships the raw @tailwind directives and no utilities.
wxss="dist/build/mp-weixin/app.wxss"
if grep -q '@tailwind' "$wxss" || ! grep -qF '.flex{display:flex}' "$wxss"; then
  echo "Tailwind utilities missing from $wxss (raw @tailwind left or .flex{display:flex} absent)." >&2
  exit 1
fi
echo "==> type-check"
pnpm -s type-check
echo "==> lint"
pnpm -s lint
echo "All template checks passed."

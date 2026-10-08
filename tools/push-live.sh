#!/usr/bin/env bash
# Publish the current tree to the repository that Vercel deploys kqcquantum.com from (finn299/kqcquantum)
# as ONE history-free commit. Project history stays in JpDeSilva17/kqc-quantum only, so nothing that was
# ever in an old commit (transaction details, partner logos) travels to the live repository.
#
#   tools/push-live.sh                 # pushes HEAD's tree to git@github.com:finn299/kqcquantum.git main
#   tools/push-live.sh <git-url>       # same, other destination
#
# Vercel builds every push to main of that repository, so the site updates a minute or two later.
set -euo pipefail
cd "$(dirname "$0")/.."

if [ -n "$(git status --porcelain)" ]; then
  echo "Working tree has uncommitted changes. Commit (or stash) first so the snapshot matches a commit." >&2
  exit 1
fi

dest="${1:-git@github.com:finn299/kqcquantum.git}"
head="$(git rev-parse --short HEAD)"
msg="KQC IR site snapshot of ${head}, $(date +%Y-%m-%d)"
snap="$(git commit-tree "HEAD^{tree}" -m "$msg")"

git push --force "$dest" "${snap}:refs/heads/main"
echo "Pushed snapshot ${snap:0:7} (tree of ${head}) to ${dest} main"

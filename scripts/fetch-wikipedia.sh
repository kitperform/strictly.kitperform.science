#!/usr/bin/env sh
# Fetch (or refresh) the raw Wikipedia HTML captures that this project is built on.
#
# Usage:
#   scripts/fetch-wikipedia.sh            # fetch main article + series 1..LATEST
#   scripts/fetch-wikipedia.sh 23 24      # fetch only the listed series numbers
#
# Wikipedia asks automated clients to send a descriptive User-Agent with contact
# info: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_User-Agent_Policy
set -eu

LATEST=24
UA="strictly.kitperform.science/0.1 (https://github.com/kitperform/strictly.kitperform.science)"
ROOT="$(cd "$(dirname "$0")/.." && pwd)/data/wikipedia"

fetch() {
  # $1 = page title, $2 = destination path
  mkdir -p "$(dirname "$2")"
  curl -fsSL -A "$UA" "https://en.wikipedia.org/wiki/$1" -o "$2"
  printf '%8d bytes  %s\n' "$(wc -c < "$2")" "$2"
  sleep 1   # be polite
}

if [ "$#" -eq 0 ]; then
  fetch "Strictly_Come_Dancing" "$ROOT/main/Strictly_Come_Dancing.html"
  set -- $(seq 1 "$LATEST")
fi

for n in "$@"; do
  padded=$(printf '%03d' "$n")
  fetch "Strictly_Come_Dancing_series_$n" "$ROOT/series/$padded/Strictly_Come_Dancing_series_$n.html"
done

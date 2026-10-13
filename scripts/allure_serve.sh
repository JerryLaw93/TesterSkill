#!/usr/bin/env bash
# Start a static HTTP server for a generated Allure report.
#
# Usage:   bash scripts/allure_serve.sh <report-dir> [port]
# Example: bash scripts/allure_serve.sh testcases/allure-report 8080
#
# The server's URL will be http://localhost:<port>/<report-dir-relative-to-cwd>/index.html
# (we cd to the parent of <report-dir> so that index.html is reachable).

set -euo pipefail

REPORT_DIR="${1:-testcases/allure-report}"
PORT="${2:-8080}"

if [ ! -d "$REPORT_DIR" ]; then
  echo "Report dir not found: $REPORT_DIR" >&2
  echo "Run scripts/gen_allure.py first." >&2
  exit 1
fi

PARENT="$(cd "$(dirname "$REPORT_DIR")" && pwd)"
NAME="$(basename "$REPORT_DIR")"
URL="http://localhost:${PORT}/${NAME}/index.html"

cd "$PARENT"
echo "Serving $PARENT on port $PORT"
echo "Open: $URL"
exec python3 -m http.server "$PORT"

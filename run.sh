
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=python3
RPT_DIR="$SCRIPT_DIR/RPT"
OUTPUT_FILE="$SCRIPT_DIR/data/player_data.txt"
TMP_FILE="$(mktemp)"

echo "[$(date +'%T')] Running RPT.py…"
"$PYTHON" "$SCRIPT_DIR/RPT.py"
echo "[$(date +'%T')] RPT.py completed successfully."

mkdir -p "$(dirname "$OUTPUT_FILE")"
touch "$OUTPUT_FILE"

set +e

find "$RPT_DIR" -type f -iname '*.rpt' -print0 \
  | xargs -r -0 awk '
    /\[Login\]: Adding/ {
        # Match "player" then capture everything until the last space before "("
        match($0, /player (.+) \(/, arr)
        if (arr[1] != "") {
            print arr[1]
        }
    }
  ' \
  | sort -u \
  > "$TMP_FILE"

grep -Fxv -f "$OUTPUT_FILE" "$TMP_FILE" >> "$OUTPUT_FILE" 2>/dev/null

set -e  

rm "$TMP_FILE"

echo "✅ $(wc -l < "$OUTPUT_FILE") unique players in $OUTPUT_FILE"

echo "[$(date +'%T')] Running xapi.py…"
"$PYTHON" "$SCRIPT_DIR/xapi.py"
echo "[$(date +'%T')] xapi.py completed successfully."

echo "[$(date +'%T')] Running format.py…"
"$PYTHON" "$SCRIPT_DIR/format.py"
echo "[$(date +'%T')] format.py completed successfully."


echo "[$(date +'%T')] Running bypass.py…"
"$PYTHON" "$SCRIPT_DIR/bypass.py"
echo "[$(date +'%T')] bypass.py completed successfully."

echo "[$(date +'%T')] Running webhook.py…"
"$PYTHON" "$SCRIPT_DIR/webhook.py"
echo "[$(date +'%T')] webhook.py completed successfully."

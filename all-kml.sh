set -e
usage="$0 DATA_DIR OUT_DIR"
[ -n "$1" -a -n "$2" ] || (echo "$usage"; exit 1)
mkdir -p "$2"
while read tab; do
    python3 main.py "$1" kml -l "$tab" > "$2/$(echo "$tab" | sed 's|/|_|g').kml"
done

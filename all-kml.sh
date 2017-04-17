set -e
[ -n "$1" ] || exit 1
[ -n "$2" ] || exit 1
mkdir -p "$2"
while read tab; do
    python3 main.py "$1" kml -l "$tab" > "$2/$(echo "$tab" | sed 's|/|_|g').kml"
done

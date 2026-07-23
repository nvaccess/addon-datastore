#!/usr/bin/env bash

set -euo pipefail

here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
addons_dir="$here/addons"

if ! command -v jq >/dev/null 2>&1; then
	echo "Error: jq is required but was not found in PATH." >&2
	echo "Install jq and run this script again." >&2
	exit 1
fi

if [[ ! -d "$addons_dir" ]]; then
	echo "Error: addons directory not found at '$addons_dir'." >&2
	exit 1
fi

updated_count=0
scanned_count=0

while IFS= read -r -d '' file; do
	((scanned_count += 1))
	tmp_file=$(mktemp)

	# Remove legacy keys from every object; missing keys are ignored safely.
	jq 'walk(
		if type == "object" then
			del(.["codeQL-warnings"], .["codeQL-errors"])
		else
			.
		end
	)' "$file" > "$tmp_file"

	if ! cmp -s "$file" "$tmp_file"; then
		jq --tab . "$tmp_file" > "$file"
		rm -f "$tmp_file"	
		((updated_count += 1))
		echo "Updated: $file"
	else
		rm -f "$tmp_file"
	fi
done < <(find "$addons_dir" -type f -name '*.json' -print0)

echo "Scanned $scanned_count JSON files in '$addons_dir'."
echo "Updated $updated_count files."

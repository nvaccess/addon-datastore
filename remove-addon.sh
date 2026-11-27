#!/usr/bin/env bash

set -euo pipefail

addon_id=$1
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
addons_dir="$here/addons"
discussions_file="$here/discussions.json"
submitters_file="$here/submitters.json"

trap 'rm -f -- "$tmp_discussions" "$tmp_submitters"' EXIT
cp -p -- "$discussions_file" "$tmp_discussions"
cp -p -- "$submitters_file" "$tmp_submitters"

jq --slurp --tab --arg id "$addon_id" '
	if length != 1 or (.[0] | type) != "object" then
		error("discussions.json must contain one object")
	else
		.[0] | with_entries(select((.key | ascii_downcase) != ($id | ascii_downcase)))
	end
' "$discussions_file" > "$tmp_discussions"

jq --slurp --tab --arg id "$addon_id" '
	if length != 1 or (.[0] | type) != "object" then
		error("submitters.json must contain one object")
	else
		.[0] | with_entries(
			if (.value | type) != "object" then
				error("submitter entries must be objects")
			elif (.value | has("addons")) then
				if (.value.addons | type) != "array" then
					error("submitter addons must be an array")
				else
					.value.addons as $original_addons
					| .value.addons |= map(
						if type == "string" then
							select(ascii_downcase != ($id | ascii_downcase))
						else
							.
						end
					)
					| if ($original_addons | length) > 0 and (.value.addons | length) == 0 then
						empty
					else
						.
					end
				end
			else
				.
			end
		)
	end
' "$submitters_file" > "$tmp_submitters"

update_if_changed() {
	local file=$1
	local tmp_file=$2
	local status
	if cmp -s "$file" "$tmp_file"; then
		return
	else
		status=$?
		if [[ $status -ne 1 ]]; then
			return "$status"
		fi
	fi
	mv -f -- "$tmp_file" "$file"
	echo "Updated: $file"
}

update_if_changed "$discussions_file" "$tmp_discussions"
update_if_changed "$submitters_file" "$tmp_submitters"

for addon_path in "$addons_dir"/* "$addons_dir"/.[!.]* "$addons_dir"/..?*; do
	if [[ -e "$addon_path" || -L "$addon_path" ]]; then
		candidate_id=${addon_path##*/}
		if [[ "${candidate_id,,}" == "${addon_id,,}" ]]; then
			rm -rf -- "$addon_path"
			echo "Removed: $addon_path"
		fi
	fi
done

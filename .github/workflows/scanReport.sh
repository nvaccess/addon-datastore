#!/usr/bin/env bash
# Compile a markdown report of VirusTotal scan results for all add-ons
# Input: file name for scan report (optional)
# Output: scanReport.md

set -e

# Take REPORT_FILE as first argument, default to scanReport.md
REPORT_FILE="${1:-scanReport.md}"

echo "# VirusTotal Scan Results Report" > "$REPORT_FILE"
echo >> "$REPORT_FILE"

echo "## Frequency Table: Add-ons by Number of Malicious Flags" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"

# Frequency table: group by malicious count, count, and sort numerically
find ./addons -name "*.json" -print0 | xargs -0 jq -r '.scanResults.virusTotal[0].last_analysis_stats.malicious // 0' \
  | sort -n \
  | uniq -c \
  | awk 'BEGIN {print "| Malicious Flags | Add-on Count |\n|---|---|"} {print "| " $2 " | " $1 " |"}' >> "$REPORT_FILE"

echo >> "$REPORT_FILE"
echo "## Add-ons Flagged as Malicious" >> "$REPORT_FILE"
echo >> "$REPORT_FILE"
# List all flagged add-ons with link and count, then sort numerically descending by malicious count
TMP_FLAGGED=$(mktemp)
find ./addons -name "*.json" -print0 | xargs -0 jq -r -s '
  [
    .[] | {id: .addonId, version: .addonVersionName, vt: .vtScanUrl, malicious: (.scanResults.virusTotal[0].last_analysis_stats.malicious // 0)}
  ] |
  map(select(.malicious > 0)) |
  .[] | (.malicious|tostring) + "\t- [" + .id + "](" + (.vt // "") + ") " + (.version // "?") + " - Malicious: " + (.malicious|tostring)
' > "$TMP_FLAGGED"
sort -r -n -k1,1 "$TMP_FLAGGED" | cut -f2- >> "$REPORT_FILE"
rm "$TMP_FLAGGED"

echo "Report written to $REPORT_FILE"

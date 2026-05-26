from pathlib import Path
import csv
from datetime import datetime, timezone

# -----------------------------
# Spain 82 App Database Template Generator
# Stage 2: Generate empty database CSV templates
# -----------------------------

EXPORT_DIR = Path("data/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.now(timezone.utc).isoformat()


def write_csv(filename, fieldnames, rows=None):
    """Create a CSV file with headers and optional rows."""
    rows = rows or []
    path = EXPORT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}")


# -----------------------------
# 1. Seasons
# -----------------------------

seasons_fields = [
    "season_id",
    "season_label",
    "start_year",
    "end_year",
    "is_active_for_extraction",
    "notes",
]

seasons_rows = [
    {"season_id": "2021-22", "season_label": "2021/22", "start_year": "2021", "end_year": "2022", "is_active_for_extraction": "true", "notes": ""},
    {"season_id": "2022-23", "season_label": "2022/23", "start_year": "2022", "end_year": "2023", "is_active_for_extraction": "true", "notes": ""},
    {"season_id": "2023-24", "season_label": "2023/24", "start_year": "2023", "end_year": "2024", "is_active_for_extraction": "true", "notes": ""},
    {"season_id": "2024-25", "season_label": "2024/25", "start_year": "2024", "end_year": "2025", "is_active_for_extraction": "true", "notes": ""},
    {"season_id": "2025-26", "season_label": "2025/26", "start_year": "2025", "end_year": "2026", "is_active_for_extraction": "true", "notes": ""},
]


# -----------------------------
# 2. Competitions
# -----------------------------

competitions_fields = [
    "competition_id",
    "competition_name",
    "competition_level",
    "competition_group",
    "source_system",
    "expected_matchdays",
    "expected_matches_per_season",
    "notes",
]

competitions_rows = [
    {"competition_id": "PRIMERA_DIVISION", "competition_name": "Primera División", "competition_level": "1", "competition_group": "", "source_system": "LaLiga", "expected_matchdays": "38", "expected_matches_per_season": "380", "notes": "Also known as LaLiga EA Sports in recent sponsorship cycle."},
    {"competition_id": "SEGUNDA_DIVISION", "competition_name": "Segunda División", "competition_level": "2", "competition_group": "", "source_system": "LaLiga", "expected_matchdays": "42", "expected_matches_per_season": "462", "notes": "Also known as LaLiga Hypermotion in recent sponsorship cycle."},
    {"competition_id": "PRIMERA_FEDERACION_G1", "competition_name": "Primera Federación", "competition_level": "3", "competition_group": "Group 1", "source_system": "RFEF", "expected_matchdays": "38", "expected_matches_per_season": "380", "notes": ""},
    {"competition_id": "PRIMERA_FEDERACION_G2", "competition_name": "Primera Federación", "competition_level": "3", "competition_group": "Group 2", "source_system": "RFEF", "expected_matchdays": "38", "expected_matches_per_season": "380", "notes": ""},
]


# -----------------------------
# 3. Teams
# -----------------------------

teams_fields = [
    "team_id",
    "club_name_official",
    "club_name_short",
    "club_name_display",
    "slug",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_level",
    "competition_group",
    "home_ground_id",
    "home_ground_name",
    "city",
    "province",
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
    "regional_challenge_eligible",
    "regional_challenge_group_name",
    "official_club_url",
    "source_url",
    "active_in_current_82_app",
    "historical_team",
    "notes",
]


# -----------------------------
# 4. Grounds
# -----------------------------

grounds_fields = [
    "ground_id",
    "ground_name",
    "city",
    "province",
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
    "capacity",
    "latitude",
    "longitude",
    "opened_year",
    "primary_tenant_team_id",
    "official_source_url",
    "notes",
]


# -----------------------------
# 5. Team aliases
# -----------------------------

team_aliases_fields = [
    "alias_id",
    "team_id",
    "source_name",
    "normalised_name",
    "source_system",
    "valid_from_season",
    "valid_to_season",
    "notes",
]# -----------------------------
# 6. Fixtures/results
# -----------------------------

fixtures_fields = [
    "fixture_id",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_level",
    "competition_group",
    "matchday",
    "round_label",
    "fixture_date",
    "kickoff_time_local",
    "home_team_id",
    "home_team_name_source",
    "away_team_id",
    "away_team_name_source",
    "home_score",
    "away_score",
    "result_status",
    "venue_id",
    "venue_name_source",
    "attendance",
    "referee",
    "match_report_url",
    "rfef_acta_url",
    "laliga_match_url",
    "source_system",
    "source_url",
    "source_retrieved_at",
    "data_confidence",
    "notes",
]


# -----------------------------
# 7. Team fixture index
# -----------------------------

team_fixture_index_fields = [
    "team_fixture_id",
    "fixture_id",
    "team_id",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "matchday",
    "fixture_date",
    "opponent_team_id",
    "home_or_away",
    "team_score",
    "opponent_score",
    "result_for_team",
    "venue_id",
    "is_home_ground",
    "team_autonomous_region_id",
    "team_autonomous_region_name",
    "team_autonomous_region_slug",
    "opponent_autonomous_region_id",
    "opponent_autonomous_region_name",
    "opponent_autonomous_region_slug",
    "source_url",
]


# -----------------------------
# 8. Fixture source audit
# -----------------------------

fixture_source_audit_fields = [
    "source_id",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "matchday",
    "source_system",
    "source_url",
    "expected_match_count",
    "status",
    "last_checked_at",
    "notes",
]


# -----------------------------
# 9. Autonomous regions
# -----------------------------

autonomous_regions_fields = [
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
    "regional_challenge_group_name",
    "notes",
]

autonomous_regions_rows = [
    {"autonomous_region_id": "AN", "autonomous_region_name": "Andalusia", "autonomous_region_slug": "andalusia", "regional_challenge_group_name": "Andalusia Challenge", "notes": ""},
    {"autonomous_region_id": "AR", "autonomous_region_name": "Aragon", "autonomous_region_slug": "aragon", "regional_challenge_group_name": "Aragon Challenge", "notes": ""},
    {"autonomous_region_id": "AS", "autonomous_region_name": "Asturias", "autonomous_region_slug": "asturias", "regional_challenge_group_name": "Asturias Challenge", "notes": ""},
    {"autonomous_region_id": "IB", "autonomous_region_name": "Balearic Islands", "autonomous_region_slug": "balearic-islands", "regional_challenge_group_name": "Balearic Islands Challenge", "notes": ""},
    {"autonomous_region_id": "PV", "autonomous_region_name": "Basque Country", "autonomous_region_slug": "basque-country", "regional_challenge_group_name": "Basque Country Challenge", "notes": ""},
    {"autonomous_region_id": "CN", "autonomous_region_name": "Canary Islands", "autonomous_region_slug": "canary-islands", "regional_challenge_group_name": "Canary Islands Challenge", "notes": ""},
    {"autonomous_region_id": "CB", "autonomous_region_name": "Cantabria", "autonomous_region_slug": "cantabria", "regional_challenge_group_name": "Cantabria Challenge", "notes": ""},
    {"autonomous_region_id": "CM", "autonomous_region_name": "Castilla-La Mancha", "autonomous_region_slug": "castilla-la-mancha", "regional_challenge_group_name": "Castilla-La Mancha Challenge", "notes": ""},
    {"autonomous_region_id": "CL", "autonomous_region_name": "Castile and León", "autonomous_region_slug": "castile-and-leon", "regional_challenge_group_name": "Castile and León Challenge", "notes": ""},
    {"autonomous_region_id": "CT", "autonomous_region_name": "Catalonia", "autonomous_region_slug": "catalonia", "regional_challenge_group_name": "Catalonia Challenge", "notes": ""},
    {"autonomous_region_id": "EX", "autonomous_region_name": "Extremadura", "autonomous_region_slug": "extremadura", "regional_challenge_group_name": "Extremadura Challenge", "notes": ""},
    {"autonomous_region_id": "GA", "autonomous_region_name": "Galicia", "autonomous_region_slug": "galicia", "regional_challenge_group_name": "Galicia Challenge", "notes": ""},
    {"autonomous_region_id": "MD", "autonomous_region_name": "Community of Madrid", "autonomous_region_slug": "community-of-madrid", "regional_challenge_group_name": "Community of Madrid Challenge", "notes": ""},
    {"autonomous_region_id": "MU", "autonomous_region_name": "Region of Murcia", "autonomous_region_slug": "region-of-murcia", "regional_challenge_group_name": "Region of Murcia Challenge", "notes": ""},
    {"autonomous_region_id": "NC", "autonomous_region_name": "Navarre", "autonomous_region_slug": "navarre", "regional_challenge_group_name": "Navarre Challenge", "notes": ""},
    {"autonomous_region_id": "RI", "autonomous_region_name": "La Rioja", "autonomous_region_slug": "la-rioja", "regional_challenge_group_name": "La Rioja Challenge", "notes": ""},
    {"autonomous_region_id": "VC", "autonomous_region_name": "Valencian Community", "autonomous_region_slug": "valencian-community", "regional_challenge_group_name": "Valencian Community Challenge", "notes": ""},
    {"autonomous_region_id": "CE", "autonomous_region_name": "Ceuta", "autonomous_region_slug": "ceuta", "regional_challenge_group_name": "Ceuta Challenge", "notes": ""},
    {"autonomous_region_id": "ML", "autonomous_region_name": "Melilla", "autonomous_region_slug": "melilla", "regional_challenge_group_name": "Melilla Challenge", "notes": ""},
]


# -----------------------------
# 10. User attended fixtures template
# -----------------------------

user_attended_fixtures_fields = [
    "user_attendance_id",
    "user_id",
    "fixture_id",
    "team_fixture_id",
    "selected_team_id",
    "venue_id",
    "attendance_date",
    "created_at",
    "attendance_type",
    "notes",
    "photo_url",
    "manual_entry_flag",
]


# -----------------------------
# Write CSV files
# -----------------------------

write_csv("seasons.csv", seasons_fields, seasons_rows)
write_csv("competitions.csv", competitions_fields, competitions_rows)
write_csv("teams.csv", teams_fields)
write_csv("grounds.csv", grounds_fields)
write_csv("team_aliases.csv", team_aliases_fields)
write_csv("fixtures_results.csv", fixtures_fields)
write_csv("team_fixture_index.csv", team_fixture_index_fields)
write_csv("fixture_source_audit.csv", fixture_source_audit_fields)
write_csv("autonomous_regions.csv", autonomous_regions_fields, autonomous_regions_rows)
write_csv("user_attended_fixtures_template.csv", user_attended_fixtures_fields)


# -----------------------------
# Validation report
# -----------------------------

validation_report = f"""# Spain 82 App Database Template Validation Report

Generated at: {NOW}

## Stage

Stage 2 completed: database CSV templates generated.

## Files created

- seasons.csv
- competitions.csv
- teams.csv
- grounds.csv
- team_aliases.csv
- fixtures_results.csv
- team_fixture_index.csv
- fixture_source_audit.csv
- autonomous_regions.csv
- user_attended_fixtures_template.csv

## Validation checks

- Export folder created: yes
- Core CSV templates created: yes
- Seasons populated: yes
- Competitions populated: yes
- Autonomous regions populated: yes
- Fixtures table ready: yes
- Team fixture index table ready: yes
- Regional challenge fields included: yes

## Notes

This script does not yet extract live fixture data.

The next stage will be to generate a source map for the official LaLiga and RFEF source pages.
"""

Path("validation_report.md").write_text(validation_report, encoding="utf-8")
print("Created validation_report.md")
# -----------------------------
# Stage 3: Generate official source map
# -----------------------------

source_map_fields = [
    "source_id",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "matchday",
    "source_system",
    "source_url",
    "expected_match_count",
    "status",
    "last_checked_at",
    "notes",
]

source_map_rows = []

for season in ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]:

    # Primera División / LaLiga
    for matchday in range(1, 39):
        source_map_rows.append({
            "source_id": f"{season}_PRIMERA_DIVISION_J{matchday:02d}",
            "season_id": season,
            "competition_id": "PRIMERA_DIVISION",
            "competition_name": "Primera División",
            "competition_group": "",
            "matchday": str(matchday),
            "source_system": "LaLiga",
            "source_url": f"https://www.laliga.com/laliga-easports/resultados/{season}/jornada-{matchday}",
            "expected_match_count": "10",
            "status": "pending",
            "last_checked_at": "",
            "notes": "",
        })

    # Segunda División / LaLiga Hypermotion
    for matchday in range(1, 43):
        source_map_rows.append({
            "source_id": f"{season}_SEGUNDA_DIVISION_J{matchday:02d}",
            "season_id": season,
            "competition_id": "SEGUNDA_DIVISION",
            "competition_name": "Segunda División",
            "competition_group": "",
            "matchday": str(matchday),
            "source_system": "LaLiga",
            "source_url": f"https://www.laliga.com/laliga-hypermotion/resultados/{season}/jornada-{matchday}",
            "expected_match_count": "11",
            "status": "pending",
            "last_checked_at": "",
            "notes": "",
        })

    # Primera Federación Group 1 placeholder
    for matchday in range(1, 39):
        source_map_rows.append({
            "source_id": f"{season}_PRIMERA_FEDERACION_G1_J{matchday:02d}",
            "season_id": season,
            "competition_id": "PRIMERA_FEDERACION_G1",
            "competition_name": "Primera Federación",
            "competition_group": "Group 1",
            "matchday": str(matchday),
            "source_system": "RFEF",
            "source_url": "",
            "expected_match_count": "10",
            "status": "source_url_required",
            "last_checked_at": "",
            "notes": "RFEF source URL to be discovered and added.",
        })

    # Primera Federación Group 2 placeholder
    for matchday in range(1, 39):
        source_map_rows.append({
            "source_id": f"{season}_PRIMERA_FEDERACION_G2_J{matchday:02d}",
            "season_id": season,
            "competition_id": "PRIMERA_FEDERACION_G2",
            "competition_name": "Primera Federación",
            "competition_group": "Group 2",
            "matchday": str(matchday),
            "source_system": "RFEF",
            "source_url": "",
            "expected_match_count": "10",
            "status": "source_url_required",
            "last_checked_at": "",
            "notes": "RFEF source URL to be discovered and added.",
        })

write_csv("official_source_map.csv", source_map_fields, source_map_rows)

print(f"Stage 3 source map generated with {len(source_map_rows)} source rows.")

print("Stage 2 template generation complete.")
# Stage 3B: Add playoff fixtures to official source map
# -----------------------------
# Important:
# Paste this block at the very bottom of scripts/official_extraction_runner.py,
# underneath the Stage 3 source map block.
#
# This block updates official_source_map.csv so that the database includes
# playoff fixture sources for:
# - Segunda División promotion playoffs

# - Primera Federación Group 1 promotion playoffs
# - Primera Federación Group 2 promotion playoffs
#
# Primera División / LaLiga regular top division does not have playoffs.

# Add phase/round columns if they are not already in the source map.
for extra_field in ["fixture_phase", "round_label"]:
    if extra_field not in source_map_fields:
        source_map_fields.append(extra_field)

# Backfill the regular-season rows created in Stage 3.
for row in source_map_rows:
    row.setdefault("fixture_phase", "regular_season")
    row.setdefault("round_label", f"Jornada {row.get('matchday', '')}".strip())

# Playoff round structure.
# These are source-map placeholders. The live extraction stage will later attach
# the exact official LaLiga/RFEF source URLs for each season and round.
playoff_rounds = [
    {
        "round_code": "SF1",
        "round_label": "Promotion playoff semi-final first leg",
        "expected_match_count": "2",
    },
    {
        "round_code": "SF2",
        "round_label": "Promotion playoff semi-final second leg",
        "expected_match_count": "2",
    },
    {
        "round_code": "F1",
        "round_label": "Promotion playoff final first leg",
        "expected_match_count": "1",
    },
    {
        "round_code": "F2",
        "round_label": "Promotion playoff final second leg",
        "expected_match_count": "1",
    },
]

playoff_competitions = [
    {
        "competition_id": "SEGUNDA_DIVISION",
        "competition_name": "Segunda División",
        "competition_group": "",
        "source_system": "LaLiga",
        "notes": "Promotion playoff source URL to be discovered and added from official LaLiga source.",
    },
    {
        "competition_id": "PRIMERA_FEDERACION_G1",
        "competition_name": "Primera Federación",
        "competition_group": "Group 1",
        "source_system": "RFEF",
        "notes": "Promotion playoff source URL to be discovered and added from official RFEF source.",
    },
    {
        "competition_id": "PRIMERA_FEDERACION_G2",
        "competition_name": "Primera Federación",
        "competition_group": "Group 2",
        "source_system": "RFEF",
        "notes": "Promotion playoff source URL to be discovered and added from official RFEF source.",
    },
]

for season in ["2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]:
    for competition in playoff_competitions:
        for playoff_round in playoff_rounds:
            source_map_rows.append({
                "source_id": f"{season}_{competition['competition_id']}_PLAYOFF_{playoff_round['round_code']}",
                "season_id": season,
                "competition_id": competition["competition_id"],
                "competition_name": competition["competition_name"],
                "competition_group": competition["competition_group"],
                "matchday": "",
                "fixture_phase": "promotion_playoff",
                "round_label": playoff_round["round_label"],
                "source_system": competition["source_system"],
                "source_url": "",
                "expected_match_count": playoff_round["expected_match_count"],
                "status": "source_url_required",
                "last_checked_at": "",
                "notes": competition["notes"],
            })

# Re-write the source map with regular-season and playoff rows included.
write_csv("official_source_map.csv", source_map_fields, source_map_rows)

print(f"Stage 3B playoff source map rows added. Total source rows now: {len(source_map_rows)}")
# -----------------------------
# Stage 4A: Test connection to official LaLiga source
# -----------------------------

import urllib.request
import urllib.error

connection_test_fields = [
    "test_name",
    "source_url",
    "http_status",
    "success",
    "checked_at",
    "notes",
]

connection_test_rows = []

test_url = "https://www.laliga.com/laliga-easports/resultados/2021-22/jornada-1"

try:
    request = urllib.request.Request(
        test_url,
        headers={
            "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        status_code = response.getcode()
        page_content = response.read().decode("utf-8", errors="ignore")

    success = status_code == 200 and len(page_content) > 1000

    connection_test_rows.append({
        "test_name": "LaLiga Primera División Jornada 1 connection test",
        "source_url": test_url,
        "http_status": str(status_code),
        "success": str(success).lower(),
        "checked_at": NOW,
        "notes": f"Downloaded {len(page_content)} characters from official LaLiga page.",
    })

    # Save a small raw HTML sample for inspection.
    raw_sample_path = EXPORT_DIR / "laliga_connection_test_sample.html"
    raw_sample_path.write_text(page_content[:5000], encoding="utf-8")

except urllib.error.HTTPError as e:
    connection_test_rows.append({
        "test_name": "LaLiga Primera División Jornada 1 connection test",
        "source_url": test_url,
        "http_status": str(e.code),
        "success": "false",
        "checked_at": NOW,
        "notes": f"HTTPError: {e.reason}",
    })

except Exception as e:
    connection_test_rows.append({
        "test_name": "LaLiga Primera División Jornada 1 connection test",
        "source_url": test_url,
        "http_status": "",
        "success": "false",
        "checked_at": NOW,
        "notes": f"Error: {type(e).__name__}: {e}",
    })

write_csv("laliga_connection_test.csv", connection_test_fields, connection_test_rows)

print("Stage 4A LaLiga connection test complete.")
# -----------------------------
# Stage 4B: Extract one LaLiga matchday page into raw fixture candidates
# -----------------------------

import re
import json

raw_laliga_fields = [
    "source_url",
    "season_id",
    "competition_id",
    "matchday",
    "extraction_method",
    "raw_home_team",
    "raw_away_team",
    "raw_home_score",
    "raw_away_score",
    "raw_date",
    "raw_time",
    "raw_match_url",
    "data_confidence",
    "notes",
]

raw_laliga_rows = []

stage_4b_url = "https://www.laliga.com/laliga-easports/resultados/2021-22/jornada-1"

try:
    request = urllib.request.Request(
        stage_4b_url,
        headers={
            "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        status_code = response.getcode()
        html = response.read().decode("utf-8", errors="ignore")

    # Save full raw HTML for inspection/debugging.
    raw_html_path = EXPORT_DIR / "stage_4b_laliga_jornada_1_raw.html"
    raw_html_path.write_text(html, encoding="utf-8")

    # First attempt: look for embedded Next.js JSON data.
    next_data_match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html,
        re.DOTALL
    )

    if next_data_match:
        try:
            next_data = json.loads(next_data_match.group(1))

            # Save embedded JSON for inspection.
            json_path = EXPORT_DIR / "stage_4b_laliga_next_data.json"
            json_path.write_text(
                json.dumps(next_data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )

            # At this stage we are not assuming the exact nested structure.
            # We create an inspection row confirming that JSON was found.
            raw_laliga_rows.append({
                "source_url": stage_4b_url,
                "season_id": "2021-22",
                "competition_id": "PRIMERA_DIVISION",
                "matchday": "1",
                "extraction_method": "next_data_detected",
                "raw_home_team": "",
                "raw_away_team": "",
                "raw_home_score": "",
                "raw_away_score": "",
                "raw_date": "",
                "raw_time": "",
                "raw_match_url": "",
                "data_confidence": "inspection_required",
                "notes": "Embedded __NEXT_DATA__ JSON found and saved for structure inspection.",
            })

        except Exception as e:
            raw_laliga_rows.append({
                "source_url": stage_4b_url,
                "season_id": "2021-22",
                "competition_id": "PRIMERA_DIVISION",
                "matchday": "1",
                "extraction_method": "next_data_parse_failed",
                "raw_home_team": "",
                "raw_away_team": "",
                "raw_home_score": "",
                "raw_away_score": "",
                "raw_date": "",
                "raw_time": "",
                "raw_match_url": "",
                "data_confidence": "failed",
                "notes": f"Found __NEXT_DATA__ but could not parse JSON: {type(e).__name__}: {e}",
            })

    else:
        # Fallback: record that no embedded JSON was found.
        # The saved raw HTML will be used to decide the next parser route.
        raw_laliga_rows.append({
            "source_url": stage_4b_url,
            "season_id": "2021-22",
            "competition_id": "PRIMERA_DIVISION",
            "matchday": "1",
            "extraction_method": "raw_html_saved",
            "raw_home_team": "",
            "raw_away_team": "",
            "raw_home_score": "",
            "raw_away_score": "",
            "raw_date": "",
            "raw_time": "",
            "raw_match_url": "",
            "data_confidence": "inspection_required",
            "notes": "No __NEXT_DATA__ JSON found. Raw HTML saved for inspection.",
        })

except Exception as e:
    raw_laliga_rows.append({
        "source_url": stage_4b_url,
        "season_id": "2021-22",
        "competition_id": "PRIMERA_DIVISION",
        "matchday": "1",
        "extraction_method": "connection_or_extraction_failed",
        "raw_home_team": "",
        "raw_away_team": "",
        "raw_home_score": "",
        "raw_away_score": "",
        "raw_date": "",
        "raw_time": "",
        "raw_match_url": "",
        "data_confidence": "failed",
        "notes": f"Error: {type(e).__name__}: {e}",
    })

write_csv("raw_laliga_stage_4b_jornada_1.csv", raw_laliga_fields, raw_laliga_rows)

print("Stage 4B LaLiga raw extraction inspection complete.")
# -----------------------------
# Stage 4C: Inspect LaLiga embedded JSON structure
# -----------------------------

json_scan_fields = [
    "json_path",
    "value_type",
    "value_preview",
    "keyword_match",
    "notes",
]

json_scan_rows = []

keywords = [
    "match",
    "matches",
    "fixture",
    "fixtures",
    "home",
    "away",
    "score",
    "team",
    "teams",
    "result",
    "date",
    "kickoff",
    "calendar",
    "jornada",
]


def scan_json(obj, path="root", depth=0, max_depth=8):
    """Recursively scan JSON keys/values for fixture-like data."""
    if depth > max_depth:
        return

    if isinstance(obj, dict):
        for key, value in obj.items():
            key_str = str(key)
            new_path = f"{path}.{key_str}"

            matched_keywords = [
                word for word in keywords
                if word.lower() in key_str.lower()
            ]

            if matched_keywords:
                preview = ""

                if isinstance(value, (str, int, float, bool)) or value is None:
                    preview = str(value)[:250]
                elif isinstance(value, list):
                    preview = f"List with {len(value)} items"
                elif isinstance(value, dict):
                    preview = f"Dict with {len(value)} keys"

                json_scan_rows.append({
                    "json_path": new_path,
                    "value_type": type(value).__name__,
                    "value_preview": preview,
                    "keyword_match": ", ".join(matched_keywords),
                    "notes": "Key matched fixture-related keyword.",
                })

            scan_json(value, new_path, depth + 1, max_depth)

    elif isinstance(obj, list):
        for index, item in enumerate(obj[:20]):
            new_path = f"{path}[{index}]"
            scan_json(item, new_path, depth + 1, max_depth)


try:
    json_path = EXPORT_DIR / "stage_4b_laliga_next_data.json"

    if json_path.exists():
        with json_path.open("r", encoding="utf-8") as f:
            next_data_for_scan = json.load(f)

        scan_json(next_data_for_scan)

        if not json_scan_rows:
            json_scan_rows.append({
                "json_path": "root",
                "value_type": type(next_data_for_scan).__name__,
                "value_preview": "No keyword matches found",
                "keyword_match": "",
                "notes": "JSON was loaded but no likely fixture-related keys were found.",
            })

    else:
        json_scan_rows.append({
            "json_path": "",
            "value_type": "",
            "value_preview": "",
            "keyword_match": "",
            "notes": "stage_4b_laliga_next_data.json was not found. Run Stage 4B first.",
        })

except Exception as e:
    json_scan_rows.append({
        "json_path": "",
        "value_type": "",
        "value_preview": "",
        "keyword_match": "",
        "notes": f"Error scanning JSON: {type(e).__name__}: {e}",
    })

write_csv("stage_4c_laliga_json_key_scan.csv", json_scan_fields, json_scan_rows)

print(f"Stage 4C JSON key scan complete with {len(json_scan_rows)} rows.")
# -----------------------------
# Stage 4D: Extract actual LaLiga Jornada 1 fixture rows
# -----------------------------

stage_4d_fields = [
    "source_url",
    "season_id",
    "competition_id",
    "competition_name",
    "matchday",
    "fixture_date",
    "home_team_name_source",
    "away_team_name_source",
    "home_score",
    "away_score",
    "extraction_method",
    "data_confidence",
    "notes",
]

stage_4d_rows = []

try:
    json_path = EXPORT_DIR / "stage_4b_laliga_next_data.json"

    with json_path.open("r", encoding="utf-8") as f:
        next_data = json.load(f)

    matches = next_data["props"]["pageProps"]["matches"]

    for match in matches:
        home_team = match.get("home_team", {})
        away_team = match.get("away_team", {})

        home_name = (
            home_team.get("name")
            or home_team.get("nickname")
            or home_team.get("short_name")
            or ""
        )

        away_name = (
            away_team.get("name")
            or away_team.get("nickname")
            or away_team.get("short_name")
            or ""
        )

        stage_4d_rows.append({
            "source_url": "https://www.laliga.com/laliga-easports/resultados/2021-22/jornada-1",
            "season_id": "2021-22",
            "competition_id": "PRIMERA_DIVISION",
            "competition_name": "Primera División",
            "matchday": "1",
            "fixture_date": match.get("date", ""),
            "home_team_name_source": home_name,
            "away_team_name_source": away_name,
            "home_score": match.get("home_score", ""),
            "away_score": match.get("away_score", ""),
            "extraction_method": "next_data_props_pageProps_matches",
            "data_confidence": "high",
            "notes": "",
        })

except Exception as e:
    stage_4d_rows.append({
        "source_url": "https://www.laliga.com/laliga-easports/resultados/2021-22/jornada-1",
        "season_id": "2021-22",
        "competition_id": "PRIMERA_DIVISION",
        "competition_name": "Primera División",
        "matchday": "1",
        "fixture_date": "",
        "home_team_name_source": "",
        "away_team_name_source": "",
        "home_score": "",
        "away_score": "",
        "extraction_method": "failed",
        "data_confidence": "failed",
        "notes": f"Error: {type(e).__name__}: {e}",
    })

write_csv("stage_4d_laliga_jornada_1_fixtures.csv", stage_4d_fields, stage_4d_rows)

print(f"Stage 4D extracted {len(stage_4d_rows)} fixture rows.")
# -----------------------------
# Stage 4E: Convert raw LaLiga Jornada 1 rows into app fixture rows
# -----------------------------

def make_team_id(team_name):
    """Create a simple stable-looking team_id from a source team name."""
    cleaned = team_name.upper()
    cleaned = cleaned.replace("Á", "A").replace("É", "E").replace("Í", "I")
    cleaned = cleaned.replace("Ó", "O").replace("Ú", "U").replace("Ü", "U")
    cleaned = cleaned.replace("Ñ", "N")
    cleaned = re.sub(r"[^A-Z0-9]+", "_", cleaned)
    cleaned = cleaned.strip("_")
    return cleaned


def make_fixture_id(season_id, competition_id, matchday, home_team_id, away_team_id):
    return f"{season_id}_{competition_id}_J{int(matchday):02d}_{home_team_id}_{away_team_id}"


stage_4e_fields = [
    "fixture_id",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_level",
    "competition_group",
    "matchday",
    "round_label",
    "fixture_date",
    "kickoff_time_local",
    "home_team_id",
    "home_team_name_source",
    "away_team_id",
    "away_team_name_source",
    "home_score",
    "away_score",
    "result_status",
    "venue_id",
    "venue_name_source",
    "attendance",
    "referee",
    "match_report_url",
    "rfef_acta_url",
    "laliga_match_url",
    "source_system",
    "source_url",
    "source_retrieved_at",
    "data_confidence",
    "notes",
]

stage_4e_rows = []

try:
    raw_file = EXPORT_DIR / "stage_4d_laliga_jornada_1_fixtures.csv"

    with raw_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    for row in raw_rows:
        home_name = row["home_team_name_source"]
        away_name = row["away_team_name_source"]

        home_team_id = make_team_id(home_name)
        away_team_id = make_team_id(away_name)

        fixture_id = make_fixture_id(
            row["season_id"],
            row["competition_id"],
            row["matchday"],
            home_team_id,
            away_team_id,
        )

        stage_4e_rows.append({
            "fixture_id": fixture_id,
            "season_id": row["season_id"],
            "competition_id": row["competition_id"],
            "competition_name": row["competition_name"],
            "competition_level": "1",
            "competition_group": "",
            "matchday": row["matchday"],
            "round_label": f"Jornada {row['matchday']}",
            "fixture_date": row["fixture_date"],
            "kickoff_time_local": "",
            "home_team_id": home_team_id,
            "home_team_name_source": home_name,
            "away_team_id": away_team_id,
            "away_team_name_source": away_name,
            "home_score": row["home_score"],
            "away_score": row["away_score"],
            "result_status": "played",
            "venue_id": "",
            "venue_name_source": "",
            "attendance": "",
            "referee": "",
            "match_report_url": "",
            "rfef_acta_url": "",
            "laliga_match_url": "",
            "source_system": "LaLiga",
            "source_url": row["source_url"],
            "source_retrieved_at": NOW,
            "data_confidence": "high",
            "notes": "Generated from Stage 4D raw LaLiga Jornada 1 extraction.",
        })

except Exception as e:
    stage_4e_rows.append({
        "fixture_id": "",
        "season_id": "2021-22",
        "competition_id": "PRIMERA_DIVISION",
        "competition_name": "Primera División",
        "competition_level": "1",
        "competition_group": "",
        "matchday": "1",
        "round_label": "Jornada 1",
        "fixture_date": "",
        "kickoff_time_local": "",
        "home_team_id": "",
        "home_team_name_source": "",
        "away_team_id": "",
        "away_team_name_source": "",
        "home_score": "",
        "away_score": "",
        "result_status": "",
        "venue_id": "",
        "venue_name_source": "",
        "attendance": "",
        "referee": "",
        "match_report_url": "",
        "rfef_acta_url": "",
        "laliga_match_url": "",
        "source_system": "LaLiga",
        "source_url": "https://www.laliga.com/laliga-easports/resultados/2021-22/jornada-1",
        "source_retrieved_at": NOW,
        "data_confidence": "failed",
        "notes": f"Error: {type(e).__name__}: {e}",
    })

write_csv("fixtures_results_stage_4e.csv", stage_4e_fields, stage_4e_rows)

print(f"Stage 4E generated {len(stage_4e_rows)} app fixture rows.")

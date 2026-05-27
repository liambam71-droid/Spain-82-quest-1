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
# -----------------------------
# Stage 4F: Build team fixture index from Stage 4E fixture rows
# -----------------------------

stage_4f_fields = [
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

stage_4f_rows = []


def result_for_team(team_score, opponent_score):
    """Return Win/Loss/Draw from the team's perspective."""
    try:
        team_score_int = int(team_score)
        opponent_score_int = int(opponent_score)

        if team_score_int > opponent_score_int:
            return "Win"
        if team_score_int < opponent_score_int:
            return "Loss"
        return "Draw"

    except Exception:
        return ""


try:
    fixtures_file = EXPORT_DIR / "fixtures_results_stage_4e.csv"

    with fixtures_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fixtures = list(reader)

    for fixture in fixtures:
        fixture_id = fixture["fixture_id"]

        home_team_id = fixture["home_team_id"]
        away_team_id = fixture["away_team_id"]

        home_score = fixture["home_score"]
        away_score = fixture["away_score"]

        # Home team perspective
        stage_4f_rows.append({
            "team_fixture_id": f"{fixture_id}__{home_team_id}",
            "fixture_id": fixture_id,
            "team_id": home_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": away_team_id,
            "home_or_away": "Home",
            "team_score": home_score,
            "opponent_score": away_score,
            "result_for_team": result_for_team(home_score, away_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "true",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

        # Away team perspective
        stage_4f_rows.append({
            "team_fixture_id": f"{fixture_id}__{away_team_id}",
            "fixture_id": fixture_id,
            "team_id": away_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": home_team_id,
            "home_or_away": "Away",
            "team_score": away_score,
            "opponent_score": home_score,
            "result_for_team": result_for_team(away_score, home_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "false",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

except Exception as e:
    stage_4f_rows.append({
        "team_fixture_id": "",
        "fixture_id": "",
        "team_id": "",
        "season_id": "2021-22",
        "competition_id": "PRIMERA_DIVISION",
        "competition_name": "Primera División",
        "competition_group": "",
        "matchday": "1",
        "fixture_date": "",
        "opponent_team_id": "",
        "home_or_away": "",
        "team_score": "",
        "opponent_score": "",
        "result_for_team": "",
        "venue_id": "",
        "is_home_ground": "",
        "team_autonomous_region_id": "",
        "team_autonomous_region_name": "",
        "team_autonomous_region_slug": "",
        "opponent_autonomous_region_id": "",
        "opponent_autonomous_region_name": "",
        "opponent_autonomous_region_slug": "",
        "source_url": "",
    })

    print(f"Stage 4F failed: {type(e).__name__}: {e}")

write_csv("team_fixture_index_stage_4f.csv", stage_4f_fields, stage_4f_rows)

print(f"Stage 4F generated {len(stage_4f_rows)} team fixture index rows.")
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
# Stage 4G: Add autonomous region tags to Stage 4F team fixture index
# -----------------------------

team_region_map_fields = [
    "team_id",
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
    "region_aliases",
    "notes",
]

team_region_map_rows = [
    {
        "team_id": "VALENCIA",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
        "region_aliases": "Valencian Community|Comunitat Valenciana|Comunidad Valenciana|Valencia region",
        "notes": "",
    },
    {
        "team_id": "GETAFE",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
        "region_aliases": "Madrid|Community of Madrid|Comunidad de Madrid|Madrid region|Region of Madrid",
        "notes": "",
    },
    {
        "team_id": "MALLORCA",
        "autonomous_region_id": "IB",
        "autonomous_region_name": "Balearic Islands",
        "autonomous_region_slug": "balearic-islands",
        "region_aliases": "Balearic Islands|Illes Balears|Islas Baleares|Mallorca",
        "notes": "",
    },
    {
        "team_id": "REAL_BETIS",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
        "region_aliases": "Andalusia|Andalucía|Andalucia",
        "notes": "",
    },
    {
        "team_id": "CADIZ_CF",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
        "region_aliases": "Andalusia|Andalucía|Andalucia",
        "notes": "",
    },
    {
        "team_id": "LEVANTE",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
        "region_aliases": "Valencian Community|Comunitat Valenciana|Comunidad Valenciana|Valencia region",
        "notes": "",
    },
    {
        "team_id": "DEPORTIVO_ALAVES",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
        "region_aliases": "Basque Country|País Vasco|Euskadi|Euskal Herria",
        "notes": "",
    },
    {
        "team_id": "REAL_MADRID",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
        "region_aliases": "Madrid|Community of Madrid|Comunidad de Madrid|Madrid region|Region of Madrid",
        "notes": "",
    },
    {
        "team_id": "OSASUNA",
        "autonomous_region_id": "NC",
        "autonomous_region_name": "Navarre",
        "autonomous_region_slug": "navarre",
        "region_aliases": "Navarre|Navarra|Nafarroa",
        "notes": "",
    },
    {
        "team_id": "ESPANYOL",
        "autonomous_region_id": "CT",
        "autonomous_region_name": "Catalonia",
        "autonomous_region_slug": "catalonia",
        "region_aliases": "Catalonia|Catalunya|Cataluña",
        "notes": "",
    },
    {
        "team_id": "CELTA",
        "autonomous_region_id": "GA",
        "autonomous_region_name": "Galicia",
        "autonomous_region_slug": "galicia",
        "region_aliases": "Galicia|Galiza",
        "notes": "",
    },
    {
        "team_id": "ATLETICO_DE_MADRID",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
        "region_aliases": "Madrid|Community of Madrid|Comunidad de Madrid|Madrid region|Region of Madrid",
        "notes": "",
    },
    {
        "team_id": "BARCELONA",
        "autonomous_region_id": "CT",
        "autonomous_region_name": "Catalonia",
        "autonomous_region_slug": "catalonia",
        "region_aliases": "Catalonia|Catalunya|Cataluña",
        "notes": "",
    },
    {
        "team_id": "REAL_SOCIEDAD",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
        "region_aliases": "Basque Country|País Vasco|Euskadi|Euskal Herria",
        "notes": "",
    },
    {
        "team_id": "SEVILLA",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
        "region_aliases": "Andalusia|Andalucía|Andalucia",
        "notes": "",
    },
    {
        "team_id": "RAYO_VALLECANO",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
        "region_aliases": "Madrid|Community of Madrid|Comunidad de Madrid|Madrid region|Region of Madrid",
        "notes": "",
    },
    {
        "team_id": "VILLARREAL",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
        "region_aliases": "Valencian Community|Comunitat Valenciana|Comunidad Valenciana|Valencia region",
        "notes": "",
    },
    {
        "team_id": "GRANADA_CF",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
        "region_aliases": "Andalusia|Andalucía|Andalucia",
        "notes": "",
    },
    {
        "team_id": "ELCHE",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
        "region_aliases": "Valencian Community|Comunitat Valenciana|Comunidad Valenciana|Valencia region",
        "notes": "",
    },
    {
        "team_id": "ATHLETIC_CLUB",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
        "region_aliases": "Basque Country|País Vasco|Euskadi|Euskal Herria",
        "notes": "",
    },
]

write_csv("team_region_map_stage_4g.csv", team_region_map_fields, team_region_map_rows)

region_lookup = {
    row["team_id"]: row
    for row in team_region_map_rows
}

stage_4g_rows = []

try:
    team_index_file = EXPORT_DIR / "team_fixture_index_stage_4f.csv"

    with team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        team_index_rows = list(reader)

    for row in team_index_rows:
        team_region = region_lookup.get(row["team_id"], {})
        opponent_region = region_lookup.get(row["opponent_team_id"], {})

        row["team_autonomous_region_id"] = team_region.get("autonomous_region_id", "")
        row["team_autonomous_region_name"] = team_region.get("autonomous_region_name", "")
        row["team_autonomous_region_slug"] = team_region.get("autonomous_region_slug", "")

        row["opponent_autonomous_region_id"] = opponent_region.get("autonomous_region_id", "")
        row["opponent_autonomous_region_name"] = opponent_region.get("autonomous_region_name", "")
        row["opponent_autonomous_region_slug"] = opponent_region.get("autonomous_region_slug", "")

        stage_4g_rows.append(row)

except Exception as e:
    print(f"Stage 4G failed: {type(e).__name__}: {e}")

write_csv("team_fixture_index_stage_4g_with_regions.csv", stage_4f_fields, stage_4g_rows)

# Regional validation summary
regional_summary_fields = [
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
    "team_count_in_stage_4g_sample",
    "team_ids",
]

regional_summary = {}

for row in team_region_map_rows:
    region_id = row["autonomous_region_id"]

    if region_id not in regional_summary:
        regional_summary[region_id] = {
            "autonomous_region_id": row["autonomous_region_id"],
            "autonomous_region_name": row["autonomous_region_name"],
            "autonomous_region_slug": row["autonomous_region_slug"],
            "team_ids": set(),
        }

    regional_summary[region_id]["team_ids"].add(row["team_id"])

regional_summary_rows = []

for region in regional_summary.values():
    team_ids = sorted(region["team_ids"])

    regional_summary_rows.append({
        "autonomous_region_id": region["autonomous_region_id"],
        "autonomous_region_name": region["autonomous_region_name"],
        "autonomous_region_slug": region["autonomous_region_slug"],
        "team_count_in_stage_4g_sample": str(len(team_ids)),
        "team_ids": "|".join(team_ids),
    })

write_csv("regional_summary_stage_4g.csv", regional_summary_fields, regional_summary_rows)

print(f"Stage 4G generated {len(stage_4g_rows)} team fixture rows with autonomous region tags.")
# -----------------------------
# Stage 4G2: Correct region tags using exact LaLiga team IDs
# -----------------------------

team_region_map_stage_4g2_rows = [
    {
        "team_id": "VALENCIA_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
    },
    {
        "team_id": "GETAFE_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
    },
    {
        "team_id": "REAL_CLUB_DEPORTIVO_MALLORCA_SAD",
        "autonomous_region_id": "IB",
        "autonomous_region_name": "Balearic Islands",
        "autonomous_region_slug": "balearic-islands",
    },
    {
        "team_id": "REAL_BETIS_BALOMPIE_SAD",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
    },
    {
        "team_id": "CADIZ_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
    },
    {
        "team_id": "LEVANTE_UNION_DEPORTIVA_SAD",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
    },
    {
        "team_id": "DEPORTIVO_ALAVES_SAD",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
    },
    {
        "team_id": "REAL_MADRID_CLUB_DE_FUTBOL",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
    },
    {
        "team_id": "CLUB_ATLETICO_OSASUNA",
        "autonomous_region_id": "NC",
        "autonomous_region_name": "Navarre",
        "autonomous_region_slug": "navarre",
    },
    {
        "team_id": "RCD_ESPANYOL_DE_BARCELONA",
        "autonomous_region_id": "CT",
        "autonomous_region_name": "Catalonia",
        "autonomous_region_slug": "catalonia",
    },
    {
        "team_id": "REAL_CLUB_CELTA_DE_VIGO_SAD",
        "autonomous_region_id": "GA",
        "autonomous_region_name": "Galicia",
        "autonomous_region_slug": "galicia",
    },
    {
        "team_id": "CLUB_ATLETICO_DE_MADRID_SAD",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
    },
    {
        "team_id": "FUTBOL_CLUB_BARCELONA",
        "autonomous_region_id": "CT",
        "autonomous_region_name": "Catalonia",
        "autonomous_region_slug": "catalonia",
    },
    {
        "team_id": "REAL_SOCIEDAD_DE_FUTBOL_SAD",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
    },
    {
        "team_id": "SEVILLA_FUTBOL_CLUB_SAD",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
    },
    {
        "team_id": "RAYO_VALLECANO_DE_MADRID_SAD",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
    },
    {
        "team_id": "VILLARREAL_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
    },
    {
        "team_id": "GRANADA_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
    },
    {
        "team_id": "ELCHE_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
    },
    {
        "team_id": "ATHLETIC_CLUB",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
    },
]

team_region_map_stage_4g2_fields = [
    "team_id",
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
]

write_csv(
    "team_region_map_stage_4g2_exact_laliga_ids.csv",
    team_region_map_stage_4g2_fields,
    team_region_map_stage_4g2_rows,
)

region_lookup_4g2 = {
    row["team_id"]: row
    for row in team_region_map_stage_4g2_rows
}

stage_4g2_rows = []

try:
    team_index_file = EXPORT_DIR / "team_fixture_index_stage_4f.csv"

    with team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        team_index_rows = list(reader)

    for row in team_index_rows:
        team_region = region_lookup_4g2.get(row["team_id"], {})
        opponent_region = region_lookup_4g2.get(row["opponent_team_id"], {})

        row["team_autonomous_region_id"] = team_region.get("autonomous_region_id", "")
        row["team_autonomous_region_name"] = team_region.get("autonomous_region_name", "")
        row["team_autonomous_region_slug"] = team_region.get("autonomous_region_slug", "")

        row["opponent_autonomous_region_id"] = opponent_region.get("autonomous_region_id", "")
        row["opponent_autonomous_region_name"] = opponent_region.get("autonomous_region_name", "")
        row["opponent_autonomous_region_slug"] = opponent_region.get("autonomous_region_slug", "")

        stage_4g2_rows.append(row)

except Exception as e:
    print(f"Stage 4G2 failed: {type(e).__name__}: {e}")

write_csv(
    "team_fixture_index_stage_4g2_with_regions.csv",
    stage_4f_fields,
    stage_4g2_rows,
)

print(f"Stage 4G2 generated {len(stage_4g2_rows)} team fixture rows with corrected region tags.")
# -----------------------------
# Stage 5A: Extract Primera División 2021/22 matchdays 1-3
# -----------------------------

stage_5a_raw_fields = [
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

stage_5a_raw_rows = []

season_id = "2021-22"
competition_id = "PRIMERA_DIVISION"
competition_name = "Primera División"

for matchday in range(1, 4):
    source_url = f"https://www.laliga.com/laliga-easports/resultados/{season_id}/jornada-{matchday}"

    try:
        request = urllib.request.Request(
            source_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not next_data_match:
            stage_5a_raw_rows.append({
                "source_url": source_url,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "matchday": str(matchday),
                "fixture_date": "",
                "home_team_name_source": "",
                "away_team_name_source": "",
                "home_score": "",
                "away_score": "",
                "extraction_method": "failed_no_next_data",
                "data_confidence": "failed",
                "notes": "No __NEXT_DATA__ JSON found.",
            })
            continue

        next_data = json.loads(next_data_match.group(1))
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

            stage_5a_raw_rows.append({
                "source_url": source_url,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "matchday": str(matchday),
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
        stage_5a_raw_rows.append({
            "source_url": source_url,
            "season_id": season_id,
            "competition_id": competition_id,
            "competition_name": competition_name,
            "matchday": str(matchday),
            "fixture_date": "",
            "home_team_name_source": "",
            "away_team_name_source": "",
            "home_score": "",
            "away_score": "",
            "extraction_method": "failed",
            "data_confidence": "failed",
            "notes": f"Error: {type(e).__name__}: {e}",
        })

write_csv("stage_5a_primera_2021_22_j1_to_j3_raw.csv", stage_5a_raw_fields, stage_5a_raw_rows)

print(f"Stage 5A extracted {len(stage_5a_raw_rows)} raw fixture rows.")
# -----------------------------
# Stage 5B: Convert Primera División 2021/22 matchdays 1-3 raw rows into app fixture rows
# -----------------------------

stage_5b_fields = [
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

stage_5b_rows = []

try:
    raw_file = EXPORT_DIR / "stage_5a_primera_2021_22_j1_to_j3_raw.csv"

    with raw_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    for row in raw_rows:
        if row.get("data_confidence") == "failed":
            continue

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

        stage_5b_rows.append({
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
            "notes": "Generated from Stage 5A Primera División 2021/22 matchdays 1-3 extraction.",
        })

except Exception as e:
    stage_5b_rows.append({
        "fixture_id": "",
        "season_id": "2021-22",
        "competition_id": "PRIMERA_DIVISION",
        "competition_name": "Primera División",
        "competition_level": "1",
        "competition_group": "",
        "matchday": "",
        "round_label": "",
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
        "source_url": "",
        "source_retrieved_at": NOW,
        "data_confidence": "failed",
        "notes": f"Stage 5B failed: {type(e).__name__}: {e}",
    })

write_csv(
    "fixtures_results_stage_5b_primera_2021_22_j1_to_j3.csv",
    stage_5b_fields,
    stage_5b_rows,
)

print(f"Stage 5B generated {len(stage_5b_rows)} app fixture rows.")
# -----------------------------
# Stage 5C: Build team fixture index for Primera División 2021/22 matchdays 1-3
# -----------------------------

stage_5c_fields = [
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

stage_5c_rows = []

try:
    fixtures_file = EXPORT_DIR / "fixtures_results_stage_5b_primera_2021_22_j1_to_j3.csv"

    with fixtures_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fixtures = list(reader)

    for fixture in fixtures:
        fixture_id = fixture["fixture_id"]

        home_team_id = fixture["home_team_id"]
        away_team_id = fixture["away_team_id"]

        home_score = fixture["home_score"]
        away_score = fixture["away_score"]

        # Home team row
        stage_5c_rows.append({
            "team_fixture_id": f"{fixture_id}__{home_team_id}",
            "fixture_id": fixture_id,
            "team_id": home_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": away_team_id,
            "home_or_away": "Home",
            "team_score": home_score,
            "opponent_score": away_score,
            "result_for_team": result_for_team(home_score, away_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "true",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

        # Away team row
        stage_5c_rows.append({
            "team_fixture_id": f"{fixture_id}__{away_team_id}",
            "fixture_id": fixture_id,
            "team_id": away_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": home_team_id,
            "home_or_away": "Away",
            "team_score": away_score,
            "opponent_score": home_score,
            "result_for_team": result_for_team(away_score, home_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "false",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

except Exception as e:
    print(f"Stage 5C failed: {type(e).__name__}: {e}")

write_csv(
    "team_fixture_index_stage_5c_primera_2021_22_j1_to_j3.csv",
    stage_5c_fields,
    stage_5c_rows,
)

print(f"Stage 5C generated {len(stage_5c_rows)} team fixture index rows.")
# -----------------------------
# Stage 5D: Add autonomous region tags to Primera División 2021/22 matchdays 1-3 team fixture index
# -----------------------------

stage_5d_rows = []

try:
    # Use the corrected exact LaLiga team ID region map from Stage 4G2
    region_map_file = EXPORT_DIR / "team_region_map_stage_4g2_exact_laliga_ids.csv"

    with region_map_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        region_map_rows = list(reader)

    region_lookup = {
        row["team_id"]: row
        for row in region_map_rows
    }

    team_index_file = EXPORT_DIR / "team_fixture_index_stage_5c_primera_2021_22_j1_to_j3.csv"

    with team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        team_index_rows = list(reader)

    for row in team_index_rows:
        team_region = region_lookup.get(row["team_id"], {})
        opponent_region = region_lookup.get(row["opponent_team_id"], {})

        row["team_autonomous_region_id"] = team_region.get("autonomous_region_id", "")
        row["team_autonomous_region_name"] = team_region.get("autonomous_region_name", "")
        row["team_autonomous_region_slug"] = team_region.get("autonomous_region_slug", "")

        row["opponent_autonomous_region_id"] = opponent_region.get("autonomous_region_id", "")
        row["opponent_autonomous_region_name"] = opponent_region.get("autonomous_region_name", "")
        row["opponent_autonomous_region_slug"] = opponent_region.get("autonomous_region_slug", "")

        stage_5d_rows.append(row)

except Exception as e:
    print(f"Stage 5D failed: {type(e).__name__}: {e}")

write_csv(
    "team_fixture_index_stage_5d_primera_2021_22_j1_to_j3_with_regions.csv",
    stage_5c_fields,
    stage_5d_rows,
)

# -----------------------------
# Stage 5D validation summary
# -----------------------------

stage_5d_validation_fields = [
    "check_name",
    "result",
    "details",
]

missing_team_regions = [
    row for row in stage_5d_rows
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_5d_rows
    if not row.get("opponent_autonomous_region_id")
]

unique_regions = sorted(set(
    row["team_autonomous_region_name"]
    for row in stage_5d_rows
    if row.get("team_autonomous_region_name")
))

stage_5d_validation_rows = [
    {
        "check_name": "team_fixture_index_rows",
        "result": str(len(stage_5d_rows)),
        "details": "Expected 60 rows for 30 fixtures.",
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "Expected 0.",
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "Expected 0.",
    },
    {
        "check_name": "unique_regions_in_sample",
        "result": str(len(unique_regions)),
        "details": "|".join(unique_regions),
    },
]

write_csv(
    "stage_5d_region_validation_summary.csv",
    stage_5d_validation_fields,
    stage_5d_validation_rows,
)

print(f"Stage 5D generated {len(stage_5d_rows)} team fixture rows with autonomous region tags.")
# -----------------------------
# Stage 6A: Extract all Primera División 2021/22 matchdays 1-38
# -----------------------------

stage_6a_raw_fields = [
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

stage_6a_raw_rows = []

season_id = "2021-22"
competition_id = "PRIMERA_DIVISION"
competition_name = "Primera División"

for matchday in range(1, 39):
    source_url = f"https://www.laliga.com/laliga-easports/resultados/{season_id}/jornada-{matchday}"

    try:
        request = urllib.request.Request(
            source_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not next_data_match:
            stage_6a_raw_rows.append({
                "source_url": source_url,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "matchday": str(matchday),
                "fixture_date": "",
                "home_team_name_source": "",
                "away_team_name_source": "",
                "home_score": "",
                "away_score": "",
                "extraction_method": "failed_no_next_data",
                "data_confidence": "failed",
                "notes": "No __NEXT_DATA__ JSON found.",
            })
            continue

        next_data = json.loads(next_data_match.group(1))
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

            stage_6a_raw_rows.append({
                "source_url": source_url,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "matchday": str(matchday),
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
        stage_6a_raw_rows.append({
            "source_url": source_url,
            "season_id": season_id,
            "competition_id": competition_id,
            "competition_name": competition_name,
            "matchday": str(matchday),
            "fixture_date": "",
            "home_team_name_source": "",
            "away_team_name_source": "",
            "home_score": "",
            "away_score": "",
            "extraction_method": "failed",
            "data_confidence": "failed",
            "notes": f"Error: {type(e).__name__}: {e}",
        })

write_csv(
    "stage_6a_primera_2021_22_j1_to_j38_raw.csv",
    stage_6a_raw_fields,
    stage_6a_raw_rows,
)

# Basic extraction validation
stage_6a_validation_fields = [
    "check_name",
    "result",
    "details",
]

failed_rows = [
    row for row in stage_6a_raw_rows
    if row.get("data_confidence") == "failed"
]

stage_6a_validation_rows = [
    {
        "check_name": "raw_fixture_rows",
        "result": str(len(stage_6a_raw_rows)),
        "details": "Expected 380 rows for 38 matchdays x 10 fixtures.",
    },
    {
        "check_name": "failed_rows",
        "result": str(len(failed_rows)),
        "details": "Expected 0.",
    },
]

write_csv(
    "stage_6a_primera_2021_22_validation_summary.csv",
    stage_6a_validation_fields,
    stage_6a_validation_rows,
)

print(f"Stage 6A extracted {len(stage_6a_raw_rows)} raw fixture rows.")
# -----------------------------
# Stage 6B: Convert full Primera División 2021/22 raw rows into app fixture rows
# -----------------------------

stage_6b_fields = [
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

stage_6b_rows = []

try:
    raw_file = EXPORT_DIR / "stage_6a_primera_2021_22_j1_to_j38_raw.csv"

    with raw_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    for row in raw_rows:
        if row.get("data_confidence") == "failed":
            continue

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

        stage_6b_rows.append({
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
            "notes": "Generated from Stage 6A full Primera División 2021/22 extraction.",
        })

except Exception as e:
    stage_6b_rows.append({
        "fixture_id": "",
        "season_id": "2021-22",
        "competition_id": "PRIMERA_DIVISION",
        "competition_name": "Primera División",
        "competition_level": "1",
        "competition_group": "",
        "matchday": "",
        "round_label": "",
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
        "source_url": "",
        "source_retrieved_at": NOW,
        "data_confidence": "failed",
        "notes": f"Stage 6B failed: {type(e).__name__}: {e}",
    })

write_csv(
    "fixtures_results_stage_6b_primera_2021_22_full.csv",
    stage_6b_fields,
    stage_6b_rows,
)

# -----------------------------
# Stage 6B validation summary
# -----------------------------

stage_6b_validation_fields = [
    "check_name",
    "result",
    "details",
]

fixture_ids = [
    row["fixture_id"]
    for row in stage_6b_rows
    if row.get("fixture_id")
]

duplicate_fixture_ids = sorted([
    fixture_id
    for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

failed_rows = [
    row for row in stage_6b_rows
    if row.get("data_confidence") == "failed"
]

stage_6b_validation_rows = [
    {
        "check_name": "fixture_rows",
        "result": str(len(stage_6b_rows)),
        "details": "Expected 380 rows for full Primera División 2021/22.",
    },
    {
        "check_name": "failed_rows",
        "result": str(len(failed_rows)),
        "details": "Expected 0.",
    },
    {
        "check_name": "duplicate_fixture_ids",
        "result": str(len(duplicate_fixture_ids)),
        "details": "|".join(duplicate_fixture_ids),
    },
]

write_csv(
    "stage_6b_primera_2021_22_validation_summary.csv",
    stage_6b_validation_fields,
    stage_6b_validation_rows,
)

print(f"Stage 6B generated {len(stage_6b_rows)} full app fixture rows.")
# -----------------------------
# Stage 6C: Build team fixture index for full Primera División 2021/22
# -----------------------------

stage_6c_fields = [
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

stage_6c_rows = []

try:
    fixtures_file = EXPORT_DIR / "fixtures_results_stage_6b_primera_2021_22_full.csv"

    with fixtures_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fixtures = list(reader)

    for fixture in fixtures:
        fixture_id = fixture["fixture_id"]

        home_team_id = fixture["home_team_id"]
        away_team_id = fixture["away_team_id"]

        home_score = fixture["home_score"]
        away_score = fixture["away_score"]

        # Home team row
        stage_6c_rows.append({
            "team_fixture_id": f"{fixture_id}__{home_team_id}",
            "fixture_id": fixture_id,
            "team_id": home_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": away_team_id,
            "home_or_away": "Home",
            "team_score": home_score,
            "opponent_score": away_score,
            "result_for_team": result_for_team(home_score, away_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "true",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

        # Away team row
        stage_6c_rows.append({
            "team_fixture_id": f"{fixture_id}__{away_team_id}",
            "fixture_id": fixture_id,
            "team_id": away_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": home_team_id,
            "home_or_away": "Away",
            "team_score": away_score,
            "opponent_score": home_score,
            "result_for_team": result_for_team(away_score, home_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "false",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

except Exception as e:
    print(f"Stage 6C failed: {type(e).__name__}: {e}")

write_csv(
    "team_fixture_index_stage_6c_primera_2021_22_full.csv",
    stage_6c_fields,
    stage_6c_rows,
)

# -----------------------------
# Stage 6C validation summary
# -----------------------------

stage_6c_validation_fields = [
    "check_name",
    "result",
    "details",
]

team_fixture_ids = [
    row["team_fixture_id"]
    for row in stage_6c_rows
    if row.get("team_fixture_id")
]

duplicate_team_fixture_ids = sorted([
    team_fixture_id
    for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

stage_6c_validation_rows = [
    {
        "check_name": "team_fixture_index_rows",
        "result": str(len(stage_6c_rows)),
        "details": "Expected 760 rows for 380 fixtures.",
    },
    {
        "check_name": "duplicate_team_fixture_ids",
        "result": str(len(duplicate_team_fixture_ids)),
        "details": "|".join(duplicate_team_fixture_ids),
    },
]

write_csv(
    "stage_6c_primera_2021_22_validation_summary.csv",
    stage_6c_validation_fields,
    stage_6c_validation_rows,
)

print(f"Stage 6C generated {len(stage_6c_rows)} full team fixture index rows.")
# -----------------------------
# Stage 6D: Add autonomous region tags to full Primera División 2021/22 team fixture index
# -----------------------------

stage_6d_rows = []

try:
    # Use the corrected exact LaLiga team ID region map from Stage 4G2
    region_map_file = EXPORT_DIR / "team_region_map_stage_4g2_exact_laliga_ids.csv"

    with region_map_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        region_map_rows = list(reader)

    region_lookup = {
        row["team_id"]: row
        for row in region_map_rows
    }

    team_index_file = EXPORT_DIR / "team_fixture_index_stage_6c_primera_2021_22_full.csv"

    with team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        team_index_rows = list(reader)

    for row in team_index_rows:
        team_region = region_lookup.get(row["team_id"], {})
        opponent_region = region_lookup.get(row["opponent_team_id"], {})

        row["team_autonomous_region_id"] = team_region.get("autonomous_region_id", "")
        row["team_autonomous_region_name"] = team_region.get("autonomous_region_name", "")
        row["team_autonomous_region_slug"] = team_region.get("autonomous_region_slug", "")

        row["opponent_autonomous_region_id"] = opponent_region.get("autonomous_region_id", "")
        row["opponent_autonomous_region_name"] = opponent_region.get("autonomous_region_name", "")
        row["opponent_autonomous_region_slug"] = opponent_region.get("autonomous_region_slug", "")

        stage_6d_rows.append(row)

except Exception as e:
    print(f"Stage 6D failed: {type(e).__name__}: {e}")

write_csv(
    "team_fixture_index_stage_6d_primera_2021_22_full_with_regions.csv",
    stage_6c_fields,
    stage_6d_rows,
)

# -----------------------------
# Stage 6D validation summary
# -----------------------------

stage_6d_validation_fields = [
    "check_name",
    "result",
    "details",
]
# -----------------------------
# Stage 7A: Extract Segunda División 2021/22 matchdays 1-3
# -----------------------------

stage_7a_raw_fields = [
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

stage_7a_raw_rows = []

season_id = "2021-22"
competition_id = "SEGUNDA_DIVISION"
competition_name = "Segunda División"

for matchday in range(1, 4):
    source_url = f"https://www.laliga.com/laliga-hypermotion/resultados/{season_id}/jornada-{matchday}"

    try:
        request = urllib.request.Request(
            source_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not next_data_match:
            stage_7a_raw_rows.append({
                "source_url": source_url,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "matchday": str(matchday),
                "fixture_date": "",
                "home_team_name_source": "",
                "away_team_name_source": "",
                "home_score": "",
                "away_score": "",
                "extraction_method": "failed_no_next_data",
                "data_confidence": "failed",
                "notes": "No __NEXT_DATA__ JSON found.",
            })
            continue

        next_data = json.loads(next_data_match.group(1))
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

            stage_7a_raw_rows.append({
                "source_url": source_url,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "matchday": str(matchday),
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
        stage_7a_raw_rows.append({
            "source_url": source_url,
            "season_id": season_id,
            "competition_id": competition_id,
            "competition_name": competition_name,
            "matchday": str(matchday),
            "fixture_date": "",
            "home_team_name_source": "",
            "away_team_name_source": "",
            "home_score": "",
            "away_score": "",
            "extraction_method": "failed",
            "data_confidence": "failed",
            "notes": f"Error: {type(e).__name__}: {e}",
        })

write_csv(
    "stage_7a_segunda_2021_22_j1_to_j3_raw.csv",
    stage_7a_raw_fields,
    stage_7a_raw_rows,
)

# -----------------------------
# Stage 7A validation summary
# -----------------------------

stage_7a_validation_fields = [
    "check_name",
    "result",
    "details",
]

failed_rows = [
    row for row in stage_7a_raw_rows
    if row.get("data_confidence") == "failed"
]

stage_7a_validation_rows = [
    {
        "check_name": "raw_fixture_rows",
        "result": str(len(stage_7a_raw_rows)),
        "details": "Expected 33 rows for 3 matchdays x 11 fixtures.",
    },
    {
        "check_name": "failed_rows",
        "result": str(len(failed_rows)),
        "details": "Expected 0.",
    },
]

write_csv(
    "stage_7a_segunda_2021_22_validation_summary.csv",
    stage_7a_validation_fields,
    stage_7a_validation_rows,
)

print(f"Stage 7A extracted {len(stage_7a_raw_rows)} raw Segunda fixture rows.")
missing_team_regions = [
    row for row in stage_6d_rows
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_6d_rows
    if not row.get("opponent_autonomous_region_id")
]

unique_regions = sorted(set(
    row["team_autonomous_region_name"]
    for row in stage_6d_rows
    if row.get("team_autonomous_region_name")
))

teams_missing_regions = sorted(set(
    row["team_id"]
    for row in missing_team_regions
    if row.get("team_id")
))

opponents_missing_regions = sorted(set(
    row["opponent_team_id"]
    for row in missing_opponent_regions
    if row.get("opponent_team_id")
))

stage_6d_validation_rows = [
    {
        "check_name": "team_fixture_index_rows",
        "result": str(len(stage_6d_rows)),
        "details": "Expected 760 rows.",
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "|".join(teams_missing_regions),
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "|".join(opponents_missing_regions),
    },
    {
        "check_name": "unique_regions_in_full_2021_22_primera",
        "result": str(len(unique_regions)),
        "details": "|".join(unique_regions),
    },
]

write_csv(
    "stage_6d_region_validation_summary.csv",
    stage_6d_validation_fields,
    stage_6d_validation_rows,
)

print(f"Stage 6D generated {len(stage_6d_rows)} full team fixture rows with autonomous region tags.")
# -----------------------------
# Stage 7B: Convert Segunda División 2021/22 matchdays 1-3 raw rows into app fixture rows
# -----------------------------

stage_7b_fields = [
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

stage_7b_rows = []

try:
    raw_file = EXPORT_DIR / "stage_7a_segunda_2021_22_j1_to_j3_raw.csv"

    with raw_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    for row in raw_rows:
        if row.get("data_confidence") == "failed":
            continue

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

        stage_7b_rows.append({
            "fixture_id": fixture_id,
            "season_id": row["season_id"],
            "competition_id": row["competition_id"],
            "competition_name": row["competition_name"],
            "competition_level": "2",
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
            "notes": "Generated from Stage 7A Segunda División 2021/22 matchdays 1-3 extraction.",
        })

except Exception as e:
    stage_7b_rows.append({
        "fixture_id": "",
        "season_id": "2021-22",
        "competition_id": "SEGUNDA_DIVISION",
        "competition_name": "Segunda División",
        "competition_level": "2",
        "competition_group": "",
        "matchday": "",
        "round_label": "",
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
        "source_url": "",
        "source_retrieved_at": NOW,
        "data_confidence": "failed",
        "notes": f"Stage 7B failed: {type(e).__name__}: {e}",
    })

write_csv(
    "fixtures_results_stage_7b_segunda_2021_22_j1_to_j3.csv",
    stage_7b_fields,
    stage_7b_rows,
)

# -----------------------------
# Stage 7B validation summary
# -----------------------------

stage_7b_validation_fields = [
    "check_name",
    "result",
    "details",
]

fixture_ids = [
    row["fixture_id"]
    for row in stage_7b_rows
    if row.get("fixture_id")
]

duplicate_fixture_ids = sorted([
    fixture_id
    for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

failed_rows = [
    row for row in stage_7b_rows
    if row.get("data_confidence") == "failed"
]

stage_7b_validation_rows = [
    {
        "check_name": "fixture_rows",
        "result": str(len(stage_7b_rows)),
        "details": "Expected 33 rows for Segunda División 2021/22 matchdays 1-3.",
    },
    {
        "check_name": "failed_rows",
        "result": str(len(failed_rows)),
        "details": "Expected 0.",
    },
    {
        "check_name": "duplicate_fixture_ids",
        "result": str(len(duplicate_fixture_ids)),
        "details": "|".join(duplicate_fixture_ids),
    },
]

write_csv(
    "stage_7b_segunda_2021_22_validation_summary.csv",
    stage_7b_validation_fields,
    stage_7b_validation_rows,
)

print(f"Stage 7B generated {len(stage_7b_rows)} Segunda app fixture rows.")
# -----------------------------
# Stage 7C: Build team fixture index for Segunda División 2021/22 matchdays 1-3
# -----------------------------

stage_7c_fields = [
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

stage_7c_rows = []

try:
    fixtures_file = EXPORT_DIR / "fixtures_results_stage_7b_segunda_2021_22_j1_to_j3.csv"

    with fixtures_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fixtures = list(reader)

    for fixture in fixtures:
        fixture_id = fixture["fixture_id"]

        home_team_id = fixture["home_team_id"]
        away_team_id = fixture["away_team_id"]

        home_score = fixture["home_score"]
        away_score = fixture["away_score"]

        # Home team row
        stage_7c_rows.append({
            "team_fixture_id": f"{fixture_id}__{home_team_id}",
            "fixture_id": fixture_id,
            "team_id": home_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": away_team_id,
            "home_or_away": "Home",
            "team_score": home_score,
            "opponent_score": away_score,
            "result_for_team": result_for_team(home_score, away_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "true",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

        # Away team row
        stage_7c_rows.append({
            "team_fixture_id": f"{fixture_id}__{away_team_id}",
            "fixture_id": fixture_id,
            "team_id": away_team_id,
            "season_id": fixture["season_id"],
            "competition_id": fixture["competition_id"],
            "competition_name": fixture["competition_name"],
            "competition_group": fixture["competition_group"],
            "matchday": fixture["matchday"],
            "fixture_date": fixture["fixture_date"],
            "opponent_team_id": home_team_id,
            "home_or_away": "Away",
            "team_score": away_score,
            "opponent_score": home_score,
            "result_for_team": result_for_team(away_score, home_score),
            "venue_id": fixture["venue_id"],
            "is_home_ground": "false",
            "team_autonomous_region_id": "",
            "team_autonomous_region_name": "",
            "team_autonomous_region_slug": "",
            "opponent_autonomous_region_id": "",
            "opponent_autonomous_region_name": "",
            "opponent_autonomous_region_slug": "",
            "source_url": fixture["source_url"],
        })

except Exception as e:
    print(f"Stage 7C failed: {type(e).__name__}: {e}")

write_csv(
    "team_fixture_index_stage_7c_segunda_2021_22_j1_to_j3.csv",
    stage_7c_fields,
    stage_7c_rows,
)

# -----------------------------
# Stage 7C validation summary
# -----------------------------

stage_7c_validation_fields = [
    "check_name",
    "result",
    "details",
]

team_fixture_ids = [
    row["team_fixture_id"]
    for row in stage_7c_rows
    if row.get("team_fixture_id")
]

duplicate_team_fixture_ids = sorted([
    team_fixture_id
    for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

stage_7c_validation_rows = [
    {
        "check_name": "team_fixture_index_rows",
        "result": str(len(stage_7c_rows)),
        "details": "Expected 66 rows for 33 fixtures.",
    },
    {
        "check_name": "duplicate_team_fixture_ids",
        "result": str(len(duplicate_team_fixture_ids)),
        "details": "|".join(duplicate_team_fixture_ids),
    },
]

write_csv(
    "stage_7c_segunda_2021_22_validation_summary.csv",
    stage_7c_validation_fields,
    stage_7c_validation_rows,
)

print(f"Stage 7C generated {len(stage_7c_rows)} Segunda team fixture index rows.")
# -----------------------------
# Stage 7D: Add autonomous region tags to Segunda División 2021/22 matchdays 1-3 team fixture index
# -----------------------------

stage_7d_region_map_fields = [
    "team_id",
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
]

stage_7d_region_map_rows = [
    {
        "team_id": "AGRUPACION_DEPORTIVA_ALCORCON_SAD",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
    },
    {
        "team_id": "BURGOS_CF",
        "autonomous_region_id": "CL",
        "autonomous_region_name": "Castile and León",
        "autonomous_region_slug": "castile-and-leon",
    },
    {
        "team_id": "CF_FUENLABRADA",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
    },
    {
        "team_id": "CLUB_DEPORTIVO_LEGANES_SAD",
        "autonomous_region_id": "MD",
        "autonomous_region_name": "Community of Madrid",
        "autonomous_region_slug": "community-of-madrid",
    },
    {
        "team_id": "CLUB_DEPORTIVO_LUGO_SAD",
        "autonomous_region_id": "GA",
        "autonomous_region_name": "Galicia",
        "autonomous_region_slug": "galicia",
    },
    {
        "team_id": "CLUB_DEPORTIVO_MIRANDES_SAD",
        "autonomous_region_id": "CL",
        "autonomous_region_name": "Castile and León",
        "autonomous_region_slug": "castile-and-leon",
    },
    {
        "team_id": "CLUB_DEPORTIVO_TENERIFE_SAD",
        "autonomous_region_id": "CN",
        "autonomous_region_name": "Canary Islands",
        "autonomous_region_slug": "canary-islands",
    },
    {
        "team_id": "FC_CARTAGENA",
        "autonomous_region_id": "MU",
        "autonomous_region_name": "Region of Murcia",
        "autonomous_region_slug": "region-of-murcia",
    },
    {
        "team_id": "GIRONA_FUTBOL_CLUB_SAD",
        "autonomous_region_id": "CT",
        "autonomous_region_name": "Catalonia",
        "autonomous_region_slug": "catalonia",
    },
    {
        "team_id": "MALAGA_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
    },
    {
        "team_id": "REAL_OVIEDO_SAD",
        "autonomous_region_id": "AS",
        "autonomous_region_name": "Asturias",
        "autonomous_region_slug": "asturias",
    },
    {
        "team_id": "REAL_SPORTING_DE_GIJON_SAD",
        "autonomous_region_id": "AS",
        "autonomous_region_name": "Asturias",
        "autonomous_region_slug": "asturias",
    },
    {
        "team_id": "REAL_VALLADOLID_CLUB_DE_FUTBOL_SAD",
        "autonomous_region_id": "CL",
        "autonomous_region_name": "Castile and León",
        "autonomous_region_slug": "castile-and-leon",
    },
    {
        "team_id": "REAL_ZARAGOZA_SAD",
        "autonomous_region_id": "AR",
        "autonomous_region_name": "Aragon",
        "autonomous_region_slug": "aragon",
    },
    {
        "team_id": "R_SOCIEDAD_B",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
    },
    {
        "team_id": "SD_AMOREBIETA",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
    },
    {
        "team_id": "SOCIEDAD_DEPORTIVA_EIBAR_SAD",
        "autonomous_region_id": "PV",
        "autonomous_region_name": "Basque Country",
        "autonomous_region_slug": "basque-country",
    },
    {
        "team_id": "SOCIEDAD_DEPORTIVA_HUESCA_SAD",
        "autonomous_region_id": "AR",
        "autonomous_region_name": "Aragon",
        "autonomous_region_slug": "aragon",
    },
    {
        "team_id": "SOCIEDAD_DEPORTIVA_PONFERRADINA_SAD",
        "autonomous_region_id": "CL",
        "autonomous_region_name": "Castile and León",
        "autonomous_region_slug": "castile-and-leon",
    },
    {
        "team_id": "UD_IBIZA",
        "autonomous_region_id": "IB",
        "autonomous_region_name": "Balearic Islands",
        "autonomous_region_slug": "balearic-islands",
    },
    {
        "team_id": "UNION_DEPORTIVA_ALMERIA_SAD",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
    },
    {
        "team_id": "UNION_DEPORTIVA_LAS_PALMAS_SAD",
        "autonomous_region_id": "CN",
        "autonomous_region_name": "Canary Islands",
        "autonomous_region_slug": "canary-islands",
    },
]

write_csv(
    "team_region_map_stage_7d_segunda_exact_laliga_ids.csv",
    stage_7d_region_map_fields,
    stage_7d_region_map_rows,
)

region_lookup_7d = {
    row["team_id"]: row
    for row in stage_7d_region_map_rows
}

stage_7d_rows = []

try:
    team_index_file = EXPORT_DIR / "team_fixture_index_stage_7c_segunda_2021_22_j1_to_j3.csv"

    with team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        team_index_rows = list(reader)

    for row in team_index_rows:
        team_region = region_lookup_7d.get(row["team_id"], {})
        opponent_region = region_lookup_7d.get(row["opponent_team_id"], {})

        row["team_autonomous_region_id"] = team_region.get("autonomous_region_id", "")
        row["team_autonomous_region_name"] = team_region.get("autonomous_region_name", "")
        row["team_autonomous_region_slug"] = team_region.get("autonomous_region_slug", "")

        row["opponent_autonomous_region_id"] = opponent_region.get("autonomous_region_id", "")
        row["opponent_autonomous_region_name"] = opponent_region.get("autonomous_region_name", "")
        row["opponent_autonomous_region_slug"] = opponent_region.get("autonomous_region_slug", "")

        stage_7d_rows.append(row)

except Exception as e:
    print(f"Stage 7D failed: {type(e).__name__}: {e}")

write_csv(
    "team_fixture_index_stage_7d_segunda_2021_22_j1_to_j3_with_regions.csv",
    stage_7c_fields,
    stage_7d_rows,
)

# -----------------------------
# Stage 7D validation summary
# -----------------------------

stage_7d_validation_fields = [
    "check_name",
    "result",
    "details",
]

missing_team_regions = [
    row for row in stage_7d_rows
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_7d_rows
    if not row.get("opponent_autonomous_region_id")
]

unique_regions = sorted(set(
    row["team_autonomous_region_name"]
    for row in stage_7d_rows
    if row.get("team_autonomous_region_name")
))

teams_missing_regions = sorted(set(
    row["team_id"]
    for row in missing_team_regions
    if row.get("team_id")
))

opponents_missing_regions = sorted(set(
    row["opponent_team_id"]
    for row in missing_opponent_regions
    if row.get("opponent_team_id")
))

stage_7d_validation_rows = [
    {
        "check_name": "team_fixture_index_rows",
        "result": str(len(stage_7d_rows)),
        "details": "Expected 66 rows.",
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "|".join(teams_missing_regions),
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "|".join(opponents_missing_regions),
    },
    {
        "check_name": "unique_regions_in_segunda_sample",
        "result": str(len(unique_regions)),
        "details": "|".join(unique_regions),
    },
]

write_csv(
    "stage_7d_segunda_region_validation_summary.csv",
    stage_7d_validation_fields,
    stage_7d_validation_rows,
)

print(f"Stage 7D generated {len(stage_7d_rows)} Segunda team fixture rows with autonomous region tags.")
# -----------------------------
# Stage 8A: LaLiga production runner for 2021/22 Primera + Segunda regular seasons
# -----------------------------

import urllib.request
import urllib.error
import re
import json

stage_8a_fixture_fields = [
    "fixture_id",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_level",
    "competition_group",
    "fixture_phase",
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

stage_8a_team_index_fields = [
    "team_fixture_id",
    "fixture_id",
    "team_id",
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "fixture_phase",
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

stage_8a_fixture_rows = []
stage_8a_team_index_rows = []
stage_8a_errors = []


def extract_laliga_regular_season(
    season_id,
    competition_id,
    competition_name,
    competition_level,
    url_competition_slug,
    matchday_count,
):
    extracted_rows = []

    for matchday in range(1, matchday_count + 1):
        source_url = f"https://www.laliga.com/{url_competition_slug}/resultados/{season_id}/jornada-{matchday}"

        try:
            request = urllib.request.Request(
                source_url,
                headers={
                    "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
                }
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                html = response.read().decode("utf-8", errors="ignore")

            next_data_match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                html,
                re.DOTALL
            )

            if not next_data_match:
                stage_8a_errors.append({
                    "competition_id": competition_id,
                    "matchday": str(matchday),
                    "source_url": source_url,
                    "error_type": "failed_no_next_data",
                    "error_message": "No __NEXT_DATA__ JSON found.",
                })
                continue

            next_data = json.loads(next_data_match.group(1))
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

                home_team_id = make_team_id(home_name)
                away_team_id = make_team_id(away_name)

                fixture_id = make_fixture_id(
                    season_id,
                    competition_id,
                    str(matchday),
                    home_team_id,
                    away_team_id,
                )

                extracted_rows.append({
                    "fixture_id": fixture_id,
                    "season_id": season_id,
                    "competition_id": competition_id,
                    "competition_name": competition_name,
                    "competition_level": competition_level,
                    "competition_group": "",
                    "fixture_phase": "regular_season",
                    "matchday": str(matchday),
                    "round_label": f"Jornada {matchday}",
                    "fixture_date": match.get("date", ""),
                    "kickoff_time_local": "",
                    "home_team_id": home_team_id,
                    "home_team_name_source": home_name,
                    "away_team_id": away_team_id,
                    "away_team_name_source": away_name,
                    "home_score": match.get("home_score", ""),
                    "away_score": match.get("away_score", ""),
                    "result_status": "played",
                    "venue_id": "",
                    "venue_name_source": "",
                    "attendance": "",
                    "referee": "",
                    "match_report_url": "",
                    "rfef_acta_url": "",
                    "laliga_match_url": "",
                    "source_system": "LaLiga",
                    "source_url": source_url,
                    "source_retrieved_at": NOW,
                    "data_confidence": "high",
                    "notes": "Generated by Stage 8A LaLiga production runner.",
                })

        except Exception as e:
            stage_8a_errors.append({
                "competition_id": competition_id,
                "matchday": str(matchday),
                "source_url": source_url,
                "error_type": type(e).__name__,
                "error_message": str(e),
            })

    return extracted_rows


# Extract Primera División 2021/22
stage_8a_fixture_rows.extend(
    extract_laliga_regular_season(
        season_id="2021-22",
        competition_id="PRIMERA_DIVISION",
        competition_name="Primera División",
        competition_level="1",
        url_competition_slug="laliga-easports",
        matchday_count=38,
    )
)

# Extract Segunda División 2021/22 regular season
stage_8a_fixture_rows.extend(
    extract_laliga_regular_season(
        season_id="2021-22",
        competition_id="SEGUNDA_DIVISION",
        competition_name="Segunda División",
        competition_level="2",
        url_competition_slug="laliga-hypermotion",
        matchday_count=42,
    )
)

write_csv(
    "laliga_production_2021_22_regular_fixtures_results.csv",
    stage_8a_fixture_fields,
    stage_8a_fixture_rows,
)


# -----------------------------
# Build combined region lookup
# -----------------------------

combined_region_lookup = {}

for region_map_filename in [
    "team_region_map_stage_4g2_exact_laliga_ids.csv",
    "team_region_map_stage_7d_segunda_exact_laliga_ids.csv",
]:
    region_map_file = EXPORT_DIR / region_map_filename

    if region_map_file.exists():
        with region_map_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                combined_region_lookup[row["team_id"]] = row


# -----------------------------
# Build team fixture index
# -----------------------------

for fixture in stage_8a_fixture_rows:
    fixture_id = fixture["fixture_id"]

    home_team_id = fixture["home_team_id"]
    away_team_id = fixture["away_team_id"]

    home_score = fixture["home_score"]
    away_score = fixture["away_score"]

    home_region = combined_region_lookup.get(home_team_id, {})
    away_region = combined_region_lookup.get(away_team_id, {})

    # Home team row
    stage_8a_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{home_team_id}",
        "fixture_id": fixture_id,
        "team_id": home_team_id,
        "season_id": fixture["season_id"],
        "competition_id": fixture["competition_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "fixture_phase": fixture["fixture_phase"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": away_team_id,
        "home_or_away": "Home",
        "team_score": home_score,
        "opponent_score": away_score,
        "result_for_team": result_for_team(home_score, away_score),
        "venue_id": fixture["venue_id"],
        "is_home_ground": "true",
        "team_autonomous_region_id": home_region.get("autonomous_region_id", ""),
        "team_autonomous_region_name": home_region.get("autonomous_region_name", ""),
        "team_autonomous_region_slug": home_region.get("autonomous_region_slug", ""),
        "opponent_autonomous_region_id": away_region.get("autonomous_region_id", ""),
        "opponent_autonomous_region_name": away_region.get("autonomous_region_name", ""),
        "opponent_autonomous_region_slug": away_region.get("autonomous_region_slug", ""),
        "source_url": fixture["source_url"],
    })

    # Away team row
    stage_8a_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{away_team_id}",
        "fixture_id": fixture_id,
        "team_id": away_team_id,
        "season_id": fixture["season_id"],
        "competition_id": fixture["competition_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "fixture_phase": fixture["fixture_phase"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": home_team_id,
        "home_or_away": "Away",
        "team_score": away_score,
        "opponent_score": home_score,
        "result_for_team": result_for_team(away_score, home_score),
        "venue_id": fixture["venue_id"],
        "is_home_ground": "false",
        "team_autonomous_region_id": away_region.get("autonomous_region_id", ""),
        "team_autonomous_region_name": away_region.get("autonomous_region_name", ""),
        "team_autonomous_region_slug": away_region.get("autonomous_region_slug", ""),
        "opponent_autonomous_region_id": home_region.get("autonomous_region_id", ""),
        "opponent_autonomous_region_name": home_region.get("autonomous_region_name", ""),
        "opponent_autonomous_region_slug": home_region.get("autonomous_region_slug", ""),
        "source_url": fixture["source_url"],
    })

write_csv(
    "laliga_production_2021_22_regular_team_fixture_index.csv",
    stage_8a_team_index_fields,
    stage_8a_team_index_rows,
)


# -----------------------------
# Stage 8A validation summary
# -----------------------------

stage_8a_validation_fields = [
    "check_name",
    "result",
    "details",
]

fixture_ids = [
    row["fixture_id"]
    for row in stage_8a_fixture_rows
    if row.get("fixture_id")
]

duplicate_fixture_ids = sorted([
    fixture_id
    for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

team_fixture_ids = [
    row["team_fixture_id"]
    for row in stage_8a_team_index_rows
    if row.get("team_fixture_id")
]

duplicate_team_fixture_ids = sorted([
    team_fixture_id
    for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

missing_team_regions = [
    row for row in stage_8a_team_index_rows
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_8a_team_index_rows
    if not row.get("opponent_autonomous_region_id")
]

teams_missing_regions = sorted(set(
    row["team_id"]
    for row in missing_team_regions
    if row.get("team_id")
))

opponents_missing_regions = sorted(set(
    row["opponent_team_id"]
    for row in missing_opponent_regions
    if row.get("opponent_team_id")
))

primera_fixture_count = len([
    row for row in stage_8a_fixture_rows
    if row["competition_id"] == "PRIMERA_DIVISION"
])

segunda_fixture_count = len([
    row for row in stage_8a_fixture_rows
    if row["competition_id"] == "SEGUNDA_DIVISION"
])

stage_8a_validation_rows = [
    {
        "check_name": "primera_fixture_rows",
        "result": str(primera_fixture_count),
        "details": "Expected 380.",
    },
    {
        "check_name": "segunda_regular_season_fixture_rows",
        "result": str(segunda_fixture_count),
        "details": "Expected 462.",
    },
    {
        "check_name": "total_fixture_rows",
        "result": str(len(stage_8a_fixture_rows)),
        "details": "Expected 842.",
    },
    {
        "check_name": "total_team_fixture_index_rows",
        "result": str(len(stage_8a_team_index_rows)),
        "details": "Expected 1684.",
    },
    {
        "check_name": "duplicate_fixture_ids",
        "result": str(len(duplicate_fixture_ids)),
        "details": "|".join(duplicate_fixture_ids),
    },
    {
        "check_name": "duplicate_team_fixture_ids",
        "result": str(len(duplicate_team_fixture_ids)),
        "details": "|".join(duplicate_team_fixture_ids),
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "|".join(teams_missing_regions),
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "|".join(opponents_missing_regions),
    },
    {
        "check_name": "extraction_errors",
        "result": str(len(stage_8a_errors)),
        "details": "See laliga_production_2021_22_regular_errors.csv if greater than 0.",
    },
]

write_csv(
    "laliga_production_2021_22_regular_validation_summary.csv",
    stage_8a_validation_fields,
    stage_8a_validation_rows,
)

error_fields = [
    "competition_id",
    "matchday",
    "source_url",
    "error_type",
    "error_message",
]

write_csv(
    "laliga_production_2021_22_regular_errors.csv",
    error_fields,
    stage_8a_errors,
)

print(f"Stage 8A production runner generated {len(stage_8a_fixture_rows)} fixture rows.")
print(f"Stage 8A production runner generated {len(stage_8a_team_index_rows)} team fixture index rows.")
# -----------------------------
# Stage 8B: Segunda División 2021/22 playoff discovery
# -----------------------------

stage_8b_discovery_fields = [
    "candidate_name",
    "candidate_url",
    "http_status",
    "success",
    "next_data_found",
    "matches_found",
    "match_count",
    "sample_home_team",
    "sample_away_team",
    "sample_home_score",
    "sample_away_score",
    "notes",
]

stage_8b_discovery_rows = []

playoff_candidate_urls = [
    {
        "candidate_name": "Segunda 2021-22 Playoff root",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/playoff",
    },
    {
        "candidate_name": "Segunda 2021-22 Playoffs root plural",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/playoffs",
    },
    {
        "candidate_name": "Segunda 2021-22 Promotion playoff",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/playoff-ascenso",
    },
    {
        "candidate_name": "Segunda 2021-22 Jornada 43",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/jornada-43",
    },
    {
        "candidate_name": "Segunda 2021-22 Jornada 44",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/jornada-44",
    },
    {
        "candidate_name": "Segunda 2021-22 Semi-final first leg",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/semifinal-ida",
    },
    {
        "candidate_name": "Segunda 2021-22 Semi-final second leg",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/semifinal-vuelta",
    },
    {
        "candidate_name": "Segunda 2021-22 Final first leg",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/final-ida",
    },
    {
        "candidate_name": "Segunda 2021-22 Final second leg",
        "candidate_url": "https://www.laliga.com/laliga-hypermotion/resultados/2021-22/final-vuelta",
    },
]

for candidate in playoff_candidate_urls:
    candidate_name = candidate["candidate_name"]
    candidate_url = candidate["candidate_url"]

    try:
        request = urllib.request.Request(
            candidate_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            status_code = response.getcode()
            html = response.read().decode("utf-8", errors="ignore")

        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        next_data_found = bool(next_data_match)
        matches_found = False
        match_count = 0
        sample_home_team = ""
        sample_away_team = ""
        sample_home_score = ""
        sample_away_score = ""
        notes = ""

        if next_data_match:
            try:
                next_data = json.loads(next_data_match.group(1))
                matches = next_data.get("props", {}).get("pageProps", {}).get("matches", [])

                if isinstance(matches, list) and matches:
                    matches_found = True
                    match_count = len(matches)

                    sample_match = matches[0]
                    sample_home = sample_match.get("home_team", {})
                    sample_away = sample_match.get("away_team", {})

                    sample_home_team = (
                        sample_home.get("name")
                        or sample_home.get("nickname")
                        or sample_home.get("short_name")
                        or ""
                    )

                    sample_away_team = (
                        sample_away.get("name")
                        or sample_away.get("nickname")
                        or sample_away.get("short_name")
                        or ""
                    )

                    sample_home_score = str(sample_match.get("home_score", ""))
                    sample_away_score = str(sample_match.get("away_score", ""))

                    # Save any promising playoff JSON for inspection
                    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", candidate_name).strip("_").lower()
                    playoff_json_path = EXPORT_DIR / f"stage_8b_{safe_name}.json"
                    playoff_json_path.write_text(
                        json.dumps(next_data, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                else:
                    notes = "NEXT_DATA found, but props.pageProps.matches was empty or missing."

            except Exception as e:
                notes = f"NEXT_DATA found, but JSON parse or match inspection failed: {type(e).__name__}: {e}"

        else:
            notes = "No __NEXT_DATA__ JSON found."

        stage_8b_discovery_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": str(status_code),
            "success": str(status_code == 200).lower(),
            "next_data_found": str(next_data_found).lower(),
            "matches_found": str(matches_found).lower(),
            "match_count": str(match_count),
            "sample_home_team": sample_home_team,
            "sample_away_team": sample_away_team,
            "sample_home_score": sample_home_score,
            "sample_away_score": sample_away_score,
            "notes": notes,
        })

    except urllib.error.HTTPError as e:
        stage_8b_discovery_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": str(e.code),
            "success": "false",
            "next_data_found": "false",
            "matches_found": "false",
            "match_count": "0",
            "sample_home_team": "",
            "sample_away_team": "",
            "sample_home_score": "",
            "sample_away_score": "",
            "notes": f"HTTPError: {e.reason}",
        })

    except Exception as e:
        stage_8b_discovery_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": "",
            "success": "false",
            "next_data_found": "false",
            "matches_found": "false",
            "match_count": "0",
            "sample_home_team": "",
            "sample_away_team": "",
            "sample_home_score": "",
            "sample_away_score": "",
            "notes": f"Error: {type(e).__name__}: {e}",
        })

write_csv(
    "stage_8b_segunda_2021_22_playoff_discovery.csv",
    stage_8b_discovery_fields,
    stage_8b_discovery_rows,
)

print("Stage 8B Segunda playoff discovery complete.")
# -----------------------------
# Stage 8C: Segunda División 2021/22 playoff final discovery
# -----------------------------

stage_8c_discovery_fields = [
    "candidate_name",
    "candidate_url",
    "http_status",
    "success",
    "next_data_found",
    "matches_found",
    "match_count",
    "sample_home_team",
    "sample_away_team",
    "sample_home_score",
    "sample_away_score",
    "notes",
]

stage_8c_discovery_rows = []

playoff_final_candidate_urls = []

for jornada in range(45, 49):
    playoff_final_candidate_urls.append({
        "candidate_name": f"Segunda 2021-22 Jornada {jornada}",
        "candidate_url": f"https://www.laliga.com/laliga-hypermotion/resultados/2021-22/jornada-{jornada}",
    })

for candidate in playoff_final_candidate_urls:
    candidate_name = candidate["candidate_name"]
    candidate_url = candidate["candidate_url"]

    try:
        request = urllib.request.Request(
            candidate_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            status_code = response.getcode()
            html = response.read().decode("utf-8", errors="ignore")

        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        next_data_found = bool(next_data_match)
        matches_found = False
        match_count = 0
        sample_home_team = ""
        sample_away_team = ""
        sample_home_score = ""
        sample_away_score = ""
        notes = ""

        if next_data_match:
            try:
                next_data = json.loads(next_data_match.group(1))
                matches = next_data.get("props", {}).get("pageProps", {}).get("matches", [])

                if isinstance(matches, list) and matches:
                    matches_found = True
                    match_count = len(matches)

                    sample_match = matches[0]
                    sample_home = sample_match.get("home_team", {})
                    sample_away = sample_match.get("away_team", {})

                    sample_home_team = (
                        sample_home.get("name")
                        or sample_home.get("nickname")
                        or sample_home.get("short_name")
                        or ""
                    )

                    sample_away_team = (
                        sample_away.get("name")
                        or sample_away.get("nickname")
                        or sample_away.get("short_name")
                        or ""
                    )

                    sample_home_score = str(sample_match.get("home_score", ""))
                    sample_away_score = str(sample_match.get("away_score", ""))

                    safe_name = re.sub(r"[^A-Za-z0-9]+", "_", candidate_name).strip("_").lower()
                    playoff_json_path = EXPORT_DIR / f"stage_8c_{safe_name}.json"
                    playoff_json_path.write_text(
                        json.dumps(next_data, ensure_ascii=False, indent=2),
                        encoding="utf-8",
                    )
                else:
                    notes = "NEXT_DATA found, but props.pageProps.matches was empty or missing."

            except Exception as e:
                notes = f"NEXT_DATA found, but JSON parse or match inspection failed: {type(e).__name__}: {e}"

        else:
            notes = "No __NEXT_DATA__ JSON found."

        stage_8c_discovery_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": str(status_code),
            "success": str(status_code == 200).lower(),
            "next_data_found": str(next_data_found).lower(),
            "matches_found": str(matches_found).lower(),
            "match_count": str(match_count),
            "sample_home_team": sample_home_team,
            "sample_away_team": sample_away_team,
            "sample_home_score": sample_home_score,
            "sample_away_score": sample_away_score,
            "notes": notes,
        })

    except urllib.error.HTTPError as e:
        stage_8c_discovery_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": str(e.code),
            "success": "false",
            "next_data_found": "false",
            "matches_found": "false",
            "match_count": "0",
            "sample_home_team": "",
            "sample_away_team": "",
            "sample_home_score": "",
            "sample_away_score": "",
            "notes": f"HTTPError: {e.reason}",
        })

    except Exception as e:
        stage_8c_discovery_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": "",
            "success": "false",
            "next_data_found": "false",
            "matches_found": "false",
            "match_count": "0",
            "sample_home_team": "",
            "sample_away_team": "",
            "sample_home_score": "",
            "sample_away_score": "",
            "notes": f"Error: {type(e).__name__}: {e}",
        })

write_csv(
    "stage_8c_segunda_2021_22_playoff_final_discovery.csv",
    stage_8c_discovery_fields,
    stage_8c_discovery_rows,
)

print("Stage 8C Segunda playoff final discovery complete.")
# -----------------------------
# Stage 8D: Extract Segunda División 2021/22 promotion playoff fixtures
# -----------------------------

stage_8d_fixture_rows = []
stage_8d_team_index_rows = []
stage_8d_errors = []

playoff_round_labels = {
    43: "Promotion playoff semi-final first leg",
    44: "Promotion playoff semi-final second leg",
    45: "Promotion playoff final first leg",
    46: "Promotion playoff final second leg",
}

season_id = "2021-22"
competition_id = "SEGUNDA_DIVISION"
competition_name = "Segunda División"
competition_level = "2"

for matchday in range(43, 47):
    source_url = f"https://www.laliga.com/laliga-hypermotion/resultados/{season_id}/jornada-{matchday}"

    try:
        request = urllib.request.Request(
            source_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not next_data_match:
            stage_8d_errors.append({
                "competition_id": competition_id,
                "matchday": str(matchday),
                "source_url": source_url,
                "error_type": "failed_no_next_data",
                "error_message": "No __NEXT_DATA__ JSON found.",
            })
            continue

        next_data = json.loads(next_data_match.group(1))
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

            home_team_id = make_team_id(home_name)
            away_team_id = make_team_id(away_name)

            fixture_id = make_fixture_id(
                season_id,
                competition_id,
                str(matchday),
                home_team_id,
                away_team_id,
            )

            stage_8d_fixture_rows.append({
                "fixture_id": fixture_id,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "competition_level": competition_level,
                "competition_group": "",
                "fixture_phase": "promotion_playoff",
                "matchday": str(matchday),
                "round_label": playoff_round_labels[matchday],
                "fixture_date": match.get("date", ""),
                "kickoff_time_local": "",
                "home_team_id": home_team_id,
                "home_team_name_source": home_name,
                "away_team_id": away_team_id,
                "away_team_name_source": away_name,
                "home_score": match.get("home_score", ""),
                "away_score": match.get("away_score", ""),
                "result_status": "played",
                "venue_id": "",
                "venue_name_source": "",
                "attendance": "",
                "referee": "",
                "match_report_url": "",
                "rfef_acta_url": "",
                "laliga_match_url": "",
                "source_system": "LaLiga",
                "source_url": source_url,
                "source_retrieved_at": NOW,
                "data_confidence": "high",
                "notes": "Generated by Stage 8D Segunda División promotion playoff extractor.",
            })

    except Exception as e:
        stage_8d_errors.append({
            "competition_id": competition_id,
            "matchday": str(matchday),
            "source_url": source_url,
            "error_type": type(e).__name__,
            "error_message": str(e),
        })

write_csv(
    "segunda_2021_22_playoff_fixtures_results_stage_8d.csv",
    stage_8a_fixture_fields,
    stage_8d_fixture_rows,
)

# -----------------------------
# Build playoff team fixture index
# -----------------------------

combined_region_lookup_8d = {}

for region_map_filename in [
    "team_region_map_stage_4g2_exact_laliga_ids.csv",
    "team_region_map_stage_7d_segunda_exact_laliga_ids.csv",
]:
    region_map_file = EXPORT_DIR / region_map_filename

    if region_map_file.exists():
        with region_map_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                combined_region_lookup_8d[row["team_id"]] = row

for fixture in stage_8d_fixture_rows:
    fixture_id = fixture["fixture_id"]

    home_team_id = fixture["home_team_id"]
    away_team_id = fixture["away_team_id"]

    home_score = fixture["home_score"]
    away_score = fixture["away_score"]

    home_region = combined_region_lookup_8d.get(home_team_id, {})
    away_region = combined_region_lookup_8d.get(away_team_id, {})

    # Home team row
    stage_8d_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{home_team_id}",
        "fixture_id": fixture_id,
        "team_id": home_team_id,
        "season_id": fixture["season_id"],
        "competition_id": fixture["competition_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "fixture_phase": fixture["fixture_phase"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": away_team_id,
        "home_or_away": "Home",
        "team_score": home_score,
        "opponent_score": away_score,
        "result_for_team": result_for_team(home_score, away_score),
        "venue_id": fixture["venue_id"],
        "is_home_ground": "true",
        "team_autonomous_region_id": home_region.get("autonomous_region_id", ""),
        "team_autonomous_region_name": home_region.get("autonomous_region_name", ""),
        "team_autonomous_region_slug": home_region.get("autonomous_region_slug", ""),
        "opponent_autonomous_region_id": away_region.get("autonomous_region_id", ""),
        "opponent_autonomous_region_name": away_region.get("autonomous_region_name", ""),
        "opponent_autonomous_region_slug": away_region.get("autonomous_region_slug", ""),
        "source_url": fixture["source_url"],
    })

    # Away team row
    stage_8d_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{away_team_id}",
        "fixture_id": fixture_id,
        "team_id": away_team_id,
        "season_id": fixture["season_id"],
        "competition_id": fixture["competition_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "fixture_phase": fixture["fixture_phase"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": home_team_id,
        "home_or_away": "Away",
        "team_score": away_score,
        "opponent_score": home_score,
        "result_for_team": result_for_team(away_score, home_score),
        "venue_id": fixture["venue_id"],
        "is_home_ground": "false",
        "team_autonomous_region_id": away_region.get("autonomous_region_id", ""),
        "team_autonomous_region_name": away_region.get("autonomous_region_name", ""),
        "team_autonomous_region_slug": away_region.get("autonomous_region_slug", ""),
        "opponent_autonomous_region_id": home_region.get("autonomous_region_id", ""),
        "opponent_autonomous_region_name": home_region.get("autonomous_region_name", ""),
        "opponent_autonomous_region_slug": home_region.get("autonomous_region_slug", ""),
        "source_url": fixture["source_url"],
    })

write_csv(
    "segunda_2021_22_playoff_team_fixture_index_stage_8d.csv",
    stage_8a_team_index_fields,
    stage_8d_team_index_rows,
)

# -----------------------------
# Stage 8D validation summary
# -----------------------------

stage_8d_validation_fields = [
    "check_name",
    "result",
    "details",
]

missing_team_regions = [
    row for row in stage_8d_team_index_rows
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_8d_team_index_rows
    if not row.get("opponent_autonomous_region_id")
]

stage_8d_validation_rows = [
    {
        "check_name": "playoff_fixture_rows",
        "result": str(len(stage_8d_fixture_rows)),
        "details": "Expected 6.",
    },
    {
        "check_name": "playoff_team_fixture_index_rows",
        "result": str(len(stage_8d_team_index_rows)),
        "details": "Expected 12.",
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "|".join(sorted(set(row["team_id"] for row in missing_team_regions))),
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "|".join(sorted(set(row["opponent_team_id"] for row in missing_opponent_regions))),
    },
    {
        "check_name": "extraction_errors",
        "result": str(len(stage_8d_errors)),
        "details": "See segunda_2021_22_playoff_errors_stage_8d.csv if greater than 0.",
    },
]

write_csv(
    "segunda_2021_22_playoff_validation_summary_stage_8d.csv",
    stage_8d_validation_fields,
    stage_8d_validation_rows,
)

error_fields = [
    "competition_id",
    "matchday",
    "source_url",
    "error_type",
    "error_message",
]

write_csv(
    "segunda_2021_22_playoff_errors_stage_8d.csv",
    error_fields,
    stage_8d_errors,
)

print(f"Stage 8D generated {len(stage_8d_fixture_rows)} Segunda playoff fixture rows.")
print(f"Stage 8D generated {len(stage_8d_team_index_rows)} Segunda playoff team fixture index rows.")
# -----------------------------
# Stage 8E: Combine 2021/22 LaLiga regular + Segunda playoff outputs
# -----------------------------

stage_8e_fixture_rows = []
stage_8e_team_index_rows = []

try:
    # Regular season fixtures: Primera + Segunda
    regular_fixtures_file = EXPORT_DIR / "laliga_production_2021_22_regular_fixtures_results.csv"

    with regular_fixtures_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        stage_8e_fixture_rows.extend(list(reader))

    # Segunda playoff fixtures
    playoff_fixtures_file = EXPORT_DIR / "segunda_2021_22_playoff_fixtures_results_stage_8d.csv"

    with playoff_fixtures_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        stage_8e_fixture_rows.extend(list(reader))

except Exception as e:
    print(f"Stage 8E fixture combine failed: {type(e).__name__}: {e}")


try:
    # Regular season team fixture index: Primera + Segunda
    regular_team_index_file = EXPORT_DIR / "laliga_production_2021_22_regular_team_fixture_index.csv"

    with regular_team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        stage_8e_team_index_rows.extend(list(reader))

    # Segunda playoff team fixture index
    playoff_team_index_file = EXPORT_DIR / "segunda_2021_22_playoff_team_fixture_index_stage_8d.csv"

    with playoff_team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        stage_8e_team_index_rows.extend(list(reader))

except Exception as e:
    print(f"Stage 8E team index combine failed: {type(e).__name__}: {e}")


write_csv(
    "laliga_2021_22_fixtures_results_complete.csv",
    stage_8a_fixture_fields,
    stage_8e_fixture_rows,
)

write_csv(
    "laliga_2021_22_team_fixture_index_complete.csv",
    stage_8a_team_index_fields,
    stage_8e_team_index_rows,
)


# -----------------------------
# Stage 8E validation summary
# -----------------------------

stage_8e_validation_fields = [
    "check_name",
    "result",
    "details",
]

fixture_ids = [
    row["fixture_id"]
    for row in stage_8e_fixture_rows
    if row.get("fixture_id")
]

duplicate_fixture_ids = sorted([
    fixture_id
    for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

team_fixture_ids = [
    row["team_fixture_id"]
    for row in stage_8e_team_index_rows
    if row.get("team_fixture_id")
]

duplicate_team_fixture_ids = sorted([
    team_fixture_id
    for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

missing_team_regions = [
    row for row in stage_8e_team_index_rows
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_8e_team_index_rows
    if not row.get("opponent_autonomous_region_id")
]

primera_regular_count = len([
    row for row in stage_8e_fixture_rows
    if row.get("competition_id") == "PRIMERA_DIVISION"
    and row.get("fixture_phase") == "regular_season"
])

segunda_regular_count = len([
    row for row in stage_8e_fixture_rows
    if row.get("competition_id") == "SEGUNDA_DIVISION"
    and row.get("fixture_phase") == "regular_season"
])

segunda_playoff_count = len([
    row for row in stage_8e_fixture_rows
    if row.get("competition_id") == "SEGUNDA_DIVISION"
    and row.get("fixture_phase") == "promotion_playoff"
])

stage_8e_validation_rows = [
    {
        "check_name": "primera_regular_fixture_rows",
        "result": str(primera_regular_count),
        "details": "Expected 380.",
    },
    {
        "check_name": "segunda_regular_fixture_rows",
        "result": str(segunda_regular_count),
        "details": "Expected 462.",
    },
    {
        "check_name": "segunda_playoff_fixture_rows",
        "result": str(segunda_playoff_count),
        "details": "Expected 6.",
    },
    {
        "check_name": "total_fixture_rows",
        "result": str(len(stage_8e_fixture_rows)),
        "details": "Expected 848.",
    },
    {
        "check_name": "total_team_fixture_index_rows",
        "result": str(len(stage_8e_team_index_rows)),
        "details": "Expected 1696.",
    },
    {
        "check_name": "duplicate_fixture_ids",
        "result": str(len(duplicate_fixture_ids)),
        "details": "|".join(duplicate_fixture_ids),
    },
    {
        "check_name": "duplicate_team_fixture_ids",
        "result": str(len(duplicate_team_fixture_ids)),
        "details": "|".join(duplicate_team_fixture_ids),
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "|".join(sorted(set(row["team_id"] for row in missing_team_regions if row.get("team_id")))),
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "|".join(sorted(set(row["opponent_team_id"] for row in missing_opponent_regions if row.get("opponent_team_id")))),
    },
]

write_csv(
    "laliga_2021_22_complete_validation_summary.csv",
    stage_8e_validation_fields,
    stage_8e_validation_rows,
)

print(f"Stage 8E combined {len(stage_8e_fixture_rows)} fixture rows.")
print(f"Stage 8E combined {len(stage_8e_team_index_rows)} team fixture index rows.")
# -----------------------------
# Stage 9A: Discover Segunda playoff jornada numbers for all target seasons
# -----------------------------

stage_9a_fields = [
    "season_id",
    "candidate_jornada",
    "candidate_url",
    "http_status",
    "success",
    "next_data_found",
    "matches_found",
    "match_count",
    "sample_home_team",
    "sample_away_team",
    "sample_home_score",
    "sample_away_score",
    "likely_playoff_round",
    "notes",
]

stage_9a_rows = []

target_seasons = [
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]

for season_id in target_seasons:
    for jornada in range(43, 49):
        candidate_url = f"https://www.laliga.com/laliga-hypermotion/resultados/{season_id}/jornada-{jornada}"

        try:
            request = urllib.request.Request(
                candidate_url,
                headers={
                    "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
                }
            )

            with urllib.request.urlopen(request, timeout=30) as response:
                status_code = response.getcode()
                html = response.read().decode("utf-8", errors="ignore")

            next_data_match = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
                html,
                re.DOTALL
            )

            next_data_found = bool(next_data_match)
            matches_found = False
            match_count = 0
            sample_home_team = ""
            sample_away_team = ""
            sample_home_score = ""
            sample_away_score = ""
            likely_playoff_round = ""
            notes = ""

            if next_data_match:
                try:
                    next_data = json.loads(next_data_match.group(1))
                    matches = next_data.get("props", {}).get("pageProps", {}).get("matches", [])

                    if isinstance(matches, list) and matches:
                        matches_found = True
                        match_count = len(matches)

                        sample_match = matches[0]
                        sample_home = sample_match.get("home_team", {})
                        sample_away = sample_match.get("away_team", {})

                        sample_home_team = (
                            sample_home.get("name")
                            or sample_home.get("nickname")
                            or sample_home.get("short_name")
                            or ""
                        )

                        sample_away_team = (
                            sample_away.get("name")
                            or sample_away.get("nickname")
                            or sample_away.get("short_name")
                            or ""
                        )

                        sample_home_score = str(sample_match.get("home_score", ""))
                        sample_away_score = str(sample_match.get("away_score", ""))

                        if jornada == 43:
                            likely_playoff_round = "Promotion playoff semi-final first leg"
                        elif jornada == 44:
                            likely_playoff_round = "Promotion playoff semi-final second leg"
                        elif jornada == 45:
                            likely_playoff_round = "Promotion playoff final first leg"
                        elif jornada == 46:
                            likely_playoff_round = "Promotion playoff final second leg"
                        else:
                            likely_playoff_round = "Unexpected extra playoff jornada"

                    else:
                        notes = "NEXT_DATA found, but props.pageProps.matches was empty or missing."

                except Exception as e:
                    notes = f"NEXT_DATA found, but JSON parse or match inspection failed: {type(e).__name__}: {e}"

            else:
                notes = "No __NEXT_DATA__ JSON found."

            stage_9a_rows.append({
                "season_id": season_id,
                "candidate_jornada": str(jornada),
                "candidate_url": candidate_url,
                "http_status": str(status_code),
                "success": str(status_code == 200).lower(),
                "next_data_found": str(next_data_found).lower(),
                "matches_found": str(matches_found).lower(),
                "match_count": str(match_count),
                "sample_home_team": sample_home_team,
                "sample_away_team": sample_away_team,
                "sample_home_score": sample_home_score,
                "sample_away_score": sample_away_score,
                "likely_playoff_round": likely_playoff_round,
                "notes": notes,
            })

        except urllib.error.HTTPError as e:
            stage_9a_rows.append({
                "season_id": season_id,
                "candidate_jornada": str(jornada),
                "candidate_url": candidate_url,
                "http_status": str(e.code),
                "success": "false",
                "next_data_found": "false",
                "matches_found": "false",
                "match_count": "0",
                "sample_home_team": "",
                "sample_away_team": "",
                "sample_home_score": "",
                "sample_away_score": "",
                "likely_playoff_round": "",
                "notes": f"HTTPError: {e.reason}",
            })

        except Exception as e:
            stage_9a_rows.append({
                "season_id": season_id,
                "candidate_jornada": str(jornada),
                "candidate_url": candidate_url,
                "http_status": "",
                "success": "false",
                "next_data_found": "false",
                "matches_found": "false",
                "match_count": "0",
                "sample_home_team": "",
                "sample_away_team": "",
                "sample_home_score": "",
                "sample_away_score": "",
                "likely_playoff_round": "",
                "notes": f"Error: {type(e).__name__}: {e}",
            })

write_csv(
    "stage_9a_segunda_playoff_jornada_discovery_all_seasons.csv",
    stage_9a_fields,
    stage_9a_rows,
)

# -----------------------------
# Stage 9A validation summary
# -----------------------------

stage_9a_validation_fields = [
    "season_id",
    "playoff_jornadas_found",
    "total_playoff_matches_found",
    "jornada_match_counts",
    "notes",
]

stage_9a_validation_rows = []

for season_id in target_seasons:
    season_rows = [
        row for row in stage_9a_rows
        if row["season_id"] == season_id
        and row["matches_found"] == "true"
    ]

    jornada_match_counts = "|".join([
        f"J{row['candidate_jornada']}={row['match_count']}"
        for row in season_rows
    ])

    total_matches = sum(
        int(row["match_count"])
        for row in season_rows
        if row["match_count"].isdigit()
    )

    stage_9a_validation_rows.append({
        "season_id": season_id,
        "playoff_jornadas_found": str(len(season_rows)),
        "total_playoff_matches_found": str(total_matches),
        "jornada_match_counts": jornada_match_counts,
        "notes": "Expected usually 4 playoff jornadas and 6 playoff matches.",
    })

write_csv(
    "stage_9a_segunda_playoff_jornada_discovery_validation.csv",
    stage_9a_validation_fields,
    stage_9a_validation_rows,
)

print("Stage 9A Segunda playoff jornada discovery complete.")
# -----------------------------
# Stage 9B: Multi-season LaLiga production runner
# Primera División regular season + Segunda División regular season + Segunda playoffs
# Seasons: 2021/22 to 2025/26
# -----------------------------

stage_9b_fixture_rows = []
stage_9b_team_index_rows = []
stage_9b_errors = []

stage_9b_seasons = [
    "2021-22",
    "2022-23",
    "2023-24",
    "2024-25",
    "2025-26",
]

stage_9b_competition_plan = [
    {
        "competition_id": "PRIMERA_DIVISION",
        "competition_name": "Primera División",
        "competition_level": "1",
        "url_competition_slug": "laliga-easports",
        "regular_matchdays": range(1, 39),
        "playoff_matchdays": [],
    },
    {
        "competition_id": "SEGUNDA_DIVISION",
        "competition_name": "Segunda División",
        "competition_level": "2",
        "url_competition_slug": "laliga-hypermotion",
        "regular_matchdays": range(1, 43),
        "playoff_matchdays": range(43, 47),
    },
]

stage_9b_playoff_round_labels = {
    43: "Promotion playoff semi-final first leg",
    44: "Promotion playoff semi-final second leg",
    45: "Promotion playoff final first leg",
    46: "Promotion playoff final second leg",
}


def stage_9b_extract_matchday(
    season_id,
    competition_id,
    competition_name,
    competition_level,
    url_competition_slug,
    matchday,
    fixture_phase,
):
    source_url = f"https://www.laliga.com/{url_competition_slug}/resultados/{season_id}/jornada-{matchday}"
    rows = []

    try:
        request = urllib.request.Request(
            source_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        next_data_match = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            html,
            re.DOTALL
        )

        if not next_data_match:
            stage_9b_errors.append({
                "season_id": season_id,
                "competition_id": competition_id,
                "matchday": str(matchday),
                "fixture_phase": fixture_phase,
                "source_url": source_url,
                "error_type": "failed_no_next_data",
                "error_message": "No __NEXT_DATA__ JSON found.",
            })
            return rows

        next_data = json.loads(next_data_match.group(1))
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

            home_team_id = make_team_id(home_name)
            away_team_id = make_team_id(away_name)

            fixture_id = make_fixture_id(
                season_id,
                competition_id,
                str(matchday),
                home_team_id,
                away_team_id,
            )

            if fixture_phase == "promotion_playoff":
                round_label = stage_9b_playoff_round_labels.get(
                    matchday,
                    f"Promotion playoff jornada {matchday}",
                )
            else:
                round_label = f"Jornada {matchday}"

            rows.append({
                "fixture_id": fixture_id,
                "season_id": season_id,
                "competition_id": competition_id,
                "competition_name": competition_name,
                "competition_level": competition_level,
                "competition_group": "",
                "fixture_phase": fixture_phase,
                "matchday": str(matchday),
                "round_label": round_label,
                "fixture_date": match.get("date", ""),
                "kickoff_time_local": "",
                "home_team_id": home_team_id,
                "home_team_name_source": home_name,
                "away_team_id": away_team_id,
                "away_team_name_source": away_name,
                "home_score": match.get("home_score", ""),
                "away_score": match.get("away_score", ""),
                "result_status": "played",
                "venue_id": "",
                "venue_name_source": "",
                "attendance": "",
                "referee": "",
                "match_report_url": "",
                "rfef_acta_url": "",
                "laliga_match_url": "",
                "source_system": "LaLiga",
                "source_url": source_url,
                "source_retrieved_at": NOW,
                "data_confidence": "high",
                "notes": "Generated by Stage 9B multi-season LaLiga production runner.",
            })

    except Exception as e:
        stage_9b_errors.append({
            "season_id": season_id,
            "competition_id": competition_id,
            "matchday": str(matchday),
            "fixture_phase": fixture_phase,
            "source_url": source_url,
            "error_type": type(e).__name__,
            "error_message": str(e),
        })

    return rows


# Extract all planned LaLiga fixtures
for season_id in stage_9b_seasons:
    for competition in stage_9b_competition_plan:

        for matchday in competition["regular_matchdays"]:
            stage_9b_fixture_rows.extend(
                stage_9b_extract_matchday(
                    season_id=season_id,
                    competition_id=competition["competition_id"],
                    competition_name=competition["competition_name"],
                    competition_level=competition["competition_level"],
                    url_competition_slug=competition["url_competition_slug"],
                    matchday=matchday,
                    fixture_phase="regular_season",
                )
            )

        for matchday in competition["playoff_matchdays"]:
            stage_9b_fixture_rows.extend(
                stage_9b_extract_matchday(
                    season_id=season_id,
                    competition_id=competition["competition_id"],
                    competition_name=competition["competition_name"],
                    competition_level=competition["competition_level"],
                    url_competition_slug=competition["url_competition_slug"],
                    matchday=matchday,
                    fixture_phase="promotion_playoff",
                )
            )


write_csv(
    "laliga_multiseason_2021_22_to_2025_26_fixtures_results.csv",
    stage_8a_fixture_fields,
    stage_9b_fixture_rows,
)


# -----------------------------
# Stage 9B: build combined region lookup
# -----------------------------

stage_9b_region_lookup = {}

for region_map_filename in [
    "team_region_map_stage_4g2_exact_laliga_ids.csv",
    "team_region_map_stage_7d_segunda_exact_laliga_ids.csv",
]:
    region_map_file = EXPORT_DIR / region_map_filename

    if region_map_file.exists():
        with region_map_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stage_9b_region_lookup[row["team_id"]] = row


# -----------------------------
# Stage 9B: build team fixture index
# -----------------------------

for fixture in stage_9b_fixture_rows:
    fixture_id = fixture["fixture_id"]

    home_team_id = fixture["home_team_id"]
    away_team_id = fixture["away_team_id"]

    home_score = fixture["home_score"]
    away_score = fixture["away_score"]

    home_region = stage_9b_region_lookup.get(home_team_id, {})
    away_region = stage_9b_region_lookup.get(away_team_id, {})

    stage_9b_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{home_team_id}",
        "fixture_id": fixture_id,
        "team_id": home_team_id,
        "season_id": fixture["season_id"],
        "competition_id": fixture["competition_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "fixture_phase": fixture["fixture_phase"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": away_team_id,
        "home_or_away": "Home",
        "team_score": home_score,
        "opponent_score": away_score,
        "result_for_team": result_for_team(home_score, away_score),
        "venue_id": fixture["venue_id"],
        "is_home_ground": "true",
        "team_autonomous_region_id": home_region.get("autonomous_region_id", ""),
        "team_autonomous_region_name": home_region.get("autonomous_region_name", ""),
        "team_autonomous_region_slug": home_region.get("autonomous_region_slug", ""),
        "opponent_autonomous_region_id": away_region.get("autonomous_region_id", ""),
        "opponent_autonomous_region_name": away_region.get("autonomous_region_name", ""),
        "opponent_autonomous_region_slug": away_region.get("autonomous_region_slug", ""),
        "source_url": fixture["source_url"],
    })

    stage_9b_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{away_team_id}",
        "fixture_id": fixture_id,
        "team_id": away_team_id,
        "season_id": fixture["season_id"],
        "competition_id": fixture["competition_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "fixture_phase": fixture["fixture_phase"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": home_team_id,
        "home_or_away": "Away",
        "team_score": away_score,
        "opponent_score": home_score,
        "result_for_team": result_for_team(away_score, home_score),
        "venue_id": fixture["venue_id"],
        "is_home_ground": "false",
        "team_autonomous_region_id": away_region.get("autonomous_region_id", ""),
        "team_autonomous_region_name": away_region.get("autonomous_region_name", ""),
        "team_autonomous_region_slug": away_region.get("autonomous_region_slug", ""),
        "opponent_autonomous_region_id": home_region.get("autonomous_region_id", ""),
        "opponent_autonomous_region_name": home_region.get("autonomous_region_name", ""),
        "opponent_autonomous_region_slug": home_region.get("autonomous_region_slug", ""),
        "source_url": fixture["source_url"],
    })


write_csv(
    "laliga_multiseason_2021_22_to_2025_26_team_fixture_index.csv",
    stage_8a_team_index_fields,
    stage_9b_team_index_rows,
)


# -----------------------------
# Stage 9B: validation summary
# -----------------------------

stage_9b_validation_fields = [
    "check_name",
    "result",
    "details",
]

fixture_ids = [
    row["fixture_id"]
    for row in stage_9b_fixture_rows
    if row.get("fixture_id")
]

duplicate_fixture_ids = sorted([
    fixture_id
    for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

team_fixture_ids = [
    row["team_fixture_id"]
    for row in stage_9b_team_index_rows
    if row.get("team_fixture_id")
]

duplicate_team_fixture_ids = sorted([
    team_fixture_id
    for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

missing_team_regions = [
    row for row in stage_9b_team_index_rows
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_9b_team_index_rows
    if not row.get("opponent_autonomous_region_id")
]

teams_missing_regions = sorted(set(
    row["team_id"]
    for row in missing_team_regions
    if row.get("team_id")
))

opponents_missing_regions = sorted(set(
    row["opponent_team_id"]
    for row in missing_opponent_regions
    if row.get("opponent_team_id")
))

primera_regular_count = len([
    row for row in stage_9b_fixture_rows
    if row.get("competition_id") == "PRIMERA_DIVISION"
    and row.get("fixture_phase") == "regular_season"
])

segunda_regular_count = len([
    row for row in stage_9b_fixture_rows
    if row.get("competition_id") == "SEGUNDA_DIVISION"
    and row.get("fixture_phase") == "regular_season"
])

segunda_playoff_count = len([
    row for row in stage_9b_fixture_rows
    if row.get("competition_id") == "SEGUNDA_DIVISION"
    and row.get("fixture_phase") == "promotion_playoff"
])

stage_9b_validation_rows = [
    {
        "check_name": "primera_regular_fixture_rows",
        "result": str(primera_regular_count),
        "details": "Expected 1900: 5 seasons x 380.",
    },
    {
        "check_name": "segunda_regular_fixture_rows",
        "result": str(segunda_regular_count),
        "details": "Expected 2310: 5 seasons x 462.",
    },
    {
        "check_name": "segunda_playoff_fixture_rows",
        "result": str(segunda_playoff_count),
        "details": "Expected 30: 5 seasons x 6.",
    },
    {
        "check_name": "total_fixture_rows",
        "result": str(len(stage_9b_fixture_rows)),
        "details": "Expected 4240.",
    },
    {
        "check_name": "total_team_fixture_index_rows",
        "result": str(len(stage_9b_team_index_rows)),
        "details": "Expected 8480.",
    },
    {
        "check_name": "duplicate_fixture_ids",
        "result": str(len(duplicate_fixture_ids)),
        "details": "|".join(duplicate_fixture_ids),
    },
    {
        "check_name": "duplicate_team_fixture_ids",
        "result": str(len(duplicate_team_fixture_ids)),
        "details": "|".join(duplicate_team_fixture_ids),
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "|".join(teams_missing_regions),
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "|".join(opponents_missing_regions),
    },
    {
        "check_name": "extraction_errors",
        "result": str(len(stage_9b_errors)),
        "details": "See laliga_multiseason_2021_22_to_2025_26_errors.csv if greater than 0.",
    },
]

write_csv(
    "laliga_multiseason_2021_22_to_2025_26_validation_summary.csv",
    stage_9b_validation_fields,
    stage_9b_validation_rows,
)

stage_9b_error_fields = [
    "season_id",
    "competition_id",
    "matchday",
    "fixture_phase",
    "source_url",
    "error_type",
    "error_message",
]

write_csv(
    "laliga_multiseason_2021_22_to_2025_26_errors.csv",
    stage_9b_error_fields,
    stage_9b_errors,
)

# Unmapped teams output for region cleanup
unmapped_team_fields = [
    "team_id",
    "occurrences_as_team",
    "occurrences_as_opponent",
]

unmapped_team_rows = []

for team_id in sorted(set(teams_missing_regions + opponents_missing_regions)):
    unmapped_team_rows.append({
        "team_id": team_id,
        "occurrences_as_team": str(len([
            row for row in missing_team_regions
            if row.get("team_id") == team_id
        ])),
        "occurrences_as_opponent": str(len([
            row for row in missing_opponent_regions
            if row.get("opponent_team_id") == team_id
        ])),
    })

write_csv(
    "laliga_multiseason_2021_22_to_2025_26_unmapped_region_teams.csv",
    unmapped_team_fields,
    unmapped_team_rows,
)

print(f"Stage 9B generated {len(stage_9b_fixture_rows)} fixture rows.")
print(f"Stage 9B generated {len(stage_9b_team_index_rows)} team fixture index rows.")
print(f"Stage 9B found {len(stage_9b_errors)} extraction errors.")
print(f"Stage 9B found {len(unmapped_team_rows)} unmapped region teams.")
# -----------------------------
# Stage 9C: Clean multi-season LaLiga output
# - Add missing region tags
# - Exclude unresolved POR_DETERMINAR fixtures from confirmed app-ready export
# -----------------------------

stage_9c_region_patch_fields = [
    "team_id",
    "autonomous_region_id",
    "autonomous_region_name",
    "autonomous_region_slug",
    "notes",
]

stage_9c_region_patch_rows = [
    {
        "team_id": "AD_CEUTA_FC",
        "autonomous_region_id": "CE",
        "autonomous_region_name": "Ceuta",
        "autonomous_region_slug": "ceuta",
        "notes": "",
    },
    {
        "team_id": "ALBACETE_BALOMPIE_SAD",
        "autonomous_region_id": "CM",
        "autonomous_region_name": "Castilla-La Mancha",
        "autonomous_region_slug": "castilla-la-mancha",
        "notes": "",
    },
    {
        "team_id": "CD_CASTELLON",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
        "notes": "",
    },
    {
        "team_id": "CLUB_DEPORTIVO_ELDENSE",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
        "notes": "",
    },
    {
        "team_id": "CORDOBA_CLUB_DE_FUTBOL",
        "autonomous_region_id": "AN",
        "autonomous_region_name": "Andalusia",
        "autonomous_region_slug": "andalusia",
        "notes": "",
    },
    {
        "team_id": "CULTURAL_Y_DEPORTIVA_LEONESA_SAD",
        "autonomous_region_id": "CL",
        "autonomous_region_name": "Castile and León",
        "autonomous_region_slug": "castile-and-leon",
        "notes": "",
    },
    {
        "team_id": "FC_ANDORRA",
        "autonomous_region_id": "AD",
        "autonomous_region_name": "Andorra",
        "autonomous_region_slug": "andorra",
        "notes": "Non-Spanish club in Spanish league system. Keep separate from Spanish autonomous communities.",
    },
    {
        "team_id": "RACING_CLUB_DE_FERROL",
        "autonomous_region_id": "GA",
        "autonomous_region_name": "Galicia",
        "autonomous_region_slug": "galicia",
        "notes": "",
    },
    {
        "team_id": "REAL_CLUB_DEPORTIVO_DE_LA_CORUNA_SAD",
        "autonomous_region_id": "GA",
        "autonomous_region_name": "Galicia",
        "autonomous_region_slug": "galicia",
        "notes": "",
    },
    {
        "team_id": "REAL_RACING_CLUB_SAD",
        "autonomous_region_id": "CB",
        "autonomous_region_name": "Cantabria",
        "autonomous_region_slug": "cantabria",
        "notes": "",
    },
    {
        "team_id": "VILLARREAL_CLUB_DE_FUTBOL_B",
        "autonomous_region_id": "VC",
        "autonomous_region_name": "Valencian Community",
        "autonomous_region_slug": "valencian-community",
        "notes": "",
    },
]

write_csv(
    "stage_9c_region_patch_new_teams.csv",
    stage_9c_region_patch_fields,
    stage_9c_region_patch_rows,
)

stage_9c_region_lookup = {}

# Existing region maps from earlier stages
for region_map_filename in [
    "team_region_map_stage_4g2_exact_laliga_ids.csv",
    "team_region_map_stage_7d_segunda_exact_laliga_ids.csv",
]:
    region_map_file = EXPORT_DIR / region_map_filename

    if region_map_file.exists():
        with region_map_file.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stage_9c_region_lookup[row["team_id"]] = row

# Add the new patch rows
for row in stage_9c_region_patch_rows:
    stage_9c_region_lookup[row["team_id"]] = row


# -----------------------------
# Read Stage 9B outputs
# -----------------------------

stage_9c_fixture_rows_all = []
stage_9c_team_index_rows_all = []

try:
    fixture_file = EXPORT_DIR / "laliga_multiseason_2021_22_to_2025_26_fixtures_results.csv"

    with fixture_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        stage_9c_fixture_rows_all = list(reader)

except Exception as e:
    print(f"Stage 9C fixture read failed: {type(e).__name__}: {e}")

try:
    team_index_file = EXPORT_DIR / "laliga_multiseason_2021_22_to_2025_26_team_fixture_index.csv"

    with team_index_file.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        stage_9c_team_index_rows_all = list(reader)

except Exception as e:
    print(f"Stage 9C team index read failed: {type(e).__name__}: {e}")


# -----------------------------
# Exclude unresolved POR_DETERMINAR fixtures from app-ready confirmed export
# -----------------------------

stage_9c_excluded_fixture_rows = [
    row for row in stage_9c_fixture_rows_all
    if row.get("home_team_id") == "POR_DETERMINAR"
    or row.get("away_team_id") == "POR_DETERMINAR"
]

excluded_fixture_ids = set(
    row["fixture_id"]
    for row in stage_9c_excluded_fixture_rows
    if row.get("fixture_id")
)

stage_9c_confirmed_fixture_rows = [
    row for row in stage_9c_fixture_rows_all
    if row.get("fixture_id") not in excluded_fixture_ids
]

stage_9c_confirmed_team_index_rows = [
    row for row in stage_9c_team_index_rows_all
    if row.get("fixture_id") not in excluded_fixture_ids
]


write_csv(
    "laliga_multiseason_2021_22_to_2025_26_excluded_unconfirmed_fixtures.csv",
    stage_8a_fixture_fields,
    stage_9c_excluded_fixture_rows,
)


# -----------------------------
# Re-apply region tags to confirmed team index rows
# -----------------------------
# -----------------------------
# Stage 10B: Extract candidate RFEF links from promising pages
# -----------------------------

from urllib.parse import urljoin

stage_10b_fields = [
    "source_page_name",
    "source_page_url",
    "link_text",
    "link_url",
    "keyword_matches",
    "notes",
]

stage_10b_rows = []

rfef_link_source_pages = [
    {
        "source_page_name": "RFEF actas page",
        "source_page_url": "https://rfef.es/es/federacion/actas",
    },
    {
        "source_page_name": "RFEF Primera Federación competition page",
        "source_page_url": "https://rfef.es/es/competiciones/primera-federacion",
    },
]

rfef_link_keywords = [
    "primera",
    "federacion",
    "federación",
    "grupo",
    "grupo 1",
    "grupo 2",
    "calendario",
    "actas",
    "resultados",
    "competicion",
    "competición",
    "matches",
    "partidos",
]

for source_page in rfef_link_source_pages:
    source_page_name = source_page["source_page_name"]
    source_page_url = source_page["source_page_url"]

    try:
        request = urllib.request.Request(
            source_page_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")

        # Extract simple anchor tags.
        link_matches = re.findall(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        for href, raw_text in link_matches:
            link_text = re.sub(r"<[^>]+>", " ", raw_text)
            link_text = re.sub(r"\s+", " ", link_text).strip()

            full_url = urljoin(source_page_url, href)

            searchable_text = f"{link_text} {full_url}".lower()

            matched_keywords = [
                keyword
                for keyword in rfef_link_keywords
                if keyword.lower() in searchable_text
            ]

            if matched_keywords:
                stage_10b_rows.append({
                    "source_page_name": source_page_name,
                    "source_page_url": source_page_url,
                    "link_text": link_text,
                    "link_url": full_url,
                    "keyword_matches": "|".join(matched_keywords),
                    "notes": "Candidate RFEF link for Primera Federación data discovery.",
                })

    except Exception as e:
        stage_10b_rows.append({
            "source_page_name": source_page_name,
            "source_page_url": source_page_url,
            "link_text": "",
            "link_url": "",
            "keyword_matches": "",
            "notes": f"Stage 10B failed for this page: {type(e).__name__}: {e}",
        })

write_csv(
    "stage_10b_rfef_candidate_links.csv",
    stage_10b_fields,
    stage_10b_rows,
)

print(f"Stage 10B extracted {len(stage_10b_rows)} candidate RFEF links.")
stage_9c_confirmed_team_index_rows_with_regions = []

for row in stage_9c_confirmed_team_index_rows:
    team_region = stage_9c_region_lookup.get(row["team_id"], {})
    opponent_region = stage_9c_region_lookup.get(row["opponent_team_id"], {})

    row["team_autonomous_region_id"] = team_region.get("autonomous_region_id", "")
    row["team_autonomous_region_name"] = team_region.get("autonomous_region_name", "")
    row["team_autonomous_region_slug"] = team_region.get("autonomous_region_slug", "")

    row["opponent_autonomous_region_id"] = opponent_region.get("autonomous_region_id", "")
    row["opponent_autonomous_region_name"] = opponent_region.get("autonomous_region_name", "")
    row["opponent_autonomous_region_slug"] = opponent_region.get("autonomous_region_slug", "")

    stage_9c_confirmed_team_index_rows_with_regions.append(row)


write_csv(
    "laliga_multiseason_2021_22_to_2025_26_confirmed_fixtures_results_clean.csv",
    stage_8a_fixture_fields,
    stage_9c_confirmed_fixture_rows,
)

write_csv(
    "laliga_multiseason_2021_22_to_2025_26_confirmed_team_fixture_index_clean.csv",
    stage_8a_team_index_fields,
    stage_9c_confirmed_team_index_rows_with_regions,
)


# -----------------------------
# Stage 9C validation summary
# -----------------------------

stage_9c_validation_fields = [
    "check_name",
    "result",
    "details",
]

fixture_ids = [
    row["fixture_id"]
    for row in stage_9c_confirmed_fixture_rows
    if row.get("fixture_id")
]

duplicate_fixture_ids = sorted([
    fixture_id
    for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

team_fixture_ids = [
    row["team_fixture_id"]
    for row in stage_9c_confirmed_team_index_rows_with_regions
    if row.get("team_fixture_id")
]

duplicate_team_fixture_ids = sorted([
    team_fixture_id
    for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

missing_team_regions = [
    row for row in stage_9c_confirmed_team_index_rows_with_regions
    if not row.get("team_autonomous_region_id")
]

missing_opponent_regions = [
    row for row in stage_9c_confirmed_team_index_rows_with_regions
    if not row.get("opponent_autonomous_region_id")
]

teams_missing_regions = sorted(set(
    row["team_id"]
    for row in missing_team_regions
    if row.get("team_id")
))

opponents_missing_regions = sorted(set(
    row["opponent_team_id"]
    for row in missing_opponent_regions
    if row.get("opponent_team_id")
))

primera_regular_count = len([
    row for row in stage_9c_confirmed_fixture_rows
    if row.get("competition_id") == "PRIMERA_DIVISION"
    and row.get("fixture_phase") == "regular_season"
])

segunda_regular_count = len([
    row for row in stage_9c_confirmed_fixture_rows
    if row.get("competition_id") == "SEGUNDA_DIVISION"
    and row.get("fixture_phase") == "regular_season"
])

segunda_playoff_count = len([
    row for row in stage_9c_confirmed_fixture_rows
    if row.get("competition_id") == "SEGUNDA_DIVISION"
    and row.get("fixture_phase") == "promotion_playoff"
])

stage_9c_validation_rows = [
    {
        "check_name": "confirmed_fixture_rows",
        "result": str(len(stage_9c_confirmed_fixture_rows)),
        "details": "Expected 4238 if two unconfirmed 2025/26 playoff placeholder fixtures are excluded.",
    },
    {
        "check_name": "confirmed_team_fixture_index_rows",
        "result": str(len(stage_9c_confirmed_team_index_rows_with_regions)),
        "details": "Expected 8476 if two unconfirmed fixtures are excluded.",
    },
    {
        "check_name": "excluded_unconfirmed_fixture_rows",
        "result": str(len(stage_9c_excluded_fixture_rows)),
        "details": "Rows containing POR_DETERMINAR.",
    },
    {
        "check_name": "primera_regular_fixture_rows",
        "result": str(primera_regular_count),
        "details": "Expected 1900.",
    },
    {
        "check_name": "segunda_regular_fixture_rows",
        "result": str(segunda_regular_count),
        "details": "Expected 2310.",
    },
    {
        "check_name": "segunda_confirmed_playoff_fixture_rows",
        "result": str(segunda_playoff_count),
        "details": "Expected 28 if two future/unconfirmed playoff placeholders are excluded.",
    },
    {
        "check_name": "duplicate_fixture_ids",
        "result": str(len(duplicate_fixture_ids)),
        "details": "|".join(duplicate_fixture_ids),
    },
    {
        "check_name": "duplicate_team_fixture_ids",
        "result": str(len(duplicate_team_fixture_ids)),
        "details": "|".join(duplicate_team_fixture_ids),
    },
    {
        "check_name": "missing_team_region_tags",
        "result": str(len(missing_team_regions)),
        "details": "|".join(teams_missing_regions),
    },
    {
        "check_name": "missing_opponent_region_tags",
        "result": str(len(missing_opponent_regions)),
        "details": "|".join(opponents_missing_regions),
    },
]

write_csv(
    "stage_9c_laliga_multiseason_clean_validation_summary.csv",
    stage_9c_validation_fields,
    stage_9c_validation_rows,
)

print(f"Stage 9C confirmed fixture rows: {len(stage_9c_confirmed_fixture_rows)}")
print(f"Stage 9C confirmed team index rows: {len(stage_9c_confirmed_team_index_rows_with_regions)}")
print(f"Stage 9C excluded unconfirmed fixture rows: {len(stage_9c_excluded_fixture_rows)}")
# -----------------------------
# Stage 9D: Create final audit note for clean LaLiga multi-season export
# -----------------------------

audit_note = f"""# LaLiga Multi-Season Fixture Export Audit Note

Generated at: {NOW}

## Scope

This export covers official LaLiga source extraction for:

- Primera División regular season fixtures
- Segunda División regular season fixtures
- Segunda División promotion playoff fixtures where confirmed

Seasons covered:

- 2021/22
- 2022/23
- 2023/24
- 2024/25
- 2025/26

## Final clean app-ready outputs

The app-ready files are:

- `laliga_multiseason_2021_22_to_2025_26_confirmed_fixtures_results_clean.csv`
- `laliga_multiseason_2021_22_to_2025_26_confirmed_team_fixture_index_clean.csv`

These files exclude unconfirmed placeholder fixtures.

## Confirmed clean dataset totals

- Primera División regular fixtures: 1,900
- Segunda División regular fixtures: 2,310
- Confirmed Segunda División playoff fixtures: 24
- Total confirmed fixture rows: 4,234
- Total confirmed team fixture index rows: 8,468

## Excluded unconfirmed fixtures

The following file records excluded placeholder rows:

- `laliga_multiseason_2021_22_to_2025_26_excluded_unconfirmed_fixtures.csv`

Six rows were excluded because they are unresolved 2025/26 Segunda División promotion playoff placeholders.

Those rows use:

- `home_team_id = POR_DETERMINAR`
- `away_team_id = POR_DETERMINAR`

They relate to:

- 2025/26 Jornada 43: playoff semi-final first legs
- 2025/26 Jornada 44: playoff semi-final second legs
- 2025/26 Jornada 45: playoff final first leg
- 2025/26 Jornada 46: playoff final second leg

## Validation status

The clean export passed the key validation checks:

- Duplicate fixture IDs: 0
- Duplicate team fixture IDs: 0
- Missing team region tags: 0
- Missing opponent region tags: 0

## Regional challenge tagging

The clean team fixture index includes autonomous-region tags for both the selected team and the opponent team.

Regional challenge logic should use the stable ID fields rather than display names:

- `team_autonomous_region_id`
- `opponent_autonomous_region_id`

For example:

- Catalonia / Catalunya / Cataluña should map to `CT`
- Andalusia / Andalucía / Andalucia should map to `AN`
- Madrid / Community of Madrid / Comunidad de Madrid should map to `MD`

## Future action required

The 2025/26 Segunda División promotion playoff fixtures should be re-run once LaLiga has confirmed the teams and results.

At that point, the six excluded `POR_DETERMINAR` placeholder rows should be replaced with confirmed fixture rows.

## Current status

This dataset is suitable for app testing and import for all confirmed LaLiga fixtures in scope.

It is not yet the full Spanish football database because Primera Federación Group 1 and Group 2 still need to be handled through the RFEF source route.
"""

audit_note_path = EXPORT_DIR / "laliga_multiseason_2021_22_to_2025_26_audit_note.md"
audit_note_path.write_text(audit_note, encoding="utf-8")

print("Stage 9D audit note created.")
# -----------------------------
# Stage 10A: RFEF Primera Federación source discovery
# -----------------------------

stage_10a_fields = [
    "candidate_name",
    "candidate_url",
    "http_status",
    "success",
    "html_length",
    "contains_primera_federacion",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_calendario",
    "contains_actas",
    "contains_resultados",
    "sample_text",
    "notes",
]

stage_10a_rows = []

rfef_candidate_urls = [
    {
        "candidate_name": "RFEF Primera Federación competition page",
        "candidate_url": "https://rfef.es/es/competiciones/primera-federacion",
    },
    {
        "candidate_name": "RFEF general resultados page",
        "candidate_url": "https://rfef.es/es/resultados",
    },
    {
        "candidate_name": "RFEF actas page",
        "candidate_url": "https://rfef.es/es/actas",
    },
    {
        "candidate_name": "RFEF federation actas page",
        "candidate_url": "https://rfef.es/es/federacion/actas",
    },
    {
        "candidate_name": "RFEF calendar transparency page",
        "candidate_url": "https://rfef.es/es/federacion/transparencia/calendario-temporada-vigente",
    },
]

for candidate in rfef_candidate_urls:
    candidate_name = candidate["candidate_name"]
    candidate_url = candidate["candidate_url"]

    try:
        request = urllib.request.Request(
            candidate_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            status_code = response.getcode()
            html = response.read().decode("utf-8", errors="ignore")

        html_lower = html.lower()

        # Save raw HTML samples for inspection.
        safe_name = re.sub(r"[^A-Za-z0-9]+", "_", candidate_name).strip("_").lower()
        sample_path = EXPORT_DIR / f"stage_10a_{safe_name}.html"
        sample_path.write_text(html[:20000], encoding="utf-8")

        sample_text = re.sub(r"\s+", " ", html[:1000]).strip()

        stage_10a_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": str(status_code),
            "success": str(status_code == 200).lower(),
            "html_length": str(len(html)),
            "contains_primera_federacion": str("primera federación" in html_lower or "primera federacion" in html_lower).lower(),
            "contains_grupo_1": str("grupo 1" in html_lower).lower(),
            "contains_grupo_2": str("grupo 2" in html_lower).lower(),
            "contains_calendario": str("calendario" in html_lower).lower(),
            "contains_actas": str("actas" in html_lower).lower(),
            "contains_resultados": str("resultados" in html_lower).lower(),
            "sample_text": sample_text,
            "notes": "Raw HTML sample saved for inspection.",
        })

    except urllib.error.HTTPError as e:
        stage_10a_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": str(e.code),
            "success": "false",
            "html_length": "0",
            "contains_primera_federacion": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_calendario": "false",
            "contains_actas": "false",
            "contains_resultados": "false",
            "sample_text": "",
            "notes": f"HTTPError: {e.reason}",
        })

    except Exception as e:
        stage_10a_rows.append({
            "candidate_name": candidate_name,
            "candidate_url": candidate_url,
            "http_status": "",
            "success": "false",
            "html_length": "0",
            "contains_primera_federacion": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_calendario": "false",
            "contains_actas": "false",
            "contains_resultados": "false",
            "sample_text": "",
            "notes": f"Error: {type(e).__name__}: {e}",
        })

write_csv(
    "stage_10a_rfef_primera_federacion_source_discovery.csv",
    stage_10a_fields,
    stage_10a_rows,
)

print("Stage 10A RFEF Primera Federación source discovery complete.")
# -----------------------------
# Stage 10C: Test direct RFEF parameterised calendar/jornada links
# -----------------------------

stage_10c_fields = [
    "test_name",
    "test_url",
    "http_status",
    "success",
    "html_length",
    "contains_primera_federacion",
    "contains_grupo",
    "contains_jornada",
    "contains_fecha",
    "contains_resultado",
    "contains_local",
    "contains_visitante",
    "contains_acta",
    "contains_calendario",
    "sample_text",
    "notes",
]

stage_10c_rows = []

rfef_direct_link_tests = [
    {
        "test_name": "RFEF Primera Federación calendar example",
        "test_url": "https://resultados.rfef.es/pnfg/NPcd/NFG_VisCalendario_Vis?cod_primaria=1000120&codtemporada=20&codcompeticion=901769680&codgrupo=901769681",
    },
    {
        "test_name": "RFEF Primera Federación jornada example blank jornada",
        "test_url": "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada?cod_primaria=1000120&CodCompeticion=901769680&CodGrupo=901769681&CodTemporada=20&CodJornada=",
    },
    {
        "test_name": "RFEF Primera Federación jornada 1 example",
        "test_url": "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada?cod_primaria=1000120&CodCompeticion=901769680&CodGrupo=901769681&CodTemporada=20&CodJornada=1",
    },
]

for test in rfef_direct_link_tests:
    test_name = test["test_name"]
    test_url = test["test_url"]

    try:
        request = urllib.request.Request(
            test_url,
            headers={
                "User-Agent": "Mozilla/5.0 Spain82QuestDataBot/0.1"
            }
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            status_code = response.getcode()
            html = response.read().decode("utf-8", errors="ignore")

        html_lower = html.lower()

        safe_name = re.sub(r"[^A-Za-z0-9]+", "_", test_name).strip("_").lower()
        sample_path = EXPORT_DIR / f"stage_10c_{safe_name}.html"
        sample_path.write_text(html[:50000], encoding="utf-8")

        sample_text = re.sub(r"<[^>]+>", " ", html[:2500])
        sample_text = re.sub(r"\s+", " ", sample_text).strip()

        stage_10c_rows.append({
            "test_name": test_name,
            "test_url": test_url,
            "http_status": str(status_code),
            "success": str(status_code == 200).lower(),
            "html_length": str(len(html)),
            "contains_primera_federacion": str("primera federación" in html_lower or "primera federacion" in html_lower).lower(),
            "contains_grupo": str("grupo" in html_lower).lower(),
            "contains_jornada": str("jornada" in html_lower).lower(),
            "contains_fecha": str("fecha" in html_lower).lower(),
            "contains_resultado": str("resultado" in html_lower or "resultados" in html_lower).lower(),
            "contains_local": str("local" in html_lower).lower(),
            "contains_visitante": str("visitante" in html_lower).lower(),
            "contains_acta": str("acta" in html_lower or "actas" in html_lower).lower(),
            "contains_calendario": str("calendario" in html_lower).lower(),
            "sample_text": sample_text,
            "notes": "Raw RFEF HTML sample saved for inspection.",
        })

    except urllib.error.HTTPError as e:
        stage_10c_rows.append({
            "test_name": test_name,
            "test_url": test_url,
            "http_status": str(e.code),
            "success": "false",
            "html_length": "0",
            "contains_primera_federacion": "false",
            "contains_grupo": "false",
            "contains_jornada": "false",
            "contains_fecha": "false",
            "contains_resultado": "false",
            "contains_local": "false",
            "contains_visitante": "false",
            "contains_acta": "false",
            "contains_calendario": "false",
            "sample_text": "",
            "notes": f"HTTPError: {e.reason}",
        })

    except Exception as e:
        stage_10c_rows.append({
            "test_name": test_name,
            "test_url": test_url,
            "http_status": "",
            "success": "false",
            "html_length": "0",
            "contains_primera_federacion": "false",
            "contains_grupo": "false",
            "contains_jornada": "false",
            "contains_fecha": "false",
            "contains_resultado": "false",
            "contains_local": "false",
            "contains_visitante": "false",
            "contains_acta": "false",
            "contains_calendario": "false",
            "sample_text": "",
            "notes": f"Error: {type(e).__name__}: {e}",
        })

write_csv(
    "stage_10c_rfef_direct_link_tests.csv",
    stage_10c_fields,
    stage_10c_rows,
)

print("Stage 10C RFEF direct link tests complete.")

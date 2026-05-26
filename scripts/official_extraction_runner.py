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

print("Stage 2 template generation complete.")

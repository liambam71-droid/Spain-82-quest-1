
from pathlib import Path
import csv

EXPORT_DIR = Path("data/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

fixtures_file = EXPORT_DIR / "fixtures_results.csv"
team_index_file = EXPORT_DIR / "team_fixture_index.csv"
validation_file = Path("validation_report.md")

fixtures = [
    {
        "fixture_id": "2021-22_LALIGA_J01_FC_BARCELONA_REAL_SOCIEDAD",
        "season_id": "2021-22",
        "competition_name": "Primera División",
        "competition_group": "",
        "matchday": "1",
        "fixture_date": "2021-08-15",
        "home_team_id": "FC_BARCELONA",
        "home_team_name_source": "FC Barcelona",
        "away_team_id": "REAL_SOCIEDAD",
        "away_team_name_source": "Real Sociedad",
        "home_score": "4",
        "away_score": "2",
        "venue_id": "CAMP_NOU",
        "source_system": "LaLiga",
        "source_url": "https://www.laliga.com/"
    }
]

fixture_fields = list(fixtures[0].keys())

with fixtures_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fixture_fields)
    writer.writeheader()
    writer.writerows(fixtures)

team_index_rows = []

for fixture in fixtures:
    home_score = int(fixture["home_score"])
    away_score = int(fixture["away_score"])

    if home_score > away_score:
        home_result = "Win"
        away_result = "Loss"
    elif home_score < away_score:
        home_result = "Loss"
        away_result = "Win"
    else:
        home_result = "Draw"
        away_result = "Draw"

    team_index_rows.append({
        "team_fixture_id": fixture["fixture_id"] + "__" + fixture["home_team_id"],
        "fixture_id": fixture["fixture_id"],
        "team_id": fixture["home_team_id"],
        "season_id": fixture["season_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": fixture["away_team_id"],
        "home_or_away": "Home",
        "team_score": fixture["home_score"],
        "opponent_score": fixture["away_score"],
        "result_for_team": home_result,
        "venue_id": fixture["venue_id"],
        "team_autonomous_region_id": "CT",
        "team_autonomous_region_name": "Catalonia",
        "team_autonomous_region_slug": "catalonia",
        "opponent_autonomous_region_id": "PV",
        "opponent_autonomous_region_name": "Basque Country",
        "opponent_autonomous_region_slug": "basque-country",
        "source_url": fixture["source_url"]
    })

    team_index_rows.append({
        "team_fixture_id": fixture["fixture_id"] + "__" + fixture["away_team_id"],
        "fixture_id": fixture["fixture_id"],
        "team_id": fixture["away_team_id"],
        "season_id": fixture["season_id"],
        "competition_name": fixture["competition_name"],
        "competition_group": fixture["competition_group"],
        "matchday": fixture["matchday"],
        "fixture_date": fixture["fixture_date"],
        "opponent_team_id": fixture["home_team_id"],
        "home_or_away": "Away",
        "team_score": fixture["away_score"],
        "opponent_score": fixture["home_score"],
        "result_for_team": away_result,
        "venue_id": fixture["venue_id"],
        "team_autonomous_region_id": "PV",
        "team_autonomous_region_name": "Basque Country",
        "team_autonomous_region_slug": "basque-country",
        "opponent_autonomous_region_id": "CT",
        "opponent_autonomous_region_name": "Catalonia",
        "opponent_autonomous_region_slug": "catalonia",
        "source_url": fixture["source_url"]
    })

team_index_fields = list(team_index_rows[0].keys())

with team_index_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=team_index_fields)
    writer.writeheader()
    writer.writerows(team_index_rows)

validation_file.write_text(
    "# Validation Report\n\n"
    "Starter workflow completed successfully.\n\n"
    "- fixtures_results.csv created\n"
    "- team_fixture_index.csv created\n"
    "- Two team index rows generated from one fixture\n"
    "- Autonomous region tags included\n",
    encoding="utf-8"
)

print("CSV export complete.")

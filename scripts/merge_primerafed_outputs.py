from pathlib import Path
import csv
import re
from datetime import datetime, timezone

EXPORT_DIR = Path("data/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.now(timezone.utc).isoformat()


def read_csv(path):
    if not path.exists():
        return []

    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(filename, fieldnames, rows=None):
    rows = rows or []

    export_path = EXPORT_DIR / filename
    with export_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    root_path = Path(filename)
    with root_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {export_path} and root copy {root_path}")


def make_team_id(name):
    value = (name or "").upper()
    value = value.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    value = value.replace("Ü", "U").replace("Ñ", "N").replace("Ç", "C")
    value = re.sub(r"[^A-Z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def make_fixture_id(season_id, competition_id, competition_group, matchday, home_team_id, away_team_id):
    group_slug = make_team_id(competition_group)
    return f"{season_id}_{competition_id}_{group_slug}_J{matchday}_{home_team_id}_v_{away_team_id}"


def result_for_team(team_score, opponent_score):
    if team_score == "" or opponent_score == "":
        return ""

    try:
        team_score = int(team_score)
        opponent_score = int(opponent_score)
    except Exception:
        return ""

    if team_score > opponent_score:
        return "W"
    if team_score < opponent_score:
        return "L"
    return "D"


fixture_fields = [
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

team_index_fields = [
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

missing_fields = [
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "fixture_phase",
    "matchday",
    "round_label",
    "missing_fixture_count",
    "reason",
    "recommended_action",
]

validation_fields = [
    "check_name",
    "result",
    "details",
]


grupo1_path = EXPORT_DIR / "primerafed_2025_26_fixtures_results_rfeffed_enhanced.csv"
grupo2_path = EXPORT_DIR / "grupo2_probe_parsed_fixtures.csv"

grupo1_rows = read_csv(grupo1_path)
grupo2_probe_rows = read_csv(grupo2_path)

final_fixture_rows = []
final_team_index_rows = []


# 1. Add Grupo 1 rows from the enhanced extractor.
for row in grupo1_rows:
    if row.get("competition_group") != "Grupo 1":
        continue

    final_fixture_rows.append({field: row.get(field, "") for field in fixture_fields})


# 2. Convert Grupo 2 probe rows into the same fixture schema.
for row in grupo2_probe_rows:
    if row.get("competition_group") != "Grupo 2":
        continue

    season_id = row.get("season_id", "2025-26")
    competition_id = row.get("competition_id", "PRIMERA_FEDERACION")
    competition_name = row.get("competition_name", "Primera Federación")
    competition_group = row.get("competition_group", "Grupo 2")
    matchday = row.get("matchday", "")
    fixture_date = row.get("fixture_date", "")
    home_team_name = row.get("home_team_name_source", "")
    away_team_name = row.get("away_team_name_source", "")
    home_score = row.get("home_score", "")
    away_score = row.get("away_score", "")

    home_team_id = make_team_id(home_team_name)
    away_team_id = make_team_id(away_team_name)

    fixture_id = make_fixture_id(
        season_id,
        competition_id,
        competition_group,
        matchday,
        home_team_id,
        away_team_id,
    )

    result_status = "played" if home_score != "" and away_score != "" else "scheduled"

    final_fixture_rows.append({
        "fixture_id": fixture_id,
        "season_id": season_id,
        "competition_id": competition_id,
        "competition_name": competition_name,
        "competition_level": "3",
        "competition_group": competition_group,
        "fixture_phase": "regular_season",
        "matchday": matchday,
        "round_label": f"Jornada {matchday}",
        "fixture_date": fixture_date,
        "kickoff_time_local": "",
        "home_team_id": home_team_id,
        "home_team_name_source": home_team_name,
        "away_team_id": away_team_id,
        "away_team_name_source": away_team_name,
        "home_score": home_score,
        "away_score": away_score,
        "result_status": result_status,
        "venue_id": "",
        "venue_name_source": "",
        "attendance": "",
        "referee": "",
        "match_report_url": "",
        "rfef_acta_url": "",
        "laliga_match_url": "",
        "source_system": "RFEF",
        "source_url": "https://marcadores.rfef.es/pnfg/NPcd/NFG_VisCalendario_Vis?cod_primaria=1000120&codtemporada=21&codjornada=1&codcompeticion=23289295&codgrupo=23289297",
        "source_retrieved_at": NOW,
        "data_confidence": row.get("data_confidence", "high"),
        "notes": "Merged from proven Grupo 2 probe calendar-view parser.",
    })


# 3. Deduplicate fixture rows by fixture_id.
deduped_fixture_rows = []
seen_fixture_ids = set()

for row in final_fixture_rows:
    fixture_id = row.get("fixture_id", "")

    if not fixture_id:
        continue

    if fixture_id in seen_fixture_ids:
        continue

    seen_fixture_ids.add(fixture_id)
    deduped_fixture_rows.append(row)

final_fixture_rows = deduped_fixture_rows


# 4. Build team fixture index from final fixture rows.
for fixture in final_fixture_rows:
    fixture_id = fixture.get("fixture_id", "")
    home_team_id = fixture.get("home_team_id", "")
    away_team_id = fixture.get("away_team_id", "")

    home_score = fixture.get("home_score", "")
    away_score = fixture.get("away_score", "")

    final_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{home_team_id}",
        "fixture_id": fixture_id,
        "team_id": home_team_id,
        "season_id": fixture.get("season_id", ""),
        "competition_id": fixture.get("competition_id", ""),
        "competition_name": fixture.get("competition_name", ""),
        "competition_group": fixture.get("competition_group", ""),
        "fixture_phase": fixture.get("fixture_phase", ""),
        "matchday": fixture.get("matchday", ""),
        "fixture_date": fixture.get("fixture_date", ""),
        "opponent_team_id": away_team_id,
        "home_or_away": "Home",
        "team_score": home_score,
        "opponent_score": away_score,
        "result_for_team": result_for_team(home_score, away_score),
        "venue_id": fixture.get("venue_id", ""),
        "is_home_ground": "true",
        "team_autonomous_region_id": "",
        "team_autonomous_region_name": "",
        "team_autonomous_region_slug": "",
        "opponent_autonomous_region_id": "",
        "opponent_autonomous_region_name": "",
        "opponent_autonomous_region_slug": "",
        "source_url": fixture.get("source_url", ""),
    })

    final_team_index_rows.append({
        "team_fixture_id": f"{fixture_id}__{away_team_id}",
        "fixture_id": fixture_id,
        "team_id": away_team_id,
        "season_id": fixture.get("season_id", ""),
        "competition_id": fixture.get("competition_id", ""),
        "competition_name": fixture.get("competition_name", ""),
        "competition_group": fixture.get("competition_group", ""),
        "fixture_phase": fixture.get("fixture_phase", ""),
        "matchday": fixture.get("matchday", ""),
        "fixture_date": fixture.get("fixture_date", ""),
        "opponent_team_id": home_team_id,
        "home_or_away": "Away",
        "team_score": away_score,
        "opponent_score": home_score,
        "result_for_team": result_for_team(away_score, home_score),
        "venue_id": fixture.get("venue_id", ""),
        "is_home_ground": "false",
        "team_autonomous_region_id": "",
        "team_autonomous_region_name": "",
        "team_autonomous_region_slug": "",
        "opponent_autonomous_region_id": "",
        "opponent_autonomous_region_name": "",
        "opponent_autonomous_region_slug": "",
        "source_url": fixture.get("source_url", ""),
    })


# 5. Missing fixtures audit for Grupo 1 J37-J38.
missing_rows = [
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 1",
        "fixture_phase": "regular_season",
        "matchday": "37",
        "round_label": "Jornada 37",
        "missing_fixture_count": "10",
        "reason": "Not exposed by tested RFEF result or calendar routes at extraction time.",
        "recommended_action": "Re-test RFEF later or fill from secondary source.",
    },
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 1",
        "fixture_phase": "regular_season",
        "matchday": "38",
        "round_label": "Jornada 38",
        "missing_fixture_count": "10",
        "reason": "Not exposed by tested RFEF result or calendar routes at extraction time.",
        "recommended_action": "Re-test RFEF later or fill from secondary source.",
    },
]


# 6. Validation.
fixture_ids = [row.get("fixture_id", "") for row in final_fixture_rows]
duplicate_fixture_ids = sorted([
    fixture_id for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

team_fixture_ids = [row.get("team_fixture_id", "") for row in final_team_index_rows]
duplicate_team_fixture_ids = sorted([
    team_fixture_id for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

grupo1_final = [row for row in final_fixture_rows if row.get("competition_group") == "Grupo 1"]
grupo2_final = [row for row in final_fixture_rows if row.get("competition_group") == "Grupo 2"]

counts_by_group_matchday = {}

for row in final_fixture_rows:
    key = f"{row.get('competition_group')}|J{row.get('matchday')}"
    counts_by_group_matchday[key] = counts_by_group_matchday.get(key, 0) + 1

unexpected_counts = [
    f"{key}={count}"
    for key, count in sorted(counts_by_group_matchday.items())
    if count != 10
]

validation_rows = [
    {
        "check_name": "input_grupo1_rows",
        "result": str(len(grupo1_rows)),
        "details": "Rows read from primerafed_2025_26_fixtures_results_rfeffed_enhanced.csv.",
    },
    {
        "check_name": "input_grupo2_probe_rows",
        "result": str(len(grupo2_probe_rows)),
        "details": "Rows read from grupo2_probe_parsed_fixtures.csv.",
    },
    {
        "check_name": "final_fixture_rows",
        "result": str(len(final_fixture_rows)),
        "details": "Expected 740: Grupo 1 J1-36 plus Grupo 2 J1-38.",
    },
    {
        "check_name": "final_team_fixture_index_rows",
        "result": str(len(final_team_index_rows)),
        "details": "Expected 1480.",
    },
    {
        "check_name": "final_grupo1_fixture_rows",
        "result": str(len(grupo1_final)),
        "details": "Expected 360.",
    },
    {
        "check_name": "final_grupo2_fixture_rows",
        "result": str(len(grupo2_final)),
        "details": "Expected 380.",
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
        "check_name": "unexpected_group_matchday_counts",
        "result": str(len(unexpected_counts)),
        "details": "|".join(unexpected_counts),
    },
    {
        "check_name": "known_missing_fixture_rows",
        "result": "20",
        "details": "Grupo 1 Jornada 37 and Jornada 38 remain missing.",
    },
]


# 7. Write outputs.
write_csv(
    "primerafed_2025_26_fixtures_results_final_candidate.csv",
    fixture_fields,
    final_fixture_rows,
)

write_csv(
    "primerafed_2025_26_team_fixture_index_final_candidate.csv",
    team_index_fields,
    final_team_index_rows,
)

write_csv(
    "primerafed_2025_26_missing_fixtures_audit.csv",
    missing_fields,
    missing_rows,
)

write_csv(
    "primerafed_2025_26_final_merge_validation.csv",
    validation_fields,
    validation_rows,
)

print("Primera Federación merge complete.")
print(f"Final fixture rows: {len(final_fixture_rows)}")
print(f"Final team fixture index rows: {len(final_team_index_rows)}")

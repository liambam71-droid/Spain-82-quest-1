from pathlib import Path
from datetime import datetime, timezone
import csv
import re

NOW = datetime.now(timezone.utc).isoformat()

PUBLIC_DATA_DIR = Path("public/data")
EXPORT_DIR = Path("data/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

CURRENT_FIXTURES_PATH = PUBLIC_DATA_DIR / "primerafed_2025_26_fixtures_results_current.csv"

# Optional latest-source files. The script will use whichever exist.
LATEST_SOURCE_CANDIDATES = [
    EXPORT_DIR / "primerafed_2025_26_fixtures_results_rfeffed_enhanced.csv",
    EXPORT_DIR / "grupo2_probe_parsed_fixtures.csv",
    Path("primerafed_2025_26_fixtures_results_rfeffed_enhanced.csv"),
    Path("grupo2_probe_parsed_fixtures.csv"),
]


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


def read_csv(path):
    if not path.exists():
        return []

    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, fieldnames, rows):
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}")


def make_team_id(name):
    value = (name or "").upper()
    value = value.replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    value = value.replace("Ü", "U").replace("Ñ", "N").replace("Ç", "C")
    value = re.sub(r"[^A-Z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value


def make_fixture_key(row):
    return "|".join([
        row.get("season_id", ""),
        row.get("competition_id", ""),
        row.get("competition_group", ""),
        str(row.get("matchday", row.get("cod_jornada", ""))),
        make_team_id(row.get("home_team_name_source", "")),
        make_team_id(row.get("away_team_name_source", "")),
    ])


def result_status(home_score, away_score):
    return "played" if home_score != "" and away_score != "" else "scheduled"


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


def normalise_latest_row(row):
    """
    Converts different extraction row shapes into the fixture schema enough for score refreshing.
    """
    matchday = row.get("matchday") or row.get("cod_jornada", "")

    season_id = row.get("season_id", "2025-26")
    competition_id = row.get("competition_id", "PRIMERA_FEDERACION")
    competition_name = row.get("competition_name", "Primera Federación")
    competition_group = row.get("competition_group", "")

    home_team_name = row.get("home_team_name_source", "")
    away_team_name = row.get("away_team_name_source", "")

    home_team_id = row.get("home_team_id") or make_team_id(home_team_name)
    away_team_id = row.get("away_team_id") or make_team_id(away_team_name)

    fixture_id = row.get("fixture_id", "")

    if not fixture_id and home_team_id and away_team_id:
        group_slug = make_team_id(competition_group)
        fixture_id = f"{season_id}_{competition_id}_{group_slug}_J{matchday}_{home_team_id}_v_{away_team_id}"

    return {
        "fixture_id": fixture_id,
        "season_id": season_id,
        "competition_id": competition_id,
        "competition_name": competition_name,
        "competition_level": row.get("competition_level", "3"),
        "competition_group": competition_group,
        "fixture_phase": row.get("fixture_phase", "regular_season"),
        "matchday": str(matchday),
        "round_label": row.get("round_label", f"Jornada {matchday}"),
        "fixture_date": row.get("fixture_date", ""),
        "kickoff_time_local": row.get("kickoff_time_local", ""),
        "home_team_id": home_team_id,
        "home_team_name_source": home_team_name,
        "away_team_id": away_team_id,
        "away_team_name_source": away_team_name,
        "home_score": row.get("home_score", ""),
        "away_score": row.get("away_score", ""),
        "result_status": result_status(row.get("home_score", ""), row.get("away_score", "")),
        "venue_id": row.get("venue_id", ""),
        "venue_name_source": row.get("venue_name_source", ""),
        "attendance": row.get("attendance", ""),
        "referee": row.get("referee", ""),
        "match_report_url": row.get("match_report_url", ""),
        "rfef_acta_url": row.get("rfef_acta_url", ""),
        "laliga_match_url": row.get("laliga_match_url", ""),
        "source_system": row.get("source_system", "RFEF"),
        "source_url": row.get("source_url", ""),
        "source_retrieved_at": NOW,
        "data_confidence": row.get("data_confidence", "high"),
        "notes": row.get("notes", "Refreshed from latest Primera Federación extraction source."),
    }


def build_team_index(fixtures):
    rows = []

    for fixture in fixtures:
        fixture_id = fixture.get("fixture_id", "")
        home_team_id = fixture.get("home_team_id", "")
        away_team_id = fixture.get("away_team_id", "")
        home_score = fixture.get("home_score", "")
        away_score = fixture.get("away_score", "")

        rows.append({
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

        rows.append({
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

    return rows


current_rows = read_csv(CURRENT_FIXTURES_PATH)

latest_rows = []

for path in LATEST_SOURCE_CANDIDATES:
    rows = read_csv(path)
    if rows:
        latest_rows.extend(rows)

latest_normalised = [
    normalise_latest_row(row)
    for row in latest_rows
    if row.get("home_team_name_source") and row.get("away_team_name_source")
]

latest_by_id = {
    row["fixture_id"]: row
    for row in latest_normalised
    if row.get("fixture_id")
}

latest_by_key = {
    make_fixture_key(row): row
    for row in latest_normalised
}

updated_rows = []
updated_score_count = 0
added_fixture_count = 0

existing_ids = set()

for current in current_rows:
    current = {field: current.get(field, "") for field in fixture_fields}
    existing_ids.add(current.get("fixture_id", ""))

    latest = latest_by_id.get(current.get("fixture_id", ""))

    if not latest:
        latest = latest_by_key.get(make_fixture_key(current))

    if latest:
        before_score = (current.get("home_score", ""), current.get("away_score", ""))

        # Only replace scores where latest has a complete score.
        if latest.get("home_score", "") != "" and latest.get("away_score", "") != "":
            current["home_score"] = latest["home_score"]
            current["away_score"] = latest["away_score"]
            current["result_status"] = "played"
            current["source_retrieved_at"] = NOW
            current["data_confidence"] = latest.get("data_confidence", current.get("data_confidence", ""))
            current["notes"] = "Score refreshed from latest Primera Federación extraction source."

        # Also refresh date/time if current is blank and latest has values.
        for field in ["fixture_date", "kickoff_time_local", "venue_name_source", "referee", "source_url"]:
            if not current.get(field) and latest.get(field):
                current[field] = latest[field]

        after_score = (current.get("home_score", ""), current.get("away_score", ""))

        if before_score != after_score:
            updated_score_count += 1

    updated_rows.append(current)


# Add only genuinely missing known-tail fixtures.
# Safety rule:
# - The current 2025-26 file already contains Grupo 1 J1-36 and Grupo 2 J1-38.
# - Do not add any "new" Grupo 2 fixtures during refresh, because slightly different IDs
#   can create duplicates.
# - Only allow new additions for the known missing Grupo 1 Jornadas 37 and 38.

allowed_new_fixture_keys = {
    "Grupo 1|37",
    "Grupo 1|38",
}

for latest in latest_normalised:
    fixture_id = latest.get("fixture_id", "")

    if not fixture_id or fixture_id in existing_ids:
        continue

    competition_group = latest.get("competition_group", "")
    matchday = str(latest.get("matchday", ""))

    allowed_key = f"{competition_group}|{matchday}"

    if allowed_key not in allowed_new_fixture_keys:
        continue

    updated_rows.append({field: latest.get(field, "") for field in fixture_fields})
    existing_ids.add(fixture_id)
    added_fixture_count += 1


team_index_rows = build_team_index(updated_rows)

validation_fields = ["check_name", "result", "details"]

fixture_ids = [row.get("fixture_id", "") for row in updated_rows]
duplicate_fixture_ids = sorted([fid for fid in set(fixture_ids) if fixture_ids.count(fid) > 1])

counts_by_group = {}
counts_by_group_matchday = {}

for row in updated_rows:
    group = row.get("competition_group", "")
    counts_by_group[group] = counts_by_group.get(group, 0) + 1

    key = f"{group}|J{row.get('matchday', '')}"
    counts_by_group_matchday[key] = counts_by_group_matchday.get(key, 0) + 1

unexpected_counts = [
    f"{key}={count}"
    for key, count in sorted(counts_by_group_matchday.items())
    if count != 10
]
blocked_new_fixture_candidates = []

for latest in latest_normalised:
    fixture_id = latest.get("fixture_id", "")

    if not fixture_id or fixture_id in existing_ids:
        continue

    competition_group = latest.get("competition_group", "")
    matchday = str(latest.get("matchday", ""))
    allowed_key = f"{competition_group}|{matchday}"

    if allowed_key not in allowed_new_fixture_keys:
        blocked_new_fixture_candidates.append(f"{allowed_key}|{fixture_id}")
validation_rows = [
    {
        "check_name": "current_input_rows",
        "result": str(len(current_rows)),
        "details": str(CURRENT_FIXTURES_PATH),
    },
    {
        "check_name": "latest_input_rows",
        "result": str(len(latest_normalised)),
        "details": "Rows read from available latest extraction/probe files.",
    },
    {
        "check_name": "updated_fixture_rows",
        "result": str(len(updated_rows)),
        "details": "Should be 740 now, 760 once Grupo 1 J37-J38 are added.",
    },
    {
        "check_name": "updated_team_index_rows",
        "result": str(len(team_index_rows)),
        "details": "Should be 2x fixture rows.",
    },
    {
        "check_name": "score_rows_updated",
        "result": str(updated_score_count),
        "details": "Fixtures where scores changed from the current file.",
    },
    {
        "check_name": "new_fixtures_added", 
        "result": str(added_fixture_count),
        "details": "Should become 20 when Grupo 1 J37-J38 are added.",
    },
    {
        "check_name": "blocked_new_fixture_candidates",
        "result": str(len(blocked_new_fixture_candidates)),
        "details": "|".join(blocked_new_fixture_candidates[:100]),
    },
    {
        "check_name": "grupo_1_rows",
        "result": str(counts_by_group.get("Grupo 1", 0)),
        "details": "Currently 360; target 380.",
    },
    {
        "check_name": "grupo_2_rows",
        "result": str(counts_by_group.get("Grupo 2", 0)),
        "details": "Target 380.",
    },
    {
        "check_name": "duplicate_fixture_ids",
        "result": str(len(duplicate_fixture_ids)),
        "details": "|".join(duplicate_fixture_ids),
    },
    {
        "check_name": "unexpected_group_matchday_counts",
        "result": str(len(unexpected_counts)),
        "details": "|".join(unexpected_counts),
    },
]

write_csv(
    PUBLIC_DATA_DIR / "primerafed_2025_26_fixtures_results_current.csv",
    fixture_fields,
    updated_rows,
)

write_csv(
    PUBLIC_DATA_DIR / "primerafed_2025_26_team_fixture_index_current.csv",
    team_index_fields,
    team_index_rows,
)

write_csv(
    EXPORT_DIR / "primerafed_2025_26_refresh_validation.csv",
    validation_fields,
    validation_rows,
)

write_csv(
    Path("primerafed_2025_26_refresh_validation.csv"),
    validation_fields,
    validation_rows,
)

print("Primera Federación current file refresh complete.")
print(f"Updated fixture rows: {len(updated_rows)}")
print(f"Updated team index rows: {len(team_index_rows)}")
print(f"Scores updated: {updated_score_count}")
print(f"New fixtures added: {added_fixture_count}")

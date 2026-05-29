from pathlib import Path
from datetime import datetime, timezone
import csv
import re

EXPORT_DIR = Path("data/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

NOW = datetime.now(timezone.utc).isoformat()


def write_csv(filename, fieldnames, rows=None):
    rows = rows or []
    path = EXPORT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}")


def make_team_id(name):
    value = name.upper()
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


# -----------------------------
# Known RFEF Primera Federación 2025/26 regular-season codes
# Discovered from RFEF classification response.
# -----------------------------

GROUPS = [
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_level": "3",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
    },
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_level": "3",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
    },
]


# -----------------------------
# Parser helpers
# -----------------------------

def is_date(value):
    return bool(re.match(r"^[0-9]{2}-[0-9]{2}-[0-9]{4}$", value.strip()))


def normalise_date(value):
    # RFEF gives DD-MM-YYYY. Convert to YYYY-MM-DD.
    value = value.strip()
    match = re.match(r"^([0-9]{2})-([0-9]{2})-([0-9]{4})$", value)
    if not match:
        return value

    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def is_time(value):
    return bool(re.match(r"^[0-9]{1,2}:[0-9]{2}$", value.strip()))


def is_score_marker(value):
    value = value.strip()
    return bool(
        value == "-"
        or re.match(r"^[0-9]{1,2}\s*-\s*[0-9]{1,2}$", value)
        or re.match(r"^[0-9]{1,2}\s*-$", value)
        or re.match(r"^-\s*[0-9]{1,2}$", value)
    )


def parse_score(value):
    value = value.strip()

    if value == "-":
        return "", ""

    match = re.match(r"^([0-9]{1,2})\s*-\s*([0-9]{1,2})$", value)
    if match:
        return match.group(1), match.group(2)

    match = re.match(r"^([0-9]{1,2})\s*-$", value)
    if match:
        return match.group(1), ""

    match = re.match(r"^-\s*([0-9]{1,2})$", value)
    if match:
        return "", match.group(1)

    return "", ""


def clean_lines(text):
    lines = []

    skip_exact = {
        "Competiciones",
        "Acciones",
        "Calendario Clasificaciones y Resultados Búsqueda por competición",
        "Filtro de búsqueda Avanzado",
        "Siguiente",
        "Anterior",
        "Provisional Definitivo",
        "RESULTADOS",
        "Calendario Clasificación Tabla Cruzada Goleadores Porteros",
        "Calendario",
        "Clasificación",
        "Tabla Cruzada",
        "Goleadores",
        "Porteros",
    }

    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()

        if not cleaned:
            continue

        if cleaned in skip_exact:
            continue

        if cleaned.startswith("Temporada "):
            continue

        if cleaned.startswith("Campeonato Nacional de Liga de Primera Federación"):
            continue

        if cleaned.startswith("Jornada "):
            continue

        lines.append(cleaned)

    return lines


def parse_fixtures_from_lines(lines):
    fixtures = []
    i = 0

    while i < len(lines):
        # Expected sequence:
        # home_team, score_marker, date, time, away_team, venue, optional Árbitro:, optional referee
        if i + 5 < len(lines):
            home = lines[i]
            score_marker = lines[i + 1]
            date_value = lines[i + 2]
            time_value = lines[i + 3]
            away = lines[i + 4]
            venue = lines[i + 5]

            if (
                is_score_marker(score_marker)
                and is_date(date_value)
                and is_time(time_value)
                and home.lower() != "árbitro:"
                and away.lower() != "árbitro:"
            ):
                home_score, away_score = parse_score(score_marker)

                referee = ""
                consumed = 6

                if i + 7 < len(lines) and lines[i + 6].lower().startswith("árbitro"):
                    referee = lines[i + 7]
                    consumed = 8

                fixtures.append({
                    "home_team_name_source": home,
                    "away_team_name_source": away,
                    "home_score": home_score,
                    "away_score": away_score,
                    "fixture_date": normalise_date(date_value),
                    "kickoff_time_local": time_value,
                    "venue_name_source": venue,
                    "referee": referee,
                    "raw_sequence": " | ".join(lines[i:i + consumed]),
                    "data_confidence": "high" if home and away and date_value and time_value else "needs_review",
                    "notes": "Parsed from RFEF visible text sequence.",
                })

                i += consumed
                continue

        i += 1

    return fixtures


# -----------------------------
# Output fields
# -----------------------------

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

raw_fields = [
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "fixture_index",
    "source_url",
    "home_team_name_source",
    "away_team_name_source",
    "home_score",
    "away_score",
    "fixture_date",
    "kickoff_time_local",
    "venue_name_source",
    "referee",
    "raw_sequence",
    "data_confidence",
    "notes",
]


# -----------------------------
# Extraction
# -----------------------------

raw_rows = []
fixture_rows = []
team_index_rows = []

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Establish one RFEF session first.
        session_page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        session_page.goto("https://marcadores.rfef.es/pnfg/?accion=1", wait_until="networkidle", timeout=60000)

        for selector in [
            "text=Aceptar",
            "text=ACEPTAR",
            "text=Accept",
            "button:has-text('Aceptar')",
            "button:has-text('ACEPTAR')",
        ]:
            try:
                if session_page.locator(selector).count() > 0:
                    session_page.locator(selector).first.click(timeout=3000)
                    session_page.wait_for_timeout(1000)
                    break
            except Exception:
                pass

        for group in GROUPS:
            for jornada in range(1, 39):
                matchday = str(jornada)

                source_url = (
                    "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
                    "?cod_primaria=1000120"
                    f"&CodTemporada={group['cod_temporada']}"
                    f"&CodJornada={matchday}"
                    f"&CodCompeticion={group['cod_competicion']}"
                    f"&CodGrupo={group['cod_grupo']}"
                )

                try:
                    page = browser.new_page(
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        )
                    )

                    page.goto(source_url, wait_until="networkidle", timeout=60000)
                    page.wait_for_timeout(1000)

                    page_text = page.inner_text("body")
                    page_html = page.content()

                    safe_name = re.sub(
                        r"[^A-Za-z0-9]+",
                        "_",
                        f"{group['competition_group']}_jornada_{matchday}",
                    ).strip("_").lower()

                    # Save failed/diagnostic files only lightly to keep artifact smaller.
                    text_path = EXPORT_DIR / f"primerafed_extract_{safe_name}_text.txt"
                    text_path.write_text(page_text[:300000], encoding="utf-8")

                    html_path = EXPORT_DIR / f"primerafed_extract_{safe_name}.html"
                    html_path.write_text(page_html[:500000], encoding="utf-8")

                    lines = clean_lines(page_text)
                    fixtures = parse_fixtures_from_lines(lines)

                    if not fixtures:
                        raw_rows.append({
                            "season_id": group["season_id"],
                            "competition_id": group["competition_id"],
                            "competition_name": group["competition_name"],
                            "competition_group": group["competition_group"],
                            "cod_temporada": group["cod_temporada"],
                            "cod_competicion": group["cod_competicion"],
                            "cod_grupo": group["cod_grupo"],
                            "cod_jornada": matchday,
                            "fixture_index": "",
                            "source_url": source_url,
                            "home_team_name_source": "",
                            "away_team_name_source": "",
                            "home_score": "",
                            "away_score": "",
                            "fixture_date": "",
                            "kickoff_time_local": "",
                            "venue_name_source": "",
                            "referee": "",
                            "raw_sequence": "",
                            "data_confidence": "failed",
                            "notes": "No fixtures parsed from page. Inspect saved text/html.",
                        })

                    for fixture_index, fixture in enumerate(fixtures):
                        raw_row = {
                            "season_id": group["season_id"],
                            "competition_id": group["competition_id"],
                            "competition_name": group["competition_name"],
                            "competition_group": group["competition_group"],
                            "cod_temporada": group["cod_temporada"],
                            "cod_competicion": group["cod_competicion"],
                            "cod_grupo": group["cod_grupo"],
                            "cod_jornada": matchday,
                            "fixture_index": str(fixture_index),
                            "source_url": source_url,
                            "home_team_name_source": fixture["home_team_name_source"],
                            "away_team_name_source": fixture["away_team_name_source"],
                            "home_score": fixture["home_score"],
                            "away_score": fixture["away_score"],
                            "fixture_date": fixture["fixture_date"],
                            "kickoff_time_local": fixture["kickoff_time_local"],
                            "venue_name_source": fixture["venue_name_source"],
                            "referee": fixture["referee"],
                            "raw_sequence": fixture["raw_sequence"],
                            "data_confidence": fixture["data_confidence"],
                            "notes": fixture["notes"],
                        }

                        raw_rows.append(raw_row)

                        home_team_id = make_team_id(fixture["home_team_name_source"])
                        away_team_id = make_team_id(fixture["away_team_name_source"])

                        fixture_id = make_fixture_id(
                            group["season_id"],
                            group["competition_id"],
                            group["competition_group"],
                            matchday,
                            home_team_id,
                            away_team_id,
                        )

                        result_status = "played" if fixture["home_score"] != "" and fixture["away_score"] != "" else "scheduled"

                        fixture_rows.append({
                            "fixture_id": fixture_id,
                            "season_id": group["season_id"],
                            "competition_id": group["competition_id"],
                            "competition_name": group["competition_name"],
                            "competition_level": group["competition_level"],
                            "competition_group": group["competition_group"],
                            "fixture_phase": "regular_season",
                            "matchday": matchday,
                            "round_label": f"Jornada {matchday}",
                            "fixture_date": fixture["fixture_date"],
                            "kickoff_time_local": fixture["kickoff_time_local"],
                            "home_team_id": home_team_id,
                            "home_team_name_source": fixture["home_team_name_source"],
                            "away_team_id": away_team_id,
                            "away_team_name_source": fixture["away_team_name_source"],
                            "home_score": fixture["home_score"],
                            "away_score": fixture["away_score"],
                            "result_status": result_status,
                            "venue_id": "",
                            "venue_name_source": fixture["venue_name_source"],
                            "attendance": "",
                            "referee": fixture["referee"],
                            "match_report_url": "",
                            "rfef_acta_url": "",
                            "laliga_match_url": "",
                            "source_system": "RFEF",
                            "source_url": source_url,
                            "source_retrieved_at": NOW,
                            "data_confidence": fixture["data_confidence"],
                            "notes": "Generated by clean Primera Federación RFEF extractor.",
                        })

                        # Home team index row
                        team_index_rows.append({
                            "team_fixture_id": f"{fixture_id}__{home_team_id}",
                            "fixture_id": fixture_id,
                            "team_id": home_team_id,
                            "season_id": group["season_id"],
                            "competition_id": group["competition_id"],
                            "competition_name": group["competition_name"],
                            "competition_group": group["competition_group"],
                            "fixture_phase": "regular_season",
                            "matchday": matchday,
                            "fixture_date": fixture["fixture_date"],
                            "opponent_team_id": away_team_id,
                            "home_or_away": "Home",
                            "team_score": fixture["home_score"],
                            "opponent_score": fixture["away_score"],
                            "result_for_team": result_for_team(fixture["home_score"], fixture["away_score"]),
                            "venue_id": "",
                            "is_home_ground": "true",
                            "team_autonomous_region_id": "",
                            "team_autonomous_region_name": "",
                            "team_autonomous_region_slug": "",
                            "opponent_autonomous_region_id": "",
                            "opponent_autonomous_region_name": "",
                            "opponent_autonomous_region_slug": "",
                            "source_url": source_url,
                        })

                        # Away team index row
                        team_index_rows.append({
                            "team_fixture_id": f"{fixture_id}__{away_team_id}",
                            "fixture_id": fixture_id,
                            "team_id": away_team_id,
                            "season_id": group["season_id"],
                            "competition_id": group["competition_id"],
                            "competition_name": group["competition_name"],
                            "competition_group": group["competition_group"],
                            "fixture_phase": "regular_season",
                            "matchday": matchday,
                            "fixture_date": fixture["fixture_date"],
                            "opponent_team_id": home_team_id,
                            "home_or_away": "Away",
                            "team_score": fixture["away_score"],
                            "opponent_score": fixture["home_score"],
                            "result_for_team": result_for_team(fixture["away_score"], fixture["home_score"]),
                            "venue_id": "",
                            "is_home_ground": "false",
                            "team_autonomous_region_id": "",
                            "team_autonomous_region_name": "",
                            "team_autonomous_region_slug": "",
                            "opponent_autonomous_region_id": "",
                            "opponent_autonomous_region_name": "",
                            "opponent_autonomous_region_slug": "",
                            "source_url": source_url,
                        })

                    page.close()

                except Exception as e:
                    raw_rows.append({
                        "season_id": group["season_id"],
                        "competition_id": group["competition_id"],
                        "competition_name": group["competition_name"],
                        "competition_group": group["competition_group"],
                        "cod_temporada": group["cod_temporada"],
                        "cod_competicion": group["cod_competicion"],
                        "cod_grupo": group["cod_grupo"],
                        "cod_jornada": matchday,
                        "fixture_index": "",
                        "source_url": source_url,
                        "home_team_name_source": "",
                        "away_team_name_source": "",
                        "home_score": "",
                        "away_score": "",
                        "fixture_date": "",
                        "kickoff_time_local": "",
                        "venue_name_source": "",
                        "referee": "",
                        "raw_sequence": "",
                        "data_confidence": "failed",
                        "notes": f"Extraction failed: {type(e).__name__}: {e}",
                    })

        browser.close()

except Exception as e:
    raw_rows.append({
        "season_id": "",
        "competition_id": "",
        "competition_name": "",
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "fixture_index": "",
        "source_url": "",
        "home_team_name_source": "",
        "away_team_name_source": "",
        "home_score": "",
        "away_score": "",
        "fixture_date": "",
        "kickoff_time_local": "",
        "venue_name_source": "",
        "referee": "",
        "raw_sequence": "",
        "data_confidence": "failed",
        "notes": f"Clean RFEF extractor failed: {type(e).__name__}: {e}",
    })


# -----------------------------
# Write outputs
# -----------------------------

write_csv(
    "primerafed_2025_26_raw_rfeffixture_extract.csv",
    raw_fields,
    raw_rows,
)

write_csv(
    "primerafed_2025_26_fixtures_results_rfeffed_clean.csv",
    fixture_fields,
    fixture_rows,
)

write_csv(
    "primerafed_2025_26_team_fixture_index_rfeffed_clean.csv",
    team_index_fields,
    team_index_rows,
)


# -----------------------------
# Validation
# -----------------------------

validation_fields = [
    "check_name",
    "result",
    "details",
]

non_failed_raw_rows = [
    row for row in raw_rows
    if row.get("data_confidence") != "failed"
]

failed_raw_rows = [
    row for row in raw_rows
    if row.get("data_confidence") == "failed"
]

high_rows = [
    row for row in raw_rows
    if row.get("data_confidence") == "high"
]

grupo_1_rows = [
    row for row in non_failed_raw_rows
    if row.get("competition_group") == "Grupo 1"
]

grupo_2_rows = [
    row for row in non_failed_raw_rows
    if row.get("competition_group") == "Grupo 2"
]

fixture_ids = [
    row["fixture_id"]
    for row in fixture_rows
    if row.get("fixture_id")
]

duplicate_fixture_ids = sorted([
    fixture_id for fixture_id in set(fixture_ids)
    if fixture_ids.count(fixture_id) > 1
])

team_fixture_ids = [
    row["team_fixture_id"]
    for row in team_index_rows
    if row.get("team_fixture_id")
]

duplicate_team_fixture_ids = sorted([
    team_fixture_id for team_fixture_id in set(team_fixture_ids)
    if team_fixture_ids.count(team_fixture_id) > 1
])

rows_by_group_jornada = {}

for row in non_failed_raw_rows:
    key = f"{row.get('competition_group')}|J{row.get('cod_jornada')}"
    rows_by_group_jornada[key] = rows_by_group_jornada.get(key, 0) + 1

unexpected_jornada_counts = [
    f"{key}={count}"
    for key, count in sorted(rows_by_group_jornada.items())
    if count != 10
]

validation_rows = [
    {
        "check_name": "raw_fixture_rows_non_failed",
        "result": str(len(non_failed_raw_rows)),
        "details": "Target is 760 if both groups and all 38 jornadas extract.",
    },
    {
        "check_name": "fixture_rows_clean",
        "result": str(len(fixture_rows)),
        "details": "Should match non-failed raw fixture rows.",
    },
    {
        "check_name": "team_fixture_index_rows",
        "result": str(len(team_index_rows)),
        "details": "Should be 2x fixture_rows_clean.",
    },
    {
        "check_name": "grupo_1_fixture_rows_non_failed",
        "result": str(len(grupo_1_rows)),
        "details": "Target is 380.",
    },
    {
        "check_name": "grupo_2_fixture_rows_non_failed",
        "result": str(len(grupo_2_rows)),
        "details": "Target is 380.",
    },
    {
        "check_name": "high_confidence_rows",
        "result": str(len(high_rows)),
        "details": "Target equals non-failed raw fixture rows.",
    },
    {
        "check_name": "failed_raw_rows",
        "result": str(len(failed_raw_rows)),
        "details": "Target is 0.",
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
        "check_name": "unexpected_jornada_counts",
        "result": str(len(unexpected_jornada_counts)),
        "details": "|".join(unexpected_jornada_counts[:100]),
    },
]

write_csv(
    "primerafed_2025_26_rfeffed_clean_validation_summary.csv",
    validation_fields,
    validation_rows,
)

print(f"Clean Primera Federación extractor produced {len(fixture_rows)} fixture rows.")
print(f"Clean Primera Federación extractor produced {len(team_index_rows)} team fixture rows.")
print(f"Failed raw rows: {len(failed_raw_rows)}")

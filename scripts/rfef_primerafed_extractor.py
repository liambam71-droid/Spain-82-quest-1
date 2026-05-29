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
# -----------------------------
# Failure audit: inspect failed Primera Federación pages
# -----------------------------

failure_audit_fields = [
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "expected_text_file",
    "text_file_exists",
    "text_length",
    "first_120_lines",
    "contains_primera_federacion",
    "contains_jornada",
    "contains_resultados",
    "contains_no_data",
    "notes",
]

failure_audit_rows = []

try:
    failed_pages = [
        row for row in raw_rows
        if row.get("data_confidence") == "failed"
    ]

    for row in failed_pages:
        competition_group = row.get("competition_group", "")
        cod_jornada = row.get("cod_jornada", "")

        safe_name = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            f"{competition_group}_jornada_{cod_jornada}",
        ).strip("_").lower()

        text_filename = f"primerafed_extract_{safe_name}_text.txt"
        text_path = EXPORT_DIR / text_filename

        text_exists = text_path.exists()
        page_text = ""

        if text_exists:
            page_text = text_path.read_text(encoding="utf-8", errors="ignore")

        page_text_lower = page_text.lower()

        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in page_text.splitlines()
            if re.sub(r"\s+", " ", line).strip()
        ]

        first_120_lines = " | ".join(lines[:120])

        contains_no_data = (
            "no hay datos" in page_text_lower
            or "sin datos" in page_text_lower
            or "no existen" in page_text_lower
            or "no se encontraron" in page_text_lower
            or "no se han encontrado" in page_text_lower
            or "no existen registros" in page_text_lower
        )

        failure_audit_rows.append({
            "competition_group": competition_group,
            "cod_temporada": row.get("cod_temporada", ""),
            "cod_competicion": row.get("cod_competicion", ""),
            "cod_grupo": row.get("cod_grupo", ""),
            "cod_jornada": cod_jornada,
            "expected_text_file": text_filename,
            "text_file_exists": str(text_exists).lower(),
            "text_length": str(len(page_text)),
            "first_120_lines": first_120_lines[:8000],
            "contains_primera_federacion": str(
                "primera federación" in page_text_lower
                or "primera federacion" in page_text_lower
                or "primera federaci" in page_text_lower
            ).lower(),
            "contains_jornada": str("jornada" in page_text_lower).lower(),
            "contains_resultados": str(
                "resultado" in page_text_lower
                or "resultados" in page_text_lower
            ).lower(),
            "contains_no_data": str(contains_no_data).lower(),
            "notes": row.get("notes", ""),
        })

except Exception as e:
    failure_audit_rows.append({
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "expected_text_file": "",
        "text_file_exists": "false",
        "text_length": "0",
        "first_120_lines": "",
        "contains_primera_federacion": "false",
        "contains_jornada": "false",
        "contains_resultados": "false",
        "contains_no_data": "false",
        "notes": f"Failure audit failed: {type(e).__name__}: {e}",
    })

write_csv(
    "primerafed_2025_26_failed_pages_audit.csv",
    failure_audit_fields,
    failure_audit_rows,
)

# Also write a root-level copy so it is easy to find in the GitHub artifact.
root_audit_path = Path("primerafed_2025_26_failed_pages_audit.csv")

with root_audit_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=failure_audit_fields)
    writer.writeheader()
    writer.writerows(failure_audit_rows)

print("Created failed pages audit: primerafed_2025_26_failed_pages_audit.csv")
# -----------------------------
# HTML failure audit: inspect failed Primera Federación page HTML
# -----------------------------

html_failure_audit_fields = [
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "expected_html_file",
    "html_file_exists",
    "html_length",
    "first_html_fragment",
    "contains_cookie_message",
    "contains_no_cookie",
    "contains_primera_federacion",
    "contains_jornada",
    "contains_resultados",
    "contains_body",
    "contains_script",
    "contains_iframe",
    "contains_no_data",
    "notes",
]

html_failure_audit_rows = []

try:
    failed_pages = [
        row for row in raw_rows
        if row.get("data_confidence") == "failed"
    ]

    for row in failed_pages:
        competition_group = row.get("competition_group", "")
        cod_jornada = row.get("cod_jornada", "")

        safe_name = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            f"{competition_group}_jornada_{cod_jornada}",
        ).strip("_").lower()

        html_filename = f"primerafed_extract_{safe_name}.html"
        html_path = EXPORT_DIR / html_filename

        html_exists = html_path.exists()
        page_html = ""

        if html_exists:
            page_html = html_path.read_text(encoding="utf-8", errors="ignore")

        html_lower = page_html.lower()

        first_html_fragment = re.sub(r"\s+", " ", page_html[:8000]).strip()

        contains_cookie_message = (
            "no se ha aceptado el cookie" in html_lower
            or "no se ha aceptado la cookie" in html_lower
            or "aceptar cookies" in html_lower
            or "aceptar cookie" in html_lower
        )

        contains_no_cookie = (
            "cookie" in html_lower
            and (
                "no se ha aceptado" in html_lower
                or "aceptar" in html_lower
            )
        )

        contains_no_data = (
            "no hay datos" in html_lower
            or "sin datos" in html_lower
            or "no existen" in html_lower
            or "no se encontraron" in html_lower
            or "no se han encontrado" in html_lower
            or "no existen registros" in html_lower
        )

        html_failure_audit_rows.append({
            "competition_group": competition_group,
            "cod_temporada": row.get("cod_temporada", ""),
            "cod_competicion": row.get("cod_competicion", ""),
            "cod_grupo": row.get("cod_grupo", ""),
            "cod_jornada": cod_jornada,
            "expected_html_file": html_filename,
            "html_file_exists": str(html_exists).lower(),
            "html_length": str(len(page_html)),
            "first_html_fragment": first_html_fragment[:8000],
            "contains_cookie_message": str(contains_cookie_message).lower(),
            "contains_no_cookie": str(contains_no_cookie).lower(),
            "contains_primera_federacion": str(
                "primera federación" in html_lower
                or "primera federacion" in html_lower
                or "primera federaci" in html_lower
            ).lower(),
            "contains_jornada": str("jornada" in html_lower).lower(),
            "contains_resultados": str(
                "resultado" in html_lower
                or "resultados" in html_lower
            ).lower(),
            "contains_body": str("<body" in html_lower).lower(),
            "contains_script": str("<script" in html_lower).lower(),
            "contains_iframe": str("<iframe" in html_lower).lower(),
            "contains_no_data": str(contains_no_data).lower(),
            "notes": row.get("notes", ""),
        })

except Exception as e:
    html_failure_audit_rows.append({
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "expected_html_file": "",
        "html_file_exists": "false",
        "html_length": "0",
        "first_html_fragment": "",
        "contains_cookie_message": "false",
        "contains_no_cookie": "false",
        "contains_primera_federacion": "false",
        "contains_jornada": "false",
        "contains_resultados": "false",
        "contains_body": "false",
        "contains_script": "false",
        "contains_iframe": "false",
        "contains_no_data": "false",
        "notes": f"HTML failure audit failed: {type(e).__name__}: {e}",
    })

write_csv(
    "primerafed_2025_26_failed_pages_html_audit.csv",
    html_failure_audit_fields,
    html_failure_audit_rows,
)

# Also write a root-level copy so it is easy to find in the GitHub artifact.
root_html_audit_path = Path("primerafed_2025_26_failed_pages_html_audit.csv")

with root_html_audit_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=html_failure_audit_fields)
    writer.writeheader()
    writer.writerows(html_failure_audit_rows)

print("Created HTML failed pages audit: primerafed_2025_26_failed_pages_html_audit.csv")
# -----------------------------
# Focused network audit:
# Compare working Grupo 1 J1 vs empty Grupo 2 J1
# -----------------------------

network_compare_fields = [
    "test_name",
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "request_index",
    "method",
    "resource_type",
    "url",
    "post_data",
    "response_status",
    "response_length",
    "contains_primera_federacion",
    "contains_jornada",
    "contains_resultados",
    "contains_team_sequence",
    "sample_text",
    "notes",
]

network_compare_rows = []

network_tests = [
    {
        "test_name": "Working comparison - Grupo 1 Jornada 1",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": "1",
    },
    {
        "test_name": "Empty comparison - Grupo 2 Jornada 1",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": "1",
    },
]


def focused_safe_decode(body):
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return body.decode(encoding), encoding
        except Exception:
            pass

    return body.decode("utf-8", errors="ignore"), "utf-8-ignore"


try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for test in network_tests:
            captured = []

            source_url = (
                "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
                "?cod_primaria=1000120"
                f"&CodTemporada={test['cod_temporada']}"
                f"&CodJornada={test['cod_jornada']}"
                f"&CodCompeticion={test['cod_competicion']}"
                f"&CodGrupo={test['cod_grupo']}"
            )

            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            def capture_response(response):
                try:
                    request = response.request
                    resource_type = request.resource_type
                    url = request.url

                    # Keep potentially relevant responses only.
                    interesting = (
                        "pnfg" in url.lower()
                        or "nfg" in url.lower()
                        or resource_type in ["document", "xhr", "fetch"]
                    )

                    if not interesting:
                        return

                    try:
                        body = response.body()
                        response_text, decode_method = focused_safe_decode(body)
                    except Exception as response_error:
                        response_text = f"Could not read response body: {type(response_error).__name__}: {response_error}"
                        decode_method = "failed"

                    captured.append({
                        "method": request.method,
                        "resource_type": resource_type,
                        "url": url,
                        "post_data": request.post_data or "",
                        "response_status": response.status,
                        "response_text": response_text,
                        "decode_method": decode_method,
                    })

                except Exception:
                    pass

            page.on("response", capture_response)

            try:
                # Establish session first.
                page.goto("https://marcadores.rfef.es/pnfg/?accion=1", wait_until="networkidle", timeout=60000)

                for selector in [
                    "text=Aceptar",
                    "text=ACEPTAR",
                    "text=Accept",
                    "button:has-text('Aceptar')",
                    "button:has-text('ACEPTAR')",
                ]:
                    try:
                        if page.locator(selector).count() > 0:
                            page.locator(selector).first.click(timeout=3000)
                            page.wait_for_timeout(1000)
                            break
                    except Exception:
                        pass

                # Now open target jornada URL.
                page.goto(source_url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(5000)

                # Save final page body/html for this exact test.
                final_text = page.inner_text("body")
                final_html = page.content()

                safe_test_name = re.sub(
                    r"[^A-Za-z0-9]+",
                    "_",
                    test["test_name"],
                ).strip("_").lower()

                (EXPORT_DIR / f"primerafed_network_compare_{safe_test_name}_final_text.txt").write_text(
                    final_text[:300000],
                    encoding="utf-8",
                )

                (EXPORT_DIR / f"primerafed_network_compare_{safe_test_name}_final_html.html").write_text(
                    final_html[:500000],
                    encoding="utf-8",
                )

                for request_index, item in enumerate(captured):
                    response_text = item["response_text"]
                    response_lower = response_text.lower()

                    # Save each captured response body for manual inspection.
                    response_filename = (
                        f"primerafed_network_compare_{safe_test_name}_response_{request_index}.txt"
                    )
                    (EXPORT_DIR / response_filename).write_text(
                        response_text[:500000],
                        encoding="utf-8",
                    )

                    plain_sample = re.sub(r"<[^>]+>", " ", response_text[:5000])
                    plain_sample = re.sub(r"\s+", " ", plain_sample).strip()

                    contains_team_sequence = bool(
                        re.search(
                            r"\n\s*-\s*\n\s*[0-9]{2}-[0-9]{2}-[0-9]{4}\s*\n\s*[0-9]{1,2}:[0-9]{2}",
                            response_text,
                        )
                    )

                    network_compare_rows.append({
                        "test_name": test["test_name"],
                        "competition_group": test["competition_group"],
                        "cod_temporada": test["cod_temporada"],
                        "cod_competicion": test["cod_competicion"],
                        "cod_grupo": test["cod_grupo"],
                        "cod_jornada": test["cod_jornada"],
                        "request_index": str(request_index),
                        "method": item["method"],
                        "resource_type": item["resource_type"],
                        "url": item["url"],
                        "post_data": item["post_data"],
                        "response_status": str(item["response_status"]),
                        "response_length": str(len(response_text)),
                        "contains_primera_federacion": str(
                            "primera federación" in response_lower
                            or "primera federacion" in response_lower
                            or "primera federaci" in response_lower
                        ).lower(),
                        "contains_jornada": str("jornada" in response_lower).lower(),
                        "contains_resultados": str(
                            "resultado" in response_lower
                            or "resultados" in response_lower
                        ).lower(),
                        "contains_team_sequence": str(contains_team_sequence).lower(),
                        "sample_text": plain_sample[:3000],
                        "notes": f"Captured response. Decode method: {item['decode_method']}.",
                    })

            except Exception as e:
                network_compare_rows.append({
                    "test_name": test["test_name"],
                    "competition_group": test["competition_group"],
                    "cod_temporada": test["cod_temporada"],
                    "cod_competicion": test["cod_competicion"],
                    "cod_grupo": test["cod_grupo"],
                    "cod_jornada": test["cod_jornada"],
                    "request_index": "",
                    "method": "",
                    "resource_type": "",
                    "url": source_url,
                    "post_data": "",
                    "response_status": "",
                    "response_length": "0",
                    "contains_primera_federacion": "false",
                    "contains_jornada": "false",
                    "contains_resultados": "false",
                    "contains_team_sequence": "false",
                    "sample_text": "",
                    "notes": f"Focused network comparison failed: {type(e).__name__}: {e}",
                })

            page.close()

        browser.close()

except Exception as e:
    network_compare_rows.append({
        "test_name": "stage_error",
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "request_index": "",
        "method": "",
        "resource_type": "",
        "url": "",
        "post_data": "",
        "response_status": "",
        "response_length": "0",
        "contains_primera_federacion": "false",
        "contains_jornada": "false",
        "contains_resultados": "false",
        "contains_team_sequence": "false",
        "sample_text": "",
        "notes": f"Focused network comparison stage failed: {type(e).__name__}: {e}",
    })

write_csv(
    "primerafed_2025_26_network_compare_g1j1_vs_g2j1.csv",
    network_compare_fields,
    network_compare_rows,
)

# Also write root-level copy for easy artifact access.
root_network_compare_path = Path("primerafed_2025_26_network_compare_g1j1_vs_g2j1.csv")

with root_network_compare_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=network_compare_fields)
    writer.writeheader()
    writer.writerows(network_compare_rows)

print("Created focused network comparison: primerafed_2025_26_network_compare_g1j1_vs_g2j1.csv")
# -----------------------------
# Grupo 2 route matrix:
# Test alternative RFEF route/parameter shapes for Primera Federación Grupo 2
# -----------------------------

route_matrix_fields = [
    "test_name",
    "host",
    "route_name",
    "cod_primaria",
    "parameter_style",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "test_url",
    "http_status",
    "page_loaded",
    "text_length",
    "html_length",
    "contains_primera_federacion",
    "contains_grupo_2",
    "contains_jornada",
    "contains_resultados",
    "contains_calendario",
    "contains_score_sequence",
    "candidate_sequence_count",
    "first_100_lines",
    "first_html_fragment",
    "notes",
]

route_matrix_rows = []

grupo_2_test_config = {
    "cod_temporada": "21",
    "cod_competicion": "23289295",
    "cod_grupo": "23289297",
    "cod_jornada": "1",
}

route_matrix_hosts = [
    "https://resultados.rfef.es",
    "https://marcadores.rfef.es",
]

route_matrix_routes = [
    {
        "route_name": "NFG_CmpJornada",
        "path": "/pnfg/NPcd/NFG_CmpJornada",
    },
    {
        "route_name": "NFG_VisCalendario_Vis",
        "path": "/pnfg/NPcd/NFG_VisCalendario_Vis",
    },
    {
        "route_name": "NFG_VisCalendario",
        "path": "/pnfg/NPcd/NFG_VisCalendario",
    },
    {
        "route_name": "NFG_CmpCalendario",
        "path": "/pnfg/NPcd/NFG_CmpCalendario",
    },
    {
        "route_name": "NFG_CmpJornada_Vis",
        "path": "/pnfg/NPcd/NFG_CmpJornada_Vis",
    },
]

route_matrix_cod_primaria_values = [
    "1000120",
    "3001668",
]

route_matrix_parameter_styles = [
    {
        "parameter_style": "upper_camel",
        "params": {
            "CodTemporada": grupo_2_test_config["cod_temporada"],
            "CodJornada": grupo_2_test_config["cod_jornada"],
            "CodCompeticion": grupo_2_test_config["cod_competicion"],
            "CodGrupo": grupo_2_test_config["cod_grupo"],
        },
    },
    {
        "parameter_style": "lower_mixed",
        "params": {
            "codtemporada": grupo_2_test_config["cod_temporada"],
            "codJornada": grupo_2_test_config["cod_jornada"],
            "codcompeticion": grupo_2_test_config["cod_competicion"],
            "codgrupo": grupo_2_test_config["cod_grupo"],
        },
    },
    {
        "parameter_style": "lower_all",
        "params": {
            "codtemporada": grupo_2_test_config["cod_temporada"],
            "codjornada": grupo_2_test_config["cod_jornada"],
            "codcompeticion": grupo_2_test_config["cod_competicion"],
            "codgrupo": grupo_2_test_config["cod_grupo"],
        },
    },
]


def route_matrix_build_query(params):
    parts = []
    for key, value in params.items():
        parts.append(f"{key}={value}")
    return "&".join(parts)


def route_matrix_clean_lines(text):
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def route_matrix_is_date(value):
    return bool(re.match(r"^[0-9]{2}-[0-9]{2}-[0-9]{4}$", value.strip()))


def route_matrix_is_time(value):
    return bool(re.match(r"^[0-9]{1,2}:[0-9]{2}$", value.strip()))


def route_matrix_is_score_marker(value):
    value = value.strip()
    return bool(
        value == "-"
        or re.match(r"^[0-9]{1,2}\s*-\s*[0-9]{1,2}$", value)
        or re.match(r"^[0-9]{1,2}\s*-$", value)
        or re.match(r"^-\s*[0-9]{1,2}$", value)
    )


def route_matrix_count_candidate_sequences(lines):
    count = 0

    for i in range(len(lines)):
        if i + 5 < len(lines):
            score_marker = lines[i + 1]
            date_value = lines[i + 2]
            time_value = lines[i + 3]

            if (
                route_matrix_is_score_marker(score_marker)
                and route_matrix_is_date(date_value)
                and route_matrix_is_time(time_value)
            ):
                count += 1

    return count


try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for host in route_matrix_hosts:
            for route in route_matrix_routes:
                for cod_primaria in route_matrix_cod_primaria_values:
                    for style in route_matrix_parameter_styles:
                        params = {
                            "cod_primaria": cod_primaria,
                            **style["params"],
                        }

                        query = route_matrix_build_query(params)
                        test_url = f"{host}{route['path']}?{query}"

                        test_name = (
                            f"Grupo 2 J1 | {host} | {route['route_name']} | "
                            f"cod_primaria={cod_primaria} | {style['parameter_style']}"
                        )

                        try:
                            page = browser.new_page(
                                user_agent=(
                                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                                    "Chrome/120.0.0.0 Safari/537.36"
                                )
                            )

                            # Establish session first.
                            page.goto(
                                "https://marcadores.rfef.es/pnfg/?accion=1",
                                wait_until="networkidle",
                                timeout=60000,
                            )

                            for selector in [
                                "text=Aceptar",
                                "text=ACEPTAR",
                                "text=Accept",
                                "button:has-text('Aceptar')",
                                "button:has-text('ACEPTAR')",
                            ]:
                                try:
                                    if page.locator(selector).count() > 0:
                                        page.locator(selector).first.click(timeout=3000)
                                        page.wait_for_timeout(1000)
                                        break
                                except Exception:
                                    pass

                            response = page.goto(
                                test_url,
                                wait_until="networkidle",
                                timeout=60000,
                            )

                            status = response.status if response else ""

                            # Give JavaScript a moment to populate if it is going to.
                            page.wait_for_timeout(3000)

                            page_text = page.inner_text("body")
                            page_html = page.content()

                            text_lower = page_text.lower()
                            html_lower = page_html.lower()

                            lines = route_matrix_clean_lines(page_text)
                            candidate_sequence_count = route_matrix_count_candidate_sequences(lines)

                            contains_score_sequence = bool(
                                candidate_sequence_count > 0
                                or re.search(
                                    r"[0-9]{2}-[0-9]{2}-[0-9]{4}.*?[0-9]{1,2}:[0-9]{2}",
                                    page_text,
                                    re.DOTALL,
                                )
                            )

                            safe_name = re.sub(
                                r"[^A-Za-z0-9]+",
                                "_",
                                test_name,
                            ).strip("_").lower()[:150]

                            # Only save HTML/text for promising or odd responses, to keep artifacts manageable.
                            if (
                                len(page_text) > 0
                                or candidate_sequence_count > 0
                                or "primera" in html_lower
                                or "jornada" in html_lower
                                or "resultado" in html_lower
                            ):
                                (EXPORT_DIR / f"primerafed_route_matrix_{safe_name}_text.txt").write_text(
                                    page_text[:300000],
                                    encoding="utf-8",
                                )

                                (EXPORT_DIR / f"primerafed_route_matrix_{safe_name}.html").write_text(
                                    page_html[:500000],
                                    encoding="utf-8",
                                )

                            first_100_lines = " | ".join(lines[:100])
                            first_html_fragment = re.sub(r"\s+", " ", page_html[:5000]).strip()

                            route_matrix_rows.append({
                                "test_name": test_name,
                                "host": host,
                                "route_name": route["route_name"],
                                "cod_primaria": cod_primaria,
                                "parameter_style": style["parameter_style"],
                                "cod_temporada": grupo_2_test_config["cod_temporada"],
                                "cod_competicion": grupo_2_test_config["cod_competicion"],
                                "cod_grupo": grupo_2_test_config["cod_grupo"],
                                "cod_jornada": grupo_2_test_config["cod_jornada"],
                                "test_url": test_url,
                                "http_status": str(status),
                                "page_loaded": "true",
                                "text_length": str(len(page_text)),
                                "html_length": str(len(page_html)),
                                "contains_primera_federacion": str(
                                    "primera federación" in text_lower
                                    or "primera federacion" in text_lower
                                    or "primera federaci" in text_lower
                                    or "primera federación" in html_lower
                                    or "primera federacion" in html_lower
                                    or "primera federaci" in html_lower
                                ).lower(),
                                "contains_grupo_2": str(
                                    "grupo 2" in text_lower
                                    or "grupo ii" in text_lower
                                    or "grupo 2" in html_lower
                                    or "grupo ii" in html_lower
                                ).lower(),
                                "contains_jornada": str(
                                    "jornada" in text_lower
                                    or "jornada" in html_lower
                                ).lower(),
                                "contains_resultados": str(
                                    "resultado" in text_lower
                                    or "resultados" in text_lower
                                    or "resultado" in html_lower
                                    or "resultados" in html_lower
                                ).lower(),
                                "contains_calendario": str(
                                    "calendario" in text_lower
                                    or "calendario" in html_lower
                                ).lower(),
                                "contains_score_sequence": str(contains_score_sequence).lower(),
                                "candidate_sequence_count": str(candidate_sequence_count),
                                "first_100_lines": first_100_lines[:6000],
                                "first_html_fragment": first_html_fragment[:6000],
                                "notes": "Grupo 2 route/parameter matrix test.",
                            })

                            page.close()

                        except Exception as e:
                            route_matrix_rows.append({
                                "test_name": test_name,
                                "host": host,
                                "route_name": route["route_name"],
                                "cod_primaria": cod_primaria,
                                "parameter_style": style["parameter_style"],
                                "cod_temporada": grupo_2_test_config["cod_temporada"],
                                "cod_competicion": grupo_2_test_config["cod_competicion"],
                                "cod_grupo": grupo_2_test_config["cod_grupo"],
                                "cod_jornada": grupo_2_test_config["cod_jornada"],
                                "test_url": test_url,
                                "http_status": "",
                                "page_loaded": "false",
                                "text_length": "0",
                                "html_length": "0",
                                "contains_primera_federacion": "false",
                                "contains_grupo_2": "false",
                                "contains_jornada": "false",
                                "contains_resultados": "false",
                                "contains_calendario": "false",
                                "contains_score_sequence": "false",
                                "candidate_sequence_count": "0",
                                "first_100_lines": "",
                                "first_html_fragment": "",
                                "notes": f"Route matrix test failed: {type(e).__name__}: {e}",
                            })

        browser.close()

except Exception as e:
    route_matrix_rows.append({
        "test_name": "stage_error",
        "host": "",
        "route_name": "",
        "cod_primaria": "",
        "parameter_style": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "test_url": "",
        "http_status": "",
        "page_loaded": "false",
        "text_length": "0",
        "html_length": "0",
        "contains_primera_federacion": "false",
        "contains_grupo_2": "false",
        "contains_jornada": "false",
        "contains_resultados": "false",
        "contains_calendario": "false",
        "contains_score_sequence": "false",
        "candidate_sequence_count": "0",
        "first_100_lines": "",
        "first_html_fragment": "",
        "notes": f"Grupo 2 route matrix stage failed: {type(e).__name__}: {e}",
    })

write_csv(
    "primerafed_2025_26_grupo2_route_matrix.csv",
    route_matrix_fields,
    route_matrix_rows,
)

# Root-level copy for easy artifact access.
root_route_matrix_path = Path("primerafed_2025_26_grupo2_route_matrix.csv")

with root_route_matrix_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=route_matrix_fields)
    writer.writeheader()
    writer.writerows(route_matrix_rows)

print(f"Created Grupo 2 route matrix: {len(route_matrix_rows)} tests.")
# -----------------------------
# Calendar-view availability audit:
# Test missing Grupo 1 J30-38 and Grupo 2 J1-38 via marcadores calendar route
# -----------------------------

calendar_missing_fields = [
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "calendar_url",
    "page_loaded",
    "text_length",
    "html_length",
    "contains_primera_federacion",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_jornada",
    "contains_resultados",
    "contains_calendario",
    "contains_score_marker",
    "contains_date",
    "contains_time",
    "first_120_lines",
    "first_html_fragment",
    "notes",
]

calendar_missing_rows = []

calendar_missing_tests = []

# Missing Grupo 1 fixtures: Jornadas 30-38
for jornada in range(30, 39):
    calendar_missing_tests.append({
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": str(jornada),
    })

# Missing Grupo 2 fixtures: Jornadas 1-38
for jornada in range(1, 39):
    calendar_missing_tests.append({
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": str(jornada),
    })


def calendar_missing_clean_lines(text):
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # Establish one session first.
        session_page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        session_page.goto(
            "https://marcadores.rfef.es/pnfg/?accion=1",
            wait_until="networkidle",
            timeout=60000,
        )

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

        session_page.close()

        for test in calendar_missing_tests:
            calendar_url = (
                "https://marcadores.rfef.es/pnfg/NPcd/NFG_VisCalendario_Vis"
                "?cod_primaria=1000120"
                f"&codtemporada={test['cod_temporada']}"
                f"&codjornada={test['cod_jornada']}"
                f"&codcompeticion={test['cod_competicion']}"
                f"&codgrupo={test['cod_grupo']}"
            )

            try:
                page = browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )

                response = page.goto(calendar_url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)

                page_text = page.inner_text("body")
                page_html = page.content()

                text_lower = page_text.lower()
                html_lower = page_html.lower()

                lines = calendar_missing_clean_lines(page_text)
                first_120_lines = " | ".join(lines[:120])
                first_html_fragment = re.sub(r"\s+", " ", page_html[:6000]).strip()

                contains_score_marker = bool(
                    re.search(r"\b[0-9]{1,2}\s*-\s*[0-9]{1,2}\b", page_text)
                    or re.search(r"\n\s*-\s*\n", page_text)
                )

                contains_date = bool(
                    re.search(r"\b[0-9]{2}-[0-9]{2}-[0-9]{4}\b", page_text)
                    or re.search(r"\b[0-9]{2}/[0-9]{2}/[0-9]{4}\b", page_text)
                )

                contains_time = bool(
                    re.search(r"\b[0-9]{1,2}:[0-9]{2}\b", page_text)
                )

                safe_name = re.sub(
                    r"[^A-Za-z0-9]+",
                    "_",
                    f"{test['competition_group']}_calendar_jornada_{test['cod_jornada']}",
                ).strip("_").lower()

                # Save all tested calendar pages for inspection.
                (EXPORT_DIR / f"primerafed_calendar_missing_{safe_name}_text.txt").write_text(
                    page_text[:500000],
                    encoding="utf-8",
                )

                (EXPORT_DIR / f"primerafed_calendar_missing_{safe_name}.html").write_text(
                    page_html[:800000],
                    encoding="utf-8",
                )

                calendar_missing_rows.append({
                    "competition_group": test["competition_group"],
                    "cod_temporada": test["cod_temporada"],
                    "cod_competicion": test["cod_competicion"],
                    "cod_grupo": test["cod_grupo"],
                    "cod_jornada": test["cod_jornada"],
                    "calendar_url": calendar_url,
                    "page_loaded": "true",
                    "text_length": str(len(page_text)),
                    "html_length": str(len(page_html)),
                    "contains_primera_federacion": str(
                        "primera federación" in text_lower
                        or "primera federacion" in text_lower
                        or "primera federaci" in text_lower
                        or "primera federación" in html_lower
                        or "primera federacion" in html_lower
                        or "primera federaci" in html_lower
                    ).lower(),
                    "contains_grupo_1": str(
                        "grupo 1" in text_lower
                        or "grupo i" in text_lower
                        or "grupo 1" in html_lower
                        or "grupo i" in html_lower
                    ).lower(),
                    "contains_grupo_2": str(
                        "grupo 2" in text_lower
                        or "grupo ii" in text_lower
                        or "grupo 2" in html_lower
                        or "grupo ii" in html_lower
                    ).lower(),
                    "contains_jornada": str(
                        "jornada" in text_lower
                        or "jornada" in html_lower
                    ).lower(),
                    "contains_resultados": str(
                        "resultado" in text_lower
                        or "resultados" in text_lower
                        or "resultado" in html_lower
                        or "resultados" in html_lower
                    ).lower(),
                    "contains_calendario": str(
                        "calendario" in text_lower
                        or "calendario" in html_lower
                    ).lower(),
                    "contains_score_marker": str(contains_score_marker).lower(),
                    "contains_date": str(contains_date).lower(),
                    "contains_time": str(contains_time).lower(),
                    "first_120_lines": first_120_lines[:8000],
                    "first_html_fragment": first_html_fragment[:8000],
                    "notes": "Calendar-view test for missing Primera Federación fixtures.",
                })

                page.close()

            except Exception as e:
                calendar_missing_rows.append({
                    "competition_group": test["competition_group"],
                    "cod_temporada": test["cod_temporada"],
                    "cod_competicion": test["cod_competicion"],
                    "cod_grupo": test["cod_grupo"],
                    "cod_jornada": test["cod_jornada"],
                    "calendar_url": calendar_url,
                    "page_loaded": "false",
                    "text_length": "0",
                    "html_length": "0",
                    "contains_primera_federacion": "false",
                    "contains_grupo_1": "false",
                    "contains_grupo_2": "false",
                    "contains_jornada": "false",
                    "contains_resultados": "false",
                    "contains_calendario": "false",
                    "contains_score_marker": "false",
                    "contains_date": "false",
                    "contains_time": "false",
                    "first_120_lines": "",
                    "first_html_fragment": "",
                    "notes": f"Calendar-view missing fixture test failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    calendar_missing_rows.append({
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "calendar_url": "",
        "page_loaded": "false",
        "text_length": "0",
        "html_length": "0",
        "contains_primera_federacion": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_jornada": "false",
        "contains_resultados": "false",
        "contains_calendario": "false",
        "contains_score_marker": "false",
        "contains_date": "false",
        "contains_time": "false",
        "first_120_lines": "",
        "first_html_fragment": "",
        "notes": f"Calendar-view missing fixture stage failed: {type(e).__name__}: {e}",
    })

write_csv(
    "primerafed_2025_26_missing_fixtures_calendar_audit.csv",
    calendar_missing_fields,
    calendar_missing_rows,
)

# Root-level copy for easy artifact access.
root_calendar_missing_path = Path("primerafed_2025_26_missing_fixtures_calendar_audit.csv")

with root_calendar_missing_path.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=calendar_missing_fields)
    writer.writeheader()
    writer.writerows(calendar_missing_rows)

print(f"Created missing fixtures calendar audit: {len(calendar_missing_rows)} tests.")
# Grupo 1 calendar parser:
# Recover missing Grupo 1 Jornadas 30-36 from marcadores calendar-view text
# -----------------------------

grupo1_calendar_fields = raw_fields
grupo1_calendar_rows = []

grupo1_known_teams = sorted(set(
    [row.get("home_team_name_source", "") for row in fixture_rows if row.get("competition_group") == "Grupo 1"]
    + [row.get("away_team_name_source", "") for row in fixture_rows if row.get("competition_group") == "Grupo 1"]
))

grupo1_known_teams = [
    team for team in grupo1_known_teams
    if team
]

# Longest first helps avoid partial matches where one club name contains another.
grupo1_known_teams = sorted(grupo1_known_teams, key=len, reverse=True)


def parse_calendar_score_middle(middle_text):
    """
    Calendar-view rows often look like:
    Home Team Away Team
    Home Team 1 0 Away Team
    Home Team 1 Away Team

    Only treat two numbers as a reliable completed score.
    A single number is ambiguous in this calendar layout, so leave score blank.
    """
    middle_text = re.sub(r"\s+", " ", middle_text).strip()

    if not middle_text:
        return "", ""

    two_score = re.match(r"^([0-9]{1,2})\s+([0-9]{1,2})$", middle_text)
    if two_score:
        return two_score.group(1), two_score.group(2)

    return "", ""


def parse_calendar_match_line(line, known_teams):
    cleaned = re.sub(r"\s+", " ", line).strip()

    for home_team in known_teams:
        if not cleaned.startswith(home_team + " "):
            continue

        remainder = cleaned[len(home_team):].strip()

        for away_team in known_teams:
            if away_team == home_team:
                continue

            if remainder == away_team:
                return home_team, away_team, "", ""

            if remainder.endswith(" " + away_team):
                middle = remainder[: -len(away_team)].strip()
                home_score, away_score = parse_calendar_score_middle(middle)
                return home_team, away_team, home_score, away_score

    return "", "", "", ""


def extract_calendar_jornada_block(lines, jornada_number):
    """
    Extract the lines between 'Jornada X (DD-MM-YYYY)' and the next Jornada header.
    """
    start_index = None
    fixture_date = ""

    jornada_pattern = re.compile(rf"^Jornada\s+{jornada_number}\s+\(([0-9]{{2}}-[0-9]{{2}}-[0-9]{{4}})\)$", re.IGNORECASE)

    for index, line in enumerate(lines):
        match = jornada_pattern.match(line)
        if match:
            start_index = index + 1
            fixture_date = normalise_date(match.group(1))
            break

    if start_index is None:
        return "", []

    end_index = len(lines)

    for index in range(start_index, len(lines)):
        if re.match(r"^Jornada\s+[0-9]+\s+\([0-9]{2}-[0-9]{2}-[0-9]{4}\)$", lines[index], re.IGNORECASE):
            end_index = index
            break

    return fixture_date, lines[start_index:end_index]


def clean_calendar_lines(text):
    lines = []

    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()

        if not cleaned:
            continue

        if cleaned in {
            "Competiciones",
            "Acciones",
            "Ver Clasificación Tabla Goleadores Tabla Porteros Ver Tabla Cruzada Versión Extendida",
            "Primera Vuelta",
            "Segunda Vuelta",
        }:
            continue

        if cleaned.startswith("Campeonato Nacional de Liga de Primera Federación"):
            continue

        if cleaned.startswith("Temporada "):
            continue

        if "Búsqueda por competición" in cleaned:
            continue

        lines.append(cleaned)

    return lines


try:
    grupo1_calendar_group = {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_level": "3",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
    }

    existing_fixture_ids = set(
        row.get("fixture_id", "")
        for row in fixture_rows
        if row.get("fixture_id")
    )

    for jornada in range(30, 37):
        matchday = str(jornada)

        safe_name = re.sub(
            r"[^A-Za-z0-9]+",
            "_",
            f"Grupo 1_calendar_jornada_{matchday}",
        ).strip("_").lower()

        text_path = EXPORT_DIR / f"primerafed_calendar_missing_{safe_name}_text.txt"

        source_url = (
            "https://marcadores.rfef.es/pnfg/NPcd/NFG_VisCalendario_Vis"
            "?cod_primaria=1000120"
            f"&codtemporada={grupo1_calendar_group['cod_temporada']}"
            f"&codjornada={matchday}"
            f"&codcompeticion={grupo1_calendar_group['cod_competicion']}"
            f"&codgrupo={grupo1_calendar_group['cod_grupo']}"
        )

        if not text_path.exists():
            grupo1_calendar_rows.append({
                "season_id": grupo1_calendar_group["season_id"],
                "competition_id": grupo1_calendar_group["competition_id"],
                "competition_name": grupo1_calendar_group["competition_name"],
                "competition_group": grupo1_calendar_group["competition_group"],
                "cod_temporada": grupo1_calendar_group["cod_temporada"],
                "cod_competicion": grupo1_calendar_group["cod_competicion"],
                "cod_grupo": grupo1_calendar_group["cod_grupo"],
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
                "notes": f"Expected calendar text file missing: {text_path.name}",
            })
            continue

        calendar_text = text_path.read_text(encoding="utf-8", errors="ignore")
        calendar_lines = clean_calendar_lines(calendar_text)

        fixture_date, jornada_lines = extract_calendar_jornada_block(calendar_lines, matchday)

        fixture_index = 0

        for line in jornada_lines:
            home_team, away_team, home_score, away_score = parse_calendar_match_line(line, grupo1_known_teams)

            if not home_team or not away_team:
                continue

            raw_row = {
                "season_id": grupo1_calendar_group["season_id"],
                "competition_id": grupo1_calendar_group["competition_id"],
                "competition_name": grupo1_calendar_group["competition_name"],
                "competition_group": grupo1_calendar_group["competition_group"],
                "cod_temporada": grupo1_calendar_group["cod_temporada"],
                "cod_competicion": grupo1_calendar_group["cod_competicion"],
                "cod_grupo": grupo1_calendar_group["cod_grupo"],
                "cod_jornada": matchday,
                "fixture_index": str(fixture_index),
                "source_url": source_url,
                "home_team_name_source": home_team,
                "away_team_name_source": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "fixture_date": fixture_date,
                "kickoff_time_local": "",
                "venue_name_source": "",
                "referee": "",
                "raw_sequence": line,
                "data_confidence": "high" if fixture_date else "needs_review",
                "notes": "Recovered from RFEF marcadores calendar-view layout.",
            }

            grupo1_calendar_rows.append(raw_row)

            home_team_id = make_team_id(home_team)
            away_team_id = make_team_id(away_team)

            fixture_id = make_fixture_id(
                grupo1_calendar_group["season_id"],
                grupo1_calendar_group["competition_id"],
                grupo1_calendar_group["competition_group"],
                matchday,
                home_team_id,
                away_team_id,
            )

            if fixture_id not in existing_fixture_ids:
                result_status = "played" if home_score != "" and away_score != "" else "scheduled"

                fixture_rows.append({
                    "fixture_id": fixture_id,
                    "season_id": grupo1_calendar_group["season_id"],
                    "competition_id": grupo1_calendar_group["competition_id"],
                    "competition_name": grupo1_calendar_group["competition_name"],
                    "competition_level": grupo1_calendar_group["competition_level"],
                    "competition_group": grupo1_calendar_group["competition_group"],
                    "fixture_phase": "regular_season",
                    "matchday": matchday,
                    "round_label": f"Jornada {matchday}",
                    "fixture_date": fixture_date,
                    "kickoff_time_local": "",
                    "home_team_id": home_team_id,
                    "home_team_name_source": home_team,
                    "away_team_id": away_team_id,
                    "away_team_name_source": away_team,
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
                    "source_url": source_url,
                    "source_retrieved_at": NOW,
                    "data_confidence": raw_row["data_confidence"],
                    "notes": "Recovered from RFEF marcadores calendar-view layout.",
                })

                team_index_rows.append({
                    "team_fixture_id": f"{fixture_id}__{home_team_id}",
                    "fixture_id": fixture_id,
                    "team_id": home_team_id,
                    "season_id": grupo1_calendar_group["season_id"],
                    "competition_id": grupo1_calendar_group["competition_id"],
                    "competition_name": grupo1_calendar_group["competition_name"],
                    "competition_group": grupo1_calendar_group["competition_group"],
                    "fixture_phase": "regular_season",
                    "matchday": matchday,
                    "fixture_date": fixture_date,
                    "opponent_team_id": away_team_id,
                    "home_or_away": "Home",
                    "team_score": home_score,
                    "opponent_score": away_score,
                    "result_for_team": result_for_team(home_score, away_score),
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

                team_index_rows.append({
                    "team_fixture_id": f"{fixture_id}__{away_team_id}",
                    "fixture_id": fixture_id,
                    "team_id": away_team_id,
                    "season_id": grupo1_calendar_group["season_id"],
                    "competition_id": grupo1_calendar_group["competition_id"],
                    "competition_name": grupo1_calendar_group["competition_name"],
                    "competition_group": grupo1_calendar_group["competition_group"],
                    "fixture_phase": "regular_season",
                    "matchday": matchday,
                    "fixture_date": fixture_date,
                    "opponent_team_id": home_team_id,
                    "home_or_away": "Away",
                    "team_score": away_score,
                    "opponent_score": home_score,
                    "result_for_team": result_for_team(away_score, home_score),
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

                existing_fixture_ids.add(fixture_id)

            fixture_index += 1

except Exception as e:
    grupo1_calendar_rows.append({
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
        "notes": f"Grupo 1 calendar parser failed: {type(e).__name__}: {e}",
    })


write_csv(
    "primerafed_2025_26_grupo1_calendar_recovered_raw.csv",
    grupo1_calendar_fields,
    grupo1_calendar_rows,
)

write_csv(
    "primerafed_2025_26_fixtures_results_rfeffed_enhanced.csv",
    fixture_fields,
    fixture_rows,
)

write_csv(
    "primerafed_2025_26_team_fixture_index_rfeffed_enhanced.csv",
    team_index_fields,
    team_index_rows,
)


# Enhanced validation after Grupo 1 calendar recovery
enhanced_validation_fields = [
    "check_name",
    "result",
    "details",
]

enhanced_grupo_1_rows = [
    row for row in fixture_rows
    if row.get("competition_group") == "Grupo 1"
]

enhanced_grupo_2_rows = [
    row for row in fixture_rows
    if row.get("competition_group") == "Grupo 2"
]

calendar_recovered_non_failed = [
    row for row in grupo1_calendar_rows
    if row.get("data_confidence") != "failed"
]

calendar_counts = {}

for row in calendar_recovered_non_failed:
    key = f"J{row.get('cod_jornada')}"
    calendar_counts[key] = calendar_counts.get(key, 0) + 1

unexpected_calendar_counts = [
    f"{key}={count}"
    for key, count in sorted(calendar_counts.items())
    if count != 10
]

enhanced_fixture_ids = [
    row.get("fixture_id", "")
    for row in fixture_rows
    if row.get("fixture_id")
]

enhanced_duplicate_fixture_ids = sorted([
    fixture_id for fixture_id in set(enhanced_fixture_ids)
    if enhanced_fixture_ids.count(fixture_id) > 1
])

enhanced_validation_rows = [
    {
        "check_name": "calendar_recovered_non_failed_rows",
        "result": str(len(calendar_recovered_non_failed)),
        "details": "Expected 70 if Grupo 1 Jornadas 30-36 all parse.",
    },
    {
        "check_name": "enhanced_fixture_rows",
        "result": str(len(fixture_rows)),
        "details": "Expected 360 if 290 existing + 70 recovered.",
    },
    {
        "check_name": "enhanced_grupo_1_fixture_rows",
        "result": str(len(enhanced_grupo_1_rows)),
        "details": "Expected 360 if Grupo 1 J1-36 complete.",
    },
    {
        "check_name": "enhanced_grupo_2_fixture_rows",
        "result": str(len(enhanced_grupo_2_rows)),
        "details": "Expected 0 until Grupo 2 calendar parser is added.",
    },
    {
        "check_name": "calendar_unexpected_jornada_counts",
        "result": str(len(unexpected_calendar_counts)),
        "details": "|".join(unexpected_calendar_counts),
    },
    {
        "check_name": "enhanced_duplicate_fixture_ids",
        "result": str(len(enhanced_duplicate_fixture_ids)),
        "details": "|".join(enhanced_duplicate_fixture_ids),
    },
]

write_csv(
    "primerafed_2025_26_grupo1_calendar_recovery_validation.csv",
    enhanced_validation_fields,
    enhanced_validation_rows,
)

# Root-level copies for easy artifact access.
for filename in [
    "primerafed_2025_26_grupo1_calendar_recovered_raw.csv",
    "primerafed_2025_26_fixtures_results_rfeffed_enhanced.csv",
    "primerafed_2025_26_team_fixture_index_rfeffed_enhanced.csv",
    "primerafed_2025_26_grupo1_calendar_recovery_validation.csv",
]:
    src = EXPORT_DIR / filename
    dst = Path(filename)

    if src.exists():
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

print("Created Grupo 1 calendar recovery outputs.")

Then run the workflow and upload:

primerafed_2025_26_grupo1_calendar_recovery_validation.csv
primerafed_2025_26_grupo1_calendar_recovered_raw.csv

What we want is:

calendar_recovered_non_failed_rows = 70
enhanced_fixture_rows = 360
enhanced_grupo_1_fixture_rows = 360
calendar_unexpected_jornada_counts = 0

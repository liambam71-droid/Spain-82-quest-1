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

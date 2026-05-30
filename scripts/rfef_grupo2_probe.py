from pathlib import Path
import csv
import re
from datetime import datetime, timezone

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

    # Root-level copy for easy artifact access.
    root_path = Path(filename)
    with root_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path} and root copy {root_path}")


summary_fields = [
    "test_name",
    "url",
    "page_loaded",
    "http_status",
    "text_length",
    "html_length",
    "line_count",
    "contains_primera_federacion",
    "contains_grupo_2",
    "contains_jornada",
    "contains_calendario",
    "contains_resultados",
    "contains_dates",
    "contains_times",
    "first_300_lines",
    "first_html_fragment",
    "notes",
]

line_fields = [
    "line_index",
    "line_text",
    "is_jornada_header",
    "contains_date",
    "contains_time",
    "contains_digit",
    "possible_fixture_line",
]

summary_rows = []
line_rows = []

grupo2_url = (
    "https://marcadores.rfef.es/pnfg/NPcd/NFG_VisCalendario_Vis"
    "?cod_primaria=1000120"
    "&codtemporada=21"
    "&codjornada=1"
    "&codcompeticion=23289295"
    "&codgrupo=23289297"
)

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        # Establish session on marcadores first.
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
                    page.wait_for_timeout(1500)
                    break
            except Exception:
                pass

        response = page.goto(
            grupo2_url,
            wait_until="networkidle",
            timeout=60000,
        )

        page.wait_for_timeout(6000)

        status = response.status if response else ""

        page_text = page.inner_text("body")
        page_html = page.content()

        (EXPORT_DIR / "grupo2_probe_page_text.txt").write_text(
            page_text[:800000],
            encoding="utf-8",
        )

        (EXPORT_DIR / "grupo2_probe_page_html.html").write_text(
            page_html[:1200000],
            encoding="utf-8",
        )

        text_lower = page_text.lower()
        html_lower = page_html.lower()

        lines = [
            re.sub(r"\s+", " ", line).strip()
            for line in page_text.splitlines()
            if re.sub(r"\s+", " ", line).strip()
        ]

        for index, line in enumerate(lines):
            lower = line.lower()

            is_jornada_header = bool(
                re.match(r"^jornada\s+[0-9]+\s+\([0-9]{2}-[0-9]{2}-[0-9]{4}\)$", line, re.IGNORECASE)
            )

            contains_date = bool(
                re.search(r"[0-9]{2}-[0-9]{2}-[0-9]{4}", line)
                or re.search(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", line)
            )

            contains_time = bool(re.search(r"\b[0-9]{1,2}:[0-9]{2}\b", line))
            contains_digit = bool(re.search(r"[0-9]", line))

            possible_fixture_line = bool(
                not is_jornada_header
                and not contains_time
                and len(line) >= 10
                and "jornada" not in lower
                and "temporada" not in lower
                and "clasificación" not in lower
                and "clasificacion" not in lower
                and "calendario" not in lower
                and "competiciones" not in lower
                and "acciones" not in lower
            )

            line_rows.append({
                "line_index": str(index),
                "line_text": line[:2000],
                "is_jornada_header": str(is_jornada_header).lower(),
                "contains_date": str(contains_date).lower(),
                "contains_time": str(contains_time).lower(),
                "contains_digit": str(contains_digit).lower(),
                "possible_fixture_line": str(possible_fixture_line).lower(),
            })

        summary_rows.append({
            "test_name": "Grupo 2 exact successful-route probe",
            "url": grupo2_url,
            "page_loaded": "true",
            "http_status": str(status),
            "text_length": str(len(page_text)),
            "html_length": str(len(page_html)),
            "line_count": str(len(lines)),
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
            "contains_jornada": str("jornada" in text_lower or "jornada" in html_lower).lower(),
            "contains_calendario": str("calendario" in text_lower or "calendario" in html_lower).lower(),
            "contains_resultados": str(
                "resultado" in text_lower
                or "resultados" in text_lower
                or "resultado" in html_lower
                or "resultados" in html_lower
            ).lower(),
            "contains_dates": str(any(row["contains_date"] == "true" for row in line_rows)).lower(),
            "contains_times": str(any(row["contains_time"] == "true" for row in line_rows)).lower(),
            "first_300_lines": " | ".join(lines[:300])[:20000],
            "first_html_fragment": re.sub(r"\s+", " ", page_html[:10000]).strip(),
            "notes": f"Generated at {NOW}. Small focused Grupo 2 probe.",
        })

        browser.close()

except Exception as e:
    summary_rows.append({
        "test_name": "Grupo 2 exact successful-route probe",
        "url": grupo2_url,
        "page_loaded": "false",
        "http_status": "",
        "text_length": "0",
        "html_length": "0",
        "line_count": "0",
        "contains_primera_federacion": "false",
        "contains_grupo_2": "false",
        "contains_jornada": "false",
        "contains_calendario": "false",
        "contains_resultados": "false",
        "contains_dates": "false",
        "contains_times": "false",
        "first_300_lines": "",
        "first_html_fragment": "",
        "notes": f"Probe failed: {type(e).__name__}: {e}",
    })

write_csv(
    "grupo2_probe_summary.csv",
    summary_fields,
    summary_rows,
)

write_csv(
    "grupo2_probe_lines.csv",
    line_fields,
    line_rows,
)

print("Grupo 2 probe complete.")
# -----------------------------
# Parse Grupo 2 probe lines into structured fixture rows
# -----------------------------

grupo2_parse_fields = [
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "matchday",
    "fixture_date",
    "fixture_index",
    "home_team_name_source",
    "away_team_name_source",
    "home_score",
    "away_score",
    "raw_line",
    "data_confidence",
    "notes",
]

grupo2_parse_rows = []

grupo2_validation_fields = [
    "check_name",
    "result",
    "details",
]

GRUPO2_TEAMS = [
    'AD Alcorcón',
    'Algeciras CF',
    'Antequera CF',
    'Atlético Madrileño',
    'Atlético Sanluqueño CF',
    'Betis Deportivo Balompié',
    'CD Eldense',
    'CD Teruel',
    'CE Europa',
    'CE Sabadell FC',
    'FC Cartagena',
    'Gimnàstic de Tarragona',
    'Hércules de Alicante CF',
    'Juventud de Torremolinos CF',
    'Marbella FC',
    'Real Murcia CF',
    'SD Tarazona',
    'Sevilla Atlético',
    'UD Ibiza',
    'Villarreal CF "B"',
]

GRUPO2_TEAMS = sorted(GRUPO2_TEAMS, key=len, reverse=True)


def probe_normalise_date(value):
    match = re.match(r"^([0-9]{2})-([0-9]{2})-([0-9]{4})$", value.strip())
    if not match:
        return value
    day, month, year = match.groups()
    return f"{year}-{month}-{day}"


def probe_parse_score_middle(middle_text):
    middle_text = re.sub(r"\s+", " ", middle_text).strip()

    if not middle_text:
        return "", ""

    # Two numbers is a reliable score, e.g. "0 2".
    two_score = re.match(r"^([0-9]{1,2})\s+([0-9]{1,2})$", middle_text)
    if two_score:
        return two_score.group(1), two_score.group(2)

    # Single numbers are ambiguous in the calendar layout, so do not treat them as final scores.
    return "", ""


def probe_parse_fixture_line(line, teams):
    cleaned = re.sub(r"\s+", " ", line).strip()

    for home_team in teams:
        if not cleaned.startswith(home_team + " "):
            continue

        remainder = cleaned[len(home_team):].strip()

        for away_team in teams:
            if away_team == home_team:
                continue

            if remainder == away_team:
                return home_team, away_team, "", ""

            if remainder.endswith(" " + away_team):
                middle = remainder[: -len(away_team)].strip()
                home_score, away_score = probe_parse_score_middle(middle)
                return home_team, away_team, home_score, away_score

    return "", "", "", ""


try:
    current_matchday = ""
    current_fixture_date = ""
    fixture_index_by_matchday = {}

    for row in line_rows:
        line = row.get("line_text", "").strip()

        jornada_match = re.match(
            r"^Jornada\s+([0-9]+)\s+\(([0-9]{2}-[0-9]{2}-[0-9]{4})\)$",
            line,
            re.IGNORECASE,
        )

        if jornada_match:
            current_matchday = jornada_match.group(1)
            current_fixture_date = probe_normalise_date(jornada_match.group(2))
            fixture_index_by_matchday[current_matchday] = 0
            continue

        if not current_matchday:
            continue

        if row.get("possible_fixture_line") != "true":
            continue

        home_team, away_team, home_score, away_score = probe_parse_fixture_line(line, GRUPO2_TEAMS)

        if not home_team or not away_team:
            continue

        fixture_index = fixture_index_by_matchday.get(current_matchday, 0)

        grupo2_parse_rows.append({
            "season_id": "2025-26",
            "competition_id": "PRIMERA_FEDERACION",
            "competition_name": "Primera Federación",
            "competition_group": "Grupo 2",
            "matchday": current_matchday,
            "fixture_date": current_fixture_date,
            "fixture_index": str(fixture_index),
            "home_team_name_source": home_team,
            "away_team_name_source": away_team,
            "home_score": home_score,
            "away_score": away_score,
            "raw_line": line,
            "data_confidence": "high" if current_fixture_date else "needs_review",
            "notes": "Parsed from Grupo 2 probe calendar-view line structure.",
        })

        fixture_index_by_matchday[current_matchday] = fixture_index + 1

except Exception as e:
    grupo2_parse_rows.append({
        "season_id": "",
        "competition_id": "",
        "competition_name": "",
        "competition_group": "",
        "matchday": "",
        "fixture_date": "",
        "fixture_index": "",
        "home_team_name_source": "",
        "away_team_name_source": "",
        "home_score": "",
        "away_score": "",
        "raw_line": "",
        "data_confidence": "failed",
        "notes": f"Grupo 2 probe parser failed: {type(e).__name__}: {e}",
    })


write_csv(
    "grupo2_probe_parsed_fixtures.csv",
    grupo2_parse_fields,
    grupo2_parse_rows,
)

counts_by_matchday = {}

for row in grupo2_parse_rows:
    matchday = row.get("matchday", "")
    if matchday:
        counts_by_matchday[matchday] = counts_by_matchday.get(matchday, 0) + 1

unexpected_counts = [
    f"J{matchday}={count}"
    for matchday, count in sorted(counts_by_matchday.items(), key=lambda item: int(item[0]))
    if count != 10
]

high_confidence_rows = [
    row for row in grupo2_parse_rows
    if row.get("data_confidence") == "high"
]

grupo2_validation_rows = [
    {
        "check_name": "grupo2_parsed_fixture_rows",
        "result": str(len(grupo2_parse_rows)),
        "details": "Expected 380.",
    },
    {
        "check_name": "grupo2_high_confidence_rows",
        "result": str(len(high_confidence_rows)),
        "details": "Expected 380.",
    },
    {
        "check_name": "matchdays_found",
        "result": str(len(counts_by_matchday)),
        "details": "Expected 38.",
    },
    {
        "check_name": "unexpected_matchday_counts",
        "result": str(len(unexpected_counts)),
        "details": "|".join(unexpected_counts),
    },
]

write_csv(
    "grupo2_probe_parse_validation.csv",
    grupo2_validation_fields,
    grupo2_validation_rows,
)

print(f"Parsed Grupo 2 probe fixtures: {len(grupo2_parse_rows)}")

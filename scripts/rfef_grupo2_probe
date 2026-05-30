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

from pathlib import Path
import csv
import re

EXPORT_DIR = Path("data/exports")
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def write_csv(filename, fieldnames, rows=None):
    rows = rows or []
    path = EXPORT_DIR / filename

    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Created {path}")


# -----------------------------
# RFEF browser-session test
# -----------------------------

fields = [
    "test_name",
    "test_url",
    "browser_started",
    "page_loaded",
    "cookie_message_present",
    "contains_primera_federacion",
    "contains_jornada",
    "contains_local",
    "contains_visitante",
    "contains_resultado",
    "sample_text",
    "notes",
]

rows = []

try:
    from playwright.sync_api import sync_playwright

    test_url = (
        "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
        "?cod_primaria=1000120"
        "&CodCompeticion=901769680"
        "&CodGrupo=901769681"
        "&CodTemporada=20"
        "&CodJornada=1"
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page.goto(test_url, wait_until="networkidle", timeout=60000)

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
                    page.wait_for_timeout(2000)
                    break
            except Exception:
                pass

        page_text = page.inner_text("body")
        page_html = page.content()
        browser.close()

    page_text_lower = page_text.lower()

    cookie_message_present = (
        "no se ha aceptado el cookie" in page_text_lower
        or "no se ha aceptado la cookie" in page_text_lower
    )

    sample_text = re.sub(r"\s+", " ", page_text[:2500]).strip()

    html_path = EXPORT_DIR / "rfef_browser_test_page.html"
    html_path.write_text(page_html[:100000], encoding="utf-8")

    rows.append({
        "test_name": "RFEF Jornada 1 browser session test",
        "test_url": test_url,
        "browser_started": "true",
        "page_loaded": "true",
        "cookie_message_present": str(cookie_message_present).lower(),
        "contains_primera_federacion": str("primera federación" in page_text_lower or "primera federacion" in page_text_lower).lower(),
        "contains_jornada": str("jornada" in page_text_lower).lower(),
        "contains_local": str("local" in page_text_lower).lower(),
        "contains_visitante": str("visitante" in page_text_lower).lower(),
        "contains_resultado": str("resultado" in page_text_lower or "resultados" in page_text_lower).lower(),
        "sample_text": sample_text,
        "notes": "Browser session completed. HTML sample saved.",
    })

except Exception as e:
    rows.append({
        "test_name": "RFEF Jornada 1 browser session test",
        "test_url": "",
        "browser_started": "false",
        "page_loaded": "false",
        "cookie_message_present": "",
        "contains_primera_federacion": "false",
        "contains_jornada": "false",
        "contains_local": "false",
        "contains_visitante": "false",
        "contains_resultado": "false",
        "sample_text": "",
        "notes": f"RFEF browser test failed: {type(e).__name__}: {e}",
    })

write_csv("rfef_browser_session_test.csv", fields, rows)

print("RFEF discovery runner complete.")

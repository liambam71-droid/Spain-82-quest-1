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
# -----------------------------
# RFEF Stage 2: discover hidden codes, dropdowns and links
# -----------------------------

from urllib.parse import urljoin

code_discovery_fields = [
    "item_type",
    "label_or_text",
    "name",
    "value",
    "href_or_action",
    "keyword_matches",
    "notes",
]

code_discovery_rows = []

keywords = [
    "primera",
    "federacion",
    "federación",
    "grupo",
    "jornada",
    "temporada",
    "competicion",
    "competición",
    "codcompeticion",
    "codtemporada",
    "codgrupo",
    "codjornada",
    "calendario",
    "resultados",
    "actas",
]

try:
    from playwright.sync_api import sync_playwright

    discovery_url = "https://marcadores.rfef.es/pnfg/?accion=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page.goto(discovery_url, wait_until="networkidle", timeout=60000)

        # Try common cookie accept buttons, if present.
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

        page_html = page.content()
        page_text = page.inner_text("body")

        html_path = EXPORT_DIR / "rfef_code_discovery_page.html"
        html_path.write_text(page_html[:300000], encoding="utf-8")

        # 1. Extract all dropdown options.
        options = page.locator("option")
        option_count = options.count()

        for i in range(option_count):
            try:
                option = options.nth(i)
                text = option.inner_text().strip()
                value = option.get_attribute("value") or ""
                parent_name = ""

                try:
                    parent_name = option.locator("xpath=..").get_attribute("name") or ""
                except Exception:
                    pass

                searchable = f"{text} {value} {parent_name}".lower()
                matched = [kw for kw in keywords if kw.lower() in searchable]

                if matched or text or value:
                    code_discovery_rows.append({
                        "item_type": "option",
                        "label_or_text": text,
                        "name": parent_name,
                        "value": value,
                        "href_or_action": "",
                        "keyword_matches": "|".join(matched),
                        "notes": "Dropdown option discovered.",
                    })
            except Exception:
                pass

        # 2. Extract all inputs, including hidden fields.
        inputs = page.locator("input")
        input_count = inputs.count()

        for i in range(input_count):
            try:
                input_el = inputs.nth(i)
                input_type = input_el.get_attribute("type") or ""
                input_name = input_el.get_attribute("name") or ""
                input_value = input_el.get_attribute("value") or ""

                searchable = f"{input_type} {input_name} {input_value}".lower()
                matched = [kw for kw in keywords if kw.lower() in searchable]

                if matched or input_name or input_value:
                    code_discovery_rows.append({
                        "item_type": f"input:{input_type}",
                        "label_or_text": "",
                        "name": input_name,
                        "value": input_value,
                        "href_or_action": "",
                        "keyword_matches": "|".join(matched),
                        "notes": "Input field discovered.",
                    })
            except Exception:
                pass

        # 3. Extract all links.
        links = page.locator("a")
        link_count = links.count()

        for i in range(link_count):
            try:
                link = links.nth(i)
                text = link.inner_text().strip()
                href = link.get_attribute("href") or ""
                full_href = urljoin(discovery_url, href)

                searchable = f"{text} {full_href}".lower()
                matched = [kw for kw in keywords if kw.lower() in searchable]

                if matched:
                    code_discovery_rows.append({
                        "item_type": "link",
                        "label_or_text": text,
                        "name": "",
                        "value": "",
                        "href_or_action": full_href,
                        "keyword_matches": "|".join(matched),
                        "notes": "Candidate link discovered.",
                    })
            except Exception:
                pass

        # 4. Extract form actions.
        forms = page.locator("form")
        form_count = forms.count()

        for i in range(form_count):
            try:
                form = forms.nth(i)
                action = form.get_attribute("action") or ""
                method = form.get_attribute("method") or ""
                name = form.get_attribute("name") or ""
                full_action = urljoin(discovery_url, action)

                searchable = f"{name} {method} {full_action}".lower()
                matched = [kw for kw in keywords if kw.lower() in searchable]

                code_discovery_rows.append({
                    "item_type": "form",
                    "label_or_text": "",
                    "name": name,
                    "value": method,
                    "href_or_action": full_action,
                    "keyword_matches": "|".join(matched),
                    "notes": "Form action discovered.",
                })
            except Exception:
                pass

        # 5. Regex scan of HTML for RFEF code-looking parameters.
        patterns = [
            r"CodCompeticion[=:'\"\s]+([0-9]+)",
            r"codcompeticion[=:'\"\s]+([0-9]+)",
            r"CodTemporada[=:'\"\s]+([0-9]+)",
            r"codtemporada[=:'\"\s]+([0-9]+)",
            r"CodGrupo[=:'\"\s]+([0-9]+)",
            r"codgrupo[=:'\"\s]+([0-9]+)",
            r"CodJornada[=:'\"\s]+([0-9]+)",
            r"codjornada[=:'\"\s]+([0-9]+)",
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, page_html, re.IGNORECASE):
                code_discovery_rows.append({
                    "item_type": "regex_code",
                    "label_or_text": pattern,
                    "name": "",
                    "value": match.group(1),
                    "href_or_action": "",
                    "keyword_matches": "code",
                    "notes": "Code-like value found by regex scan.",
                })

        browser.close()

except Exception as e:
    code_discovery_rows.append({
        "item_type": "error",
        "label_or_text": "",
        "name": "",
        "value": "",
        "href_or_action": "",
        "keyword_matches": "",
        "notes": f"RFEF code discovery failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_code_discovery_candidates.csv",
    code_discovery_fields,
    code_discovery_rows,
)

print(f"RFEF code discovery completed with {len(code_discovery_rows)} rows.")

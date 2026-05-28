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
# -----------------------------
# RFEF Stage 3: test discovered RFEF code sets
# -----------------------------

rfef_code_set_test_fields = [
    "code_set_name",
    "test_url",
    "http_status",
    "page_loaded",
    "contains_primera_federacion",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_jornada",
    "contains_local",
    "contains_visitante",
    "contains_resultado",
    "sample_text",
    "notes",
]

rfef_code_set_test_rows = []

rfef_code_sets_to_test = [
    {
        "code_set_name": "Discovered code set A",
        "cod_temporada": "21",
        "cod_competicion": "23289293",
        "cod_grupo": "23289294",
        "cod_jornada": "42",
    },
    {
        "code_set_name": "Discovered code set B",
        "cod_temporada": "21",
        "cod_competicion": "23289454",
        "cod_grupo": "23289455",
        "cod_jornada": "1",
    },
    {
        "code_set_name": "Discovered code set C",
        "cod_temporada": "21",
        "cod_competicion": "23289468",
        "cod_grupo": "23289469",
        "cod_jornada": "4",
    },
]

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for code_set in rfef_code_sets_to_test:
            test_url = (
                "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
                "?cod_primaria=1000120"
                f"&CodCompeticion={code_set['cod_competicion']}"
                f"&CodGrupo={code_set['cod_grupo']}"
                f"&CodTemporada={code_set['cod_temporada']}"
                f"&CodJornada={code_set['cod_jornada']}"
            )

            try:
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
                page_text_lower = page_text.lower()

                safe_name = re.sub(r"[^A-Za-z0-9]+", "_", code_set["code_set_name"]).strip("_").lower()
                html_path = EXPORT_DIR / f"rfef_stage_3_{safe_name}.html"
                html_path.write_text(page_html[:150000], encoding="utf-8")

                sample_text = re.sub(r"\s+", " ", page_text[:4000]).strip()

                rfef_code_set_test_rows.append({
                    "code_set_name": code_set["code_set_name"],
                    "test_url": test_url,
                    "http_status": "browser",
                    "page_loaded": "true",
                    "contains_primera_federacion": str("primera federación" in page_text_lower or "primera federacion" in page_text_lower).lower(),
                    "contains_grupo_1": str("grupo 1" in page_text_lower).lower(),
                    "contains_grupo_2": str("grupo 2" in page_text_lower).lower(),
                    "contains_jornada": str("jornada" in page_text_lower).lower(),
                    "contains_local": str("local" in page_text_lower).lower(),
                    "contains_visitante": str("visitante" in page_text_lower).lower(),
                    "contains_resultado": str("resultado" in page_text_lower or "resultados" in page_text_lower).lower(),
                    "sample_text": sample_text,
                    "notes": "Code set tested through Playwright browser session.",
                })

                page.close()

            except Exception as e:
                rfef_code_set_test_rows.append({
                    "code_set_name": code_set["code_set_name"],
                    "test_url": test_url,
                    "http_status": "",
                    "page_loaded": "false",
                    "contains_primera_federacion": "false",
                    "contains_grupo_1": "false",
                    "contains_grupo_2": "false",
                    "contains_jornada": "false",
                    "contains_local": "false",
                    "contains_visitante": "false",
                    "contains_resultado": "false",
                    "sample_text": "",
                    "notes": f"Code set test failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    rfef_code_set_test_rows.append({
        "code_set_name": "stage_error",
        "test_url": "",
        "http_status": "",
        "page_loaded": "false",
        "contains_primera_federacion": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_jornada": "false",
        "contains_local": "false",
        "contains_visitante": "false",
        "contains_resultado": "false",
        "sample_text": "",
        "notes": f"RFEF Stage 3 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_code_set_test_results.csv",
    rfef_code_set_test_fields,
    rfef_code_set_test_rows,
)

print(f"RFEF Stage 3 tested {len(rfef_code_set_test_rows)} code sets.")
# -----------------------------
# RFEF Stage 4: broader search for regular-season Primera Federación codes
# -----------------------------

rfef_regular_discovery_fields = [
    "item_type",
    "label_or_text",
    "href_or_action",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "keyword_matches",
    "regular_season_signal",
    "notes",
]

rfef_regular_discovery_rows = []

regular_keywords = [
    "primera federación",
    "primera federacion",
    "1ª federación",
    "1ª federacion",
    "primera federaci",
    "liga regular",
    "fase regular",
    "grupo 1",
    "grupo 2",
    "grupo primero",
    "grupo segundo",
    "jornada",
    "calendario",
    "clasificación",
    "clasificacion",
    "resultados",
]

code_patterns = {
    "cod_temporada": [
        r"CodTemporada=([0-9]+)",
        r"codtemporada=([0-9]+)",
        r"cod_temporada=([0-9]+)",
    ],
    "cod_competicion": [
        r"CodCompeticion=([0-9]+)",
        r"codcompeticion=([0-9]+)",
        r"codcompeticion%3D([0-9]+)",
    ],
    "cod_grupo": [
        r"CodGrupo=([0-9]+)",
        r"codgrupo=([0-9]+)",
        r"codgrupo%3D([0-9]+)",
    ],
    "cod_jornada": [
        r"CodJornada=([0-9]+)",
        r"codjornada=([0-9]+)",
        r"codjornada%3D([0-9]+)",
    ],
}


def extract_first_code(text, pattern_list):
    for pattern in pattern_list:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


try:
    from playwright.sync_api import sync_playwright

    discovery_pages = [
        {
            "name": "marcadores accion 1",
            "url": "https://marcadores.rfef.es/pnfg/?accion=1",
        },
        {
            "name": "resultados base",
            "url": "https://resultados.rfef.es/pnfg/NPcd/NFG_VisCompeticiones",
        },
        {
            "name": "actas base",
            "url": "https://resultados.rfef.es/pnfg/NPcd/NFG_VisActas",
        },
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for discovery_page in discovery_pages:
            page = browser.new_page(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            try:
                page.goto(discovery_page["url"], wait_until="networkidle", timeout=60000)

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

                safe_page_name = re.sub(r"[^A-Za-z0-9]+", "_", discovery_page["name"]).strip("_").lower()
                html_path = EXPORT_DIR / f"rfef_stage_4_regular_discovery_{safe_page_name}.html"
                html_path.write_text(page_html[:500000], encoding="utf-8")

                # 1. Search full HTML lines/fragments around Primera Federación / Liga Regular.
                html_fragments = re.split(r"[\n\r]+|</a>|</option>|</tr>|</div>", page_html)

                for fragment in html_fragments:
                    clean_fragment = re.sub(r"<[^>]+>", " ", fragment)
                    clean_fragment = re.sub(r"\s+", " ", clean_fragment).strip()
                    searchable = clean_fragment.lower()

                    matched = [
                        keyword for keyword in regular_keywords
                        if keyword in searchable
                    ]

                    if matched:
                        href_match = re.search(r'href=["\']([^"\']+)["\']', fragment, re.IGNORECASE)
                        href = href_match.group(1) if href_match else ""

                        combined_text = f"{fragment} {href}"

                        cod_temporada = extract_first_code(combined_text, code_patterns["cod_temporada"])
                        cod_competicion = extract_first_code(combined_text, code_patterns["cod_competicion"])
                        cod_grupo = extract_first_code(combined_text, code_patterns["cod_grupo"])
                        cod_jornada = extract_first_code(combined_text, code_patterns["cod_jornada"])

                        regular_signal = (
                            "true"
                            if "liga regular" in searchable or "fase regular" in searchable
                            else "false"
                        )

                        rfef_regular_discovery_rows.append({
                            "item_type": "html_fragment",
                            "label_or_text": clean_fragment[:1000],
                            "href_or_action": href,
                            "cod_temporada": cod_temporada,
                            "cod_competicion": cod_competicion,
                            "cod_grupo": cod_grupo,
                            "cod_jornada": cod_jornada,
                            "keyword_matches": "|".join(matched),
                            "regular_season_signal": regular_signal,
                            "notes": f"Found on {discovery_page['name']}",
                        })

                # 2. Extract all links and keep ones with useful keywords or RFEF code params.
                links = page.locator("a")
                link_count = links.count()

                for i in range(link_count):
                    try:
                        link = links.nth(i)
                        text = link.inner_text().strip()
                        href = link.get_attribute("href") or ""
                        full_href = urljoin(discovery_page["url"], href)

                        searchable = f"{text} {full_href}".lower()

                        matched = [
                            keyword for keyword in regular_keywords
                            if keyword in searchable
                        ]

                        has_codes = (
                            "codcompeticion" in searchable
                            or "codgrupo" in searchable
                            or "codtemporada" in searchable
                            or "codjornada" in searchable
                        )

                        if matched or has_codes:
                            cod_temporada = extract_first_code(full_href, code_patterns["cod_temporada"])
                            cod_competicion = extract_first_code(full_href, code_patterns["cod_competicion"])
                            cod_grupo = extract_first_code(full_href, code_patterns["cod_grupo"])
                            cod_jornada = extract_first_code(full_href, code_patterns["cod_jornada"])

                            regular_signal = (
                                "true"
                                if "liga regular" in searchable or "fase regular" in searchable
                                else "false"
                            )

                            rfef_regular_discovery_rows.append({
                                "item_type": "link",
                                "label_or_text": text[:1000],
                                "href_or_action": full_href,
                                "cod_temporada": cod_temporada,
                                "cod_competicion": cod_competicion,
                                "cod_grupo": cod_grupo,
                                "cod_jornada": cod_jornada,
                                "keyword_matches": "|".join(matched),
                                "regular_season_signal": regular_signal,
                                "notes": f"Link found on {discovery_page['name']}",
                            })

                    except Exception:
                        pass

                # 3. Extract options in case competition/group lives in dropdowns.
                options = page.locator("option")
                option_count = options.count()

                for i in range(option_count):
                    try:
                        option = options.nth(i)
                        text = option.inner_text().strip()
                        value = option.get_attribute("value") or ""

                        searchable = f"{text} {value}".lower()
                        matched = [
                            keyword for keyword in regular_keywords
                            if keyword in searchable
                        ]

                        if matched:
                            rfef_regular_discovery_rows.append({
                                "item_type": "option",
                                "label_or_text": text[:1000],
                                "href_or_action": "",
                                "cod_temporada": "",
                                "cod_competicion": value,
                                "cod_grupo": "",
                                "cod_jornada": "",
                                "keyword_matches": "|".join(matched),
                                "regular_season_signal": "true" if "liga regular" in searchable else "false",
                                "notes": f"Option found on {discovery_page['name']}",
                            })

                    except Exception:
                        pass

            except Exception as e:
                rfef_regular_discovery_rows.append({
                    "item_type": "error",
                    "label_or_text": "",
                    "href_or_action": discovery_page["url"],
                    "cod_temporada": "",
                    "cod_competicion": "",
                    "cod_grupo": "",
                    "cod_jornada": "",
                    "keyword_matches": "",
                    "regular_season_signal": "false",
                    "notes": f"Stage 4 discovery failed on {discovery_page['name']}: {type(e).__name__}: {e}",
                })

            page.close()

        browser.close()

except Exception as e:
    rfef_regular_discovery_rows.append({
        "item_type": "stage_error",
        "label_or_text": "",
        "href_or_action": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "keyword_matches": "",
        "regular_season_signal": "false",
        "notes": f"RFEF Stage 4 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_regular_season_code_discovery_candidates.csv",
    rfef_regular_discovery_fields,
    rfef_regular_discovery_rows,
)

print(f"RFEF Stage 4 found {len(rfef_regular_discovery_rows)} regular-season code candidates.")
# -----------------------------
# RFEF Stage 5: inspect official Primera Federación competition page for calendar/group links
# -----------------------------

rfef_competition_page_fields = [
    "item_type",
    "label_or_text",
    "href_or_action",
    "contains_calendario",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_actas",
    "contains_resultados",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "notes",
]

rfef_competition_page_rows = []

competition_page_url = "https://rfef.es/es/competiciones/primera-federacion"

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

        page.goto(competition_page_url, wait_until="networkidle", timeout=60000)

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

        html_path = EXPORT_DIR / "rfef_stage_5_primera_federacion_competition_page.html"
        html_path.write_text(page_html[:700000], encoding="utf-8")

        text_path = EXPORT_DIR / "rfef_stage_5_primera_federacion_competition_page_text.txt"
        text_path.write_text(page_text[:200000], encoding="utf-8")

        def extract_code_from_text(text, label):
            patterns = {
                "cod_temporada": [
                    r"CodTemporada=([0-9]+)",
                    r"codtemporada=([0-9]+)",
                    r"codtemporada%3D([0-9]+)",
                ],
                "cod_competicion": [
                    r"CodCompeticion=([0-9]+)",
                    r"codcompeticion=([0-9]+)",
                    r"codcompeticion%3D([0-9]+)",
                ],
                "cod_grupo": [
                    r"CodGrupo=([0-9]+)",
                    r"codgrupo=([0-9]+)",
                    r"codgrupo%3D([0-9]+)",
                ],
                "cod_jornada": [
                    r"CodJornada=([0-9]+)",
                    r"codjornada=([0-9]+)",
                    r"codjornada%3D([0-9]+)",
                ],
            }

            for pattern in patterns[label]:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
            return ""

        def add_candidate(item_type, label_or_text, href_or_action, notes):
            searchable = f"{label_or_text} {href_or_action}".lower()

            rfef_competition_page_rows.append({
                "item_type": item_type,
                "label_or_text": label_or_text[:1500],
                "href_or_action": href_or_action,
                "contains_calendario": str("calendario" in searchable).lower(),
                "contains_grupo_1": str("grupo 1" in searchable or "grupo i" in searchable).lower(),
                "contains_grupo_2": str("grupo 2" in searchable or "grupo ii" in searchable).lower(),
                "contains_actas": str("acta" in searchable or "actas" in searchable).lower(),
                "contains_resultados": str("resultado" in searchable or "resultados" in searchable).lower(),
                "cod_temporada": extract_code_from_text(href_or_action + " " + label_or_text, "cod_temporada"),
                "cod_competicion": extract_code_from_text(href_or_action + " " + label_or_text, "cod_competicion"),
                "cod_grupo": extract_code_from_text(href_or_action + " " + label_or_text, "cod_grupo"),
                "cod_jornada": extract_code_from_text(href_or_action + " " + label_or_text, "cod_jornada"),
                "notes": notes,
            })

        # 1. Extract all links from the competition page.
        links = page.locator("a")
        link_count = links.count()

        for i in range(link_count):
            try:
                link = links.nth(i)
                text = link.inner_text().strip()
                href = link.get_attribute("href") or ""
                full_href = urljoin(competition_page_url, href)

                searchable = f"{text} {full_href}".lower()

                if (
                    "calendario" in searchable
                    or "acta" in searchable
                    or "resultado" in searchable
                    or "grupo" in searchable
                    or "primera" in searchable
                    or "federacion" in searchable
                    or "federación" in searchable
                    or "codcompeticion" in searchable
                    or "codgrupo" in searchable
                    or "codtemporada" in searchable
                ):
                    add_candidate(
                        "link",
                        text,
                        full_href,
                        "Candidate link from official Primera Federación competition page.",
                    )

            except Exception:
                pass

        # 2. Extract buttons and clickable elements.
        clickable_selectors = [
            "button",
            "[role=button]",
            ".btn",
            ".button",
            "[onclick]",
        ]

        for selector in clickable_selectors:
            try:
                elements = page.locator(selector)
                count = elements.count()

                for i in range(count):
                    try:
                        el = elements.nth(i)
                        text = el.inner_text().strip()
                        onclick = el.get_attribute("onclick") or ""
                        href = el.get_attribute("href") or ""
                        action = onclick or href

                        searchable = f"{text} {action}".lower()

                        if (
                            "calendario" in searchable
                            or "acta" in searchable
                            or "resultado" in searchable
                            or "grupo" in searchable
                            or "primera" in searchable
                            or "federacion" in searchable
                            or "federación" in searchable
                            or "codcompeticion" in searchable
                            or "codgrupo" in searchable
                            or "codtemporada" in searchable
                        ):
                            add_candidate(
                                f"clickable:{selector}",
                                text,
                                action,
                                "Candidate clickable element from competition page.",
                            )
                    except Exception:
                        pass

            except Exception:
                pass

        # 3. Extract nearby HTML fragments containing important words.
        fragments = re.split(r"[\n\r]+|</a>|</button>|</div>|</li>|</tr>", page_html)

        for fragment in fragments:
            clean_fragment = re.sub(r"<[^>]+>", " ", fragment)
            clean_fragment = re.sub(r"\s+", " ", clean_fragment).strip()
            searchable = clean_fragment.lower()

            if (
                "calendario" in searchable
                or "actas" in searchable
                or "resultados" in searchable
                or "grupo 1" in searchable
                or "grupo 2" in searchable
                or "grupo i" in searchable
                or "grupo ii" in searchable
            ):
                href_match = re.search(r'href=["\']([^"\']+)["\']', fragment, re.IGNORECASE)
                href = href_match.group(1) if href_match else ""
                full_href = urljoin(competition_page_url, href) if href else ""

                add_candidate(
                    "html_fragment",
                    clean_fragment,
                    full_href,
                    "Relevant HTML fragment from official competition page.",
                )

        browser.close()

except Exception as e:
    rfef_competition_page_rows.append({
        "item_type": "error",
        "label_or_text": "",
        "href_or_action": "",
        "contains_calendario": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_actas": "false",
        "contains_resultados": "false",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "notes": f"RFEF Stage 5 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_primera_federacion_competition_page_candidates.csv",
    rfef_competition_page_fields,
    rfef_competition_page_rows,
)

print(f"RFEF Stage 5 found {len(rfef_competition_page_rows)} competition page candidates.")
# -----------------------------
# RFEF Stage 6: inspect dropdown hierarchy on marcadores page
# -----------------------------

rfef_dropdown_fields = [
    "select_index",
    "select_name",
    "select_id",
    "select_label_guess",
    "option_index",
    "option_text",
    "option_value",
    "contains_primera_federacion",
    "contains_liga_regular",
    "contains_grupo_1",
    "contains_grupo_2",
    "notes",
]

rfef_dropdown_rows = []

try:
    from playwright.sync_api import sync_playwright

    dropdown_url = "https://marcadores.rfef.es/pnfg/?accion=1"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page.goto(dropdown_url, wait_until="networkidle", timeout=60000)

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
        html_path = EXPORT_DIR / "rfef_stage_6_dropdown_page.html"
        html_path.write_text(page_html[:700000], encoding="utf-8")

        selects = page.locator("select")
        select_count = selects.count()

        for select_index in range(select_count):
            try:
                select = selects.nth(select_index)

                select_name = select.get_attribute("name") or ""
                select_id = select.get_attribute("id") or ""

                # Try to find nearby/preceding label text.
                select_label_guess = ""

                try:
                    if select_id:
                        label_locator = page.locator(f"label[for='{select_id}']")
                        if label_locator.count() > 0:
                            select_label_guess = label_locator.first.inner_text().strip()
                except Exception:
                    pass

                if not select_label_guess:
                    try:
                        parent_text = select.locator("xpath=..").inner_text().strip()
                        select_label_guess = re.sub(r"\s+", " ", parent_text[:300])
                    except Exception:
                        pass

                options = select.locator("option")
                option_count = options.count()

                for option_index in range(option_count):
                    try:
                        option = options.nth(option_index)

                        option_text = option.inner_text().strip()
                        option_value = option.get_attribute("value") or ""

                        searchable = f"{select_name} {select_id} {select_label_guess} {option_text} {option_value}".lower()

                        rfef_dropdown_rows.append({
                            "select_index": str(select_index),
                            "select_name": select_name,
                            "select_id": select_id,
                            "select_label_guess": select_label_guess,
                            "option_index": str(option_index),
                            "option_text": option_text,
                            "option_value": option_value,
                            "contains_primera_federacion": str(
                                "primera federación" in searchable
                                or "primera federacion" in searchable
                                or "1ª federación" in searchable
                                or "1ª federacion" in searchable
                            ).lower(),
                            "contains_liga_regular": str(
                                "liga regular" in searchable
                                or "fase regular" in searchable
                            ).lower(),
                            "contains_grupo_1": str(
                                "grupo 1" in searchable
                                or "grupo i" in searchable
                            ).lower(),
                            "contains_grupo_2": str(
                                "grupo 2" in searchable
                                or "grupo ii" in searchable
                            ).lower(),
                            "notes": "Dropdown option discovered on marcadores page.",
                        })

                    except Exception as e:
                        rfef_dropdown_rows.append({
                            "select_index": str(select_index),
                            "select_name": select_name,
                            "select_id": select_id,
                            "select_label_guess": select_label_guess,
                            "option_index": str(option_index),
                            "option_text": "",
                            "option_value": "",
                            "contains_primera_federacion": "false",
                            "contains_liga_regular": "false",
                            "contains_grupo_1": "false",
                            "contains_grupo_2": "false",
                            "notes": f"Option inspection failed: {type(e).__name__}: {e}",
                        })

            except Exception as e:
                rfef_dropdown_rows.append({
                    "select_index": str(select_index),
                    "select_name": "",
                    "select_id": "",
                    "select_label_guess": "",
                    "option_index": "",
                    "option_text": "",
                    "option_value": "",
                    "contains_primera_federacion": "false",
                    "contains_liga_regular": "false",
                    "contains_grupo_1": "false",
                    "contains_grupo_2": "false",
                    "notes": f"Select inspection failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    rfef_dropdown_rows.append({
        "select_index": "",
        "select_name": "",
        "select_id": "",
        "select_label_guess": "",
        "option_index": "",
        "option_text": "",
        "option_value": "",
        "contains_primera_federacion": "false",
        "contains_liga_regular": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "notes": f"RFEF Stage 6 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_stage_6_dropdown_hierarchy.csv",
    rfef_dropdown_fields,
    rfef_dropdown_rows,
)

# Small filtered summary of promising dropdown options
rfef_dropdown_filtered_fields = rfef_dropdown_fields

rfef_dropdown_filtered_rows = [
    row for row in rfef_dropdown_rows
    if row["contains_primera_federacion"] == "true"
    or row["contains_liga_regular"] == "true"
    or row["contains_grupo_1"] == "true"
    or row["contains_grupo_2"] == "true"
]

write_csv(
    "rfef_stage_6_dropdown_hierarchy_filtered.csv",
    rfef_dropdown_filtered_fields,
    rfef_dropdown_filtered_rows,
)

print(f"RFEF Stage 6 found {len(rfef_dropdown_rows)} dropdown option rows.")
print(f"RFEF Stage 6 found {len(rfef_dropdown_filtered_rows)} filtered candidate rows.")
# -----------------------------
# RFEF Stage 7: capture network requests from marcadores page
# -----------------------------

rfef_network_fields = [
    "request_index",
    "method",
    "resource_type",
    "url",
    "contains_competicion",
    "contains_temporada",
    "contains_grupo",
    "contains_jornada",
    "contains_calendario",
    "contains_actas",
    "contains_resultados",
    "contains_primera",
    "notes",
]

rfef_network_rows = []

try:
    from playwright.sync_api import sync_playwright

    network_url = "https://marcadores.rfef.es/pnfg/?accion=1"

    captured_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        def capture_request(request):
            try:
                captured_requests.append({
                    "method": request.method,
                    "resource_type": request.resource_type,
                    "url": request.url,
                })
            except Exception:
                pass

        page.on("request", capture_request)

        page.goto(network_url, wait_until="networkidle", timeout=60000)

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
                    page.wait_for_timeout(3000)
                    break
            except Exception:
                pass

        # Wait a little longer in case the page makes delayed requests.
        page.wait_for_timeout(5000)

        page_html = page.content()
        html_path = EXPORT_DIR / "rfef_stage_7_network_capture_page.html"
        html_path.write_text(page_html[:500000], encoding="utf-8")

        browser.close()

    interesting_keywords = [
        "competicion",
        "competición",
        "temporada",
        "grupo",
        "jornada",
        "calendario",
        "acta",
        "actas",
        "resultado",
        "resultados",
        "primera",
        "federacion",
        "federación",
        "pnfg",
        "NFG",
        "Cmp",
        "Vis",
    ]

    for index, req in enumerate(captured_requests):
        url = req["url"]
        searchable = url.lower()

        is_interesting = any(
            keyword.lower() in searchable
            for keyword in interesting_keywords
        )

        if is_interesting:
            rfef_network_rows.append({
                "request_index": str(index),
                "method": req["method"],
                "resource_type": req["resource_type"],
                "url": url,
                "contains_competicion": str("competicion" in searchable or "competición" in searchable).lower(),
                "contains_temporada": str("temporada" in searchable).lower(),
                "contains_grupo": str("grupo" in searchable).lower(),
                "contains_jornada": str("jornada" in searchable).lower(),
                "contains_calendario": str("calendario" in searchable).lower(),
                "contains_actas": str("acta" in searchable or "actas" in searchable).lower(),
                "contains_resultados": str("resultado" in searchable or "resultados" in searchable).lower(),
                "contains_primera": str("primera" in searchable).lower(),
                "notes": "Interesting network request captured from RFEF page load.",
            })

except Exception as e:
    rfef_network_rows.append({
        "request_index": "",
        "method": "",
        "resource_type": "",
        "url": "",
        "contains_competicion": "false",
        "contains_temporada": "false",
        "contains_grupo": "false",
        "contains_jornada": "false",
        "contains_calendario": "false",
        "contains_actas": "false",
        "contains_resultados": "false",
        "contains_primera": "false",
        "notes": f"RFEF Stage 7 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_stage_7_network_requests.csv",
    rfef_network_fields,
    rfef_network_rows,
)

print(f"RFEF Stage 7 captured {len(rfef_network_rows)} interesting network requests.")
# -----------------------------
# RFEF Stage 8: capture POST payload and response for NFG_CMP_Paneles
# -----------------------------

rfef_panel_fields = [
    "request_index",
    "method",
    "url",
    "post_data",
    "response_status",
    "response_sample",
    "contains_primera_federacion",
    "contains_liga_regular",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_codcompeticion",
    "contains_codgrupo",
    "contains_codtemporada",
    "notes",
]

rfef_panel_rows = []

try:
    from playwright.sync_api import sync_playwright

    panel_url = "https://marcadores.rfef.es/pnfg/?accion=1"

    captured_panel_requests = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

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
                url = request.url

                if "NFG_CMP_Paneles" not in url:
                    return

                post_data = request.post_data or ""

                try:
                    response_text = response.text()
                except Exception as response_error:
                    response_text = f"Could not read response text: {type(response_error).__name__}: {response_error}"

                captured_panel_requests.append({
                    "method": request.method,
                    "url": url,
                    "post_data": post_data,
                    "response_status": response.status,
                    "response_text": response_text,
                })

            except Exception:
                pass

        page.on("response", capture_response)

        page.goto(panel_url, wait_until="networkidle", timeout=60000)

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
                    page.wait_for_timeout(3000)
                    break
            except Exception:
                pass

        page.wait_for_timeout(8000)

        browser.close()

    for index, captured in enumerate(captured_panel_requests):
        response_text = captured["response_text"]
        response_lower = response_text.lower()

        safe_name = f"rfef_stage_8_panel_response_{index}.html"
        response_path = EXPORT_DIR / safe_name
        response_path.write_text(response_text[:1000000], encoding="utf-8")

        rfef_panel_rows.append({
            "request_index": str(index),
            "method": captured["method"],
            "url": captured["url"],
            "post_data": captured["post_data"],
            "response_status": str(captured["response_status"]),
            "response_sample": re.sub(r"\s+", " ", response_text[:3000]).strip(),
            "contains_primera_federacion": str(
                "primera federación" in response_lower
                or "primera federacion" in response_lower
            ).lower(),
            "contains_liga_regular": str(
                "liga regular" in response_lower
                or "fase regular" in response_lower
            ).lower(),
            "contains_grupo_1": str(
                "grupo 1" in response_lower
                or "grupo i" in response_lower
            ).lower(),
            "contains_grupo_2": str(
                "grupo 2" in response_lower
                or "grupo ii" in response_lower
            ).lower(),
            "contains_codcompeticion": str(
                "codcompeticion" in response_lower
                or "codcompeticion" in captured["post_data"].lower()
            ).lower(),
            "contains_codgrupo": str(
                "codgrupo" in response_lower
                or "codgrupo" in captured["post_data"].lower()
            ).lower(),
            "contains_codtemporada": str(
                "codtemporada" in response_lower
                or "codtemporada" in captured["post_data"].lower()
            ).lower(),
            "notes": f"Response saved to {safe_name}",
        })

    if not rfef_panel_rows:
        rfef_panel_rows.append({
            "request_index": "",
            "method": "",
            "url": "",
            "post_data": "",
            "response_status": "",
            "response_sample": "",
            "contains_primera_federacion": "false",
            "contains_liga_regular": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_codcompeticion": "false",
            "contains_codgrupo": "false",
            "contains_codtemporada": "false",
            "notes": "No NFG_CMP_Paneles responses captured.",
        })

except Exception as e:
    rfef_panel_rows.append({
        "request_index": "",
        "method": "",
        "url": "",
        "post_data": "",
        "response_status": "",
        "response_sample": "",
        "contains_primera_federacion": "false",
        "contains_liga_regular": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_codcompeticion": "false",
        "contains_codgrupo": "false",
        "contains_codtemporada": "false",
        "notes": f"RFEF Stage 8 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_stage_8_panel_request_response.csv",
    rfef_panel_fields,
    rfef_panel_rows,
)

print(f"RFEF Stage 8 captured {len(rfef_panel_rows)} panel request/response rows.")
# -----------------------------
# RFEF Stage 9: parse panel response for fixture/result code links
# -----------------------------

rfef_stage_9_fields = [
    "item_type",
    "label_or_text",
    "href_or_action",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "cod_acta",
    "contains_primera_federacion",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_jornada",
    "contains_calendario",
    "contains_acta",
    "contains_resultado",
    "notes",
]

rfef_stage_9_rows = []


def stage_9_extract_code(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


stage_9_code_patterns = {
    "cod_temporada": [
        r"CodTemporada=([0-9]+)",
        r"codtemporada=([0-9]+)",
        r"CodTemporada&quot;?:?&?quot;?([0-9]+)",
        r"codtemporada&quot;?:?&?quot;?([0-9]+)",
    ],
    "cod_competicion": [
        r"CodCompeticion=([0-9]+)",
        r"codcompeticion=([0-9]+)",
        r"CodCompeticion&quot;?:?&?quot;?([0-9]+)",
        r"codcompeticion&quot;?:?&?quot;?([0-9]+)",
    ],
    "cod_grupo": [
        r"CodGrupo=([0-9]+)",
        r"codgrupo=([0-9]+)",
        r"CodGrupo&quot;?:?&?quot;?([0-9]+)",
        r"codgrupo&quot;?:?&?quot;?([0-9]+)",
    ],
    "cod_jornada": [
        r"CodJornada=([0-9]+)",
        r"codjornada=([0-9]+)",
        r"CodJornada&quot;?:?&?quot;?([0-9]+)",
        r"codjornada&quot;?:?&?quot;?([0-9]+)",
    ],
    "cod_acta": [
        r"CodActa=([0-9]+)",
        r"codacta=([0-9]+)",
        r"codacta&quot;?:?&?quot;?([0-9]+)",
    ],
}

try:
    panel_files = sorted(EXPORT_DIR.glob("rfef_stage_8_panel_response_*.html"))

    if not panel_files:
        rfef_stage_9_rows.append({
            "item_type": "error",
            "label_or_text": "",
            "href_or_action": "",
            "cod_temporada": "",
            "cod_competicion": "",
            "cod_grupo": "",
            "cod_jornada": "",
            "cod_acta": "",
            "contains_primera_federacion": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_jornada": "false",
            "contains_calendario": "false",
            "contains_acta": "false",
            "contains_resultado": "false",
            "notes": "No Stage 8 panel response HTML files found.",
        })

    for panel_file in panel_files:
        panel_html = panel_file.read_text(encoding="utf-8", errors="ignore")
        panel_lower = panel_html.lower()

        # Save a plain-text version for easier manual inspection.
        plain_text = re.sub(r"<[^>]+>", " ", panel_html)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()

        plain_path = EXPORT_DIR / f"{panel_file.stem}_plain_text.txt"
        plain_path.write_text(plain_text[:500000], encoding="utf-8")

        # 1. Extract anchor hrefs.
        link_matches = re.findall(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            panel_html,
            re.IGNORECASE | re.DOTALL,
        )

        for href, raw_text in link_matches:
            label = re.sub(r"<[^>]+>", " ", raw_text)
            label = re.sub(r"\s+", " ", label).strip()

            combined = f"{label} {href}"
            combined_lower = combined.lower()

            if (
                "codcompeticion" in combined_lower
                or "codgrupo" in combined_lower
                or "codtemporada" in combined_lower
                or "codjornada" in combined_lower
                or "codacta" in combined_lower
                or "primera" in combined_lower
                or "federaci" in combined_lower
                or "grupo" in combined_lower
                or "jornada" in combined_lower
                or "calendario" in combined_lower
                or "acta" in combined_lower
                or "resultado" in combined_lower
            ):
                rfef_stage_9_rows.append({
                    "item_type": "link",
                    "label_or_text": label[:1200],
                    "href_or_action": href,
                    "cod_temporada": stage_9_extract_code(combined, stage_9_code_patterns["cod_temporada"]),
                    "cod_competicion": stage_9_extract_code(combined, stage_9_code_patterns["cod_competicion"]),
                    "cod_grupo": stage_9_extract_code(combined, stage_9_code_patterns["cod_grupo"]),
                    "cod_jornada": stage_9_extract_code(combined, stage_9_code_patterns["cod_jornada"]),
                    "cod_acta": stage_9_extract_code(combined, stage_9_code_patterns["cod_acta"]),
                    "contains_primera_federacion": str("primera federación" in combined_lower or "primera federacion" in combined_lower).lower(),
                    "contains_grupo_1": str("grupo 1" in combined_lower or "grupo i" in combined_lower).lower(),
                    "contains_grupo_2": str("grupo 2" in combined_lower or "grupo ii" in combined_lower).lower(),
                    "contains_jornada": str("jornada" in combined_lower).lower(),
                    "contains_calendario": str("calendario" in combined_lower).lower(),
                    "contains_acta": str("acta" in combined_lower).lower(),
                    "contains_resultado": str("resultado" in combined_lower or "resultados" in combined_lower).lower(),
                    "notes": f"Link extracted from {panel_file.name}",
                })

        # 2. Extract onclick/action fragments.
        onclick_matches = re.findall(
            r'onclick=["\']([^"\']+)["\']',
            panel_html,
            re.IGNORECASE | re.DOTALL,
        )

        for onclick in onclick_matches:
            combined = onclick
            combined_lower = combined.lower()

            if (
                "codcompeticion" in combined_lower
                or "codgrupo" in combined_lower
                or "codtemporada" in combined_lower
                or "codjornada" in combined_lower
                or "codacta" in combined_lower
                or "jornada" in combined_lower
                or "calendario" in combined_lower
                or "acta" in combined_lower
                or "resultado" in combined_lower
            ):
                rfef_stage_9_rows.append({
                    "item_type": "onclick",
                    "label_or_text": "",
                    "href_or_action": onclick[:1500],
                    "cod_temporada": stage_9_extract_code(combined, stage_9_code_patterns["cod_temporada"]),
                    "cod_competicion": stage_9_extract_code(combined, stage_9_code_patterns["cod_competicion"]),
                    "cod_grupo": stage_9_extract_code(combined, stage_9_code_patterns["cod_grupo"]),
                    "cod_jornada": stage_9_extract_code(combined, stage_9_code_patterns["cod_jornada"]),
                    "cod_acta": stage_9_extract_code(combined, stage_9_code_patterns["cod_acta"]),
                    "contains_primera_federacion": str("primera federación" in combined_lower or "primera federacion" in combined_lower).lower(),
                    "contains_grupo_1": str("grupo 1" in combined_lower or "grupo i" in combined_lower).lower(),
                    "contains_grupo_2": str("grupo 2" in combined_lower or "grupo ii" in combined_lower).lower(),
                    "contains_jornada": str("jornada" in combined_lower).lower(),
                    "contains_calendario": str("calendario" in combined_lower).lower(),
                    "contains_acta": str("acta" in combined_lower).lower(),
                    "contains_resultado": str("resultado" in combined_lower or "resultados" in combined_lower).lower(),
                    "notes": f"Onclick extracted from {panel_file.name}",
                })

        # 3. Extract HTML fragments around code-looking values.
        fragments = re.split(r"[\n\r]+|</a>|</button>|</div>|</li>|</tr>|</span>", panel_html)

        for fragment in fragments:
            fragment_lower = fragment.lower()

            if (
                "codcompeticion" in fragment_lower
                or "codgrupo" in fragment_lower
                or "codtemporada" in fragment_lower
                or "codjornada" in fragment_lower
                or "codacta" in fragment_lower
                or "primera federación" in fragment_lower
                or "primera federacion" in fragment_lower
                or "grupo 1" in fragment_lower
                or "grupo 2" in fragment_lower
                or "grupo i" in fragment_lower
                or "grupo ii" in fragment_lower
            ):
                label = re.sub(r"<[^>]+>", " ", fragment)
                label = re.sub(r"\s+", " ", label).strip()

                rfef_stage_9_rows.append({
                    "item_type": "html_fragment",
                    "label_or_text": label[:1500],
                    "href_or_action": fragment[:1500],
                    "cod_temporada": stage_9_extract_code(fragment, stage_9_code_patterns["cod_temporada"]),
                    "cod_competicion": stage_9_extract_code(fragment, stage_9_code_patterns["cod_competicion"]),
                    "cod_grupo": stage_9_extract_code(fragment, stage_9_code_patterns["cod_grupo"]),
                    "cod_jornada": stage_9_extract_code(fragment, stage_9_code_patterns["cod_jornada"]),
                    "cod_acta": stage_9_extract_code(fragment, stage_9_code_patterns["cod_acta"]),
                    "contains_primera_federacion": str("primera federación" in fragment_lower or "primera federacion" in fragment_lower).lower(),
                    "contains_grupo_1": str("grupo 1" in fragment_lower or "grupo i" in fragment_lower).lower(),
                    "contains_grupo_2": str("grupo 2" in fragment_lower or "grupo ii" in fragment_lower).lower(),
                    "contains_jornada": str("jornada" in fragment_lower).lower(),
                    "contains_calendario": str("calendario" in fragment_lower).lower(),
                    "contains_acta": str("acta" in fragment_lower).lower(),
                    "contains_resultado": str("resultado" in fragment_lower or "resultados" in fragment_lower).lower(),
                    "notes": f"HTML fragment extracted from {panel_file.name}",
                })

except Exception as e:
    rfef_stage_9_rows.append({
        "item_type": "error",
        "label_or_text": "",
        "href_or_action": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "cod_acta": "",
        "contains_primera_federacion": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_jornada": "false",
        "contains_calendario": "false",
        "contains_acta": "false",
        "contains_resultado": "false",
        "notes": f"RFEF Stage 9 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_stage_9_panel_code_links.csv",
    rfef_stage_9_fields,
    rfef_stage_9_rows,
)

print(f"RFEF Stage 9 extracted {len(rfef_stage_9_rows)} panel code/link candidates.")
# -----------------------------
# RFEF Stage 10: test grupo_categoria values against NFG_CMP_Paneles
# -----------------------------

import urllib.parse

rfef_stage_10_fields = [
    "grupo_categoria",
    "response_status",
    "response_length",
    "contains_primera_federacion",
    "contains_liga_regular",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_segunda_division",
    "contains_play_off",
    "contains_codcompeticion",
    "contains_codgrupo",
    "sample_text",
    "notes",
]

rfef_stage_10_rows = []

# We know 900163685 and 900163686 returned Segunda / playoff panels.
# This tests nearby category IDs to discover the regular Primera Federación category.
grupo_categoria_candidates = [
    "900163680",
    "900163681",
    "900163682",
    "900163683",
    "900163684",
    "900163685",
    "900163686",
    "900163687",
    "900163688",
    "900163689",
    "900163690",
    "900163691",
    "900163692",
    "900163693",
    "900163694",
    "900163695",
    "900163696",
    "900163697",
    "900163698",
    "900163699",
    "900163700",
    "900163701",
    "900163702",
    "900163703",
    "900163704",
    "900163705",
]

try:
    from playwright.sync_api import sync_playwright

    panel_endpoint = "https://marcadores.rfef.es/pnfg/NPcd/NFG_CMP_Paneles"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        # First open the main page to establish any session/cookies.
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
                    page.wait_for_timeout(2000)
                    break
            except Exception:
                pass

        for grupo_categoria in grupo_categoria_candidates:
            try:
                post_data = urllib.parse.urlencode({
                    "cod_primaria": "3001668",
                    "grupo_categoria": grupo_categoria,
                    "resultados": "1",
                    "columna": "1",
                    "extendido": "1",
                    "no_paginacion": "1",
                    "tipo_peticion": "1",
                    "N_Ajax": "1",
                })

                response = page.request.post(
                    panel_endpoint,
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "X-Requested-With": "XMLHttpRequest",
                        "Referer": "https://marcadores.rfef.es/pnfg/?accion=1",
                    },
                    data=post_data,
                    timeout=60000,
                )

                response_text = response.text()
                response_lower = response_text.lower()

                safe_name = re.sub(r"[^A-Za-z0-9]+", "_", grupo_categoria).strip("_")
                response_path = EXPORT_DIR / f"rfef_stage_10_grupo_categoria_{safe_name}.html"
                response_path.write_text(response_text[:1000000], encoding="utf-8")

                sample_text = re.sub(r"<[^>]+>", " ", response_text[:4000])
                sample_text = re.sub(r"\s+", " ", sample_text).strip()

                rfef_stage_10_rows.append({
                    "grupo_categoria": grupo_categoria,
                    "response_status": str(response.status),
                    "response_length": str(len(response_text)),
                    "contains_primera_federacion": str(
                        "primera federación" in response_lower
                        or "primera federacion" in response_lower
                    ).lower(),
                    "contains_liga_regular": str(
                        "liga regular" in response_lower
                        or "fase regular" in response_lower
                    ).lower(),
                    "contains_grupo_1": str(
                        "grupo 1" in response_lower
                        or "grupo i" in response_lower
                    ).lower(),
                    "contains_grupo_2": str(
                        "grupo 2" in response_lower
                        or "grupo ii" in response_lower
                    ).lower(),
                    "contains_segunda_division": str(
                        "segunda división" in response_lower
                        or "segunda division" in response_lower
                    ).lower(),
                    "contains_play_off": str(
                        "play off" in response_lower
                        or "play-off" in response_lower
                        or "playoff" in response_lower
                    ).lower(),
                    "contains_codcompeticion": str("codcompeticion" in response_lower).lower(),
                    "contains_codgrupo": str("codgrupo" in response_lower).lower(),
                    "sample_text": sample_text,
                    "notes": "POST test against NFG_CMP_Paneles with candidate grupo_categoria.",
                })

            except Exception as e:
                rfef_stage_10_rows.append({
                    "grupo_categoria": grupo_categoria,
                    "response_status": "",
                    "response_length": "0",
                    "contains_primera_federacion": "false",
                    "contains_liga_regular": "false",
                    "contains_grupo_1": "false",
                    "contains_grupo_2": "false",
                    "contains_segunda_division": "false",
                    "contains_play_off": "false",
                    "contains_codcompeticion": "false",
                    "contains_codgrupo": "false",
                    "sample_text": "",
                    "notes": f"Stage 10 candidate failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    rfef_stage_10_rows.append({
        "grupo_categoria": "",
        "response_status": "",
        "response_length": "0",
        "contains_primera_federacion": "false",
        "contains_liga_regular": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_segunda_division": "false",
        "contains_play_off": "false",
        "contains_codcompeticion": "false",
        "contains_codgrupo": "false",
        "sample_text": "",
        "notes": f"RFEF Stage 10 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_stage_10_grupo_categoria_tests.csv",
    rfef_stage_10_fields,
    rfef_stage_10_rows,
)

print(f"RFEF Stage 10 tested {len(rfef_stage_10_rows)} grupo_categoria candidates.")

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

from pathlib import Path
import csv
import re
from urllib.parse import urljoin
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

    print(f"Created {path}")


def clean_text(text, limit=2000):
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


# -----------------------------
# RFEF Research Stage R1:
# JavaScript bundle and network source inspection
# -----------------------------

r1_script_fields = [
    "source_page_url",
    "script_index",
    "script_url",
    "download_status",
    "script_length",
    "contains_nfg_cmp_paneles",
    "contains_grupo_categoria",
    "contains_cod_primaria",
    "contains_codcompeticion",
    "contains_codgrupo",
    "contains_codtemporada",
    "contains_primera_federacion",
    "contains_categoria",
    "contains_competicion",
    "notes",
]

r1_match_fields = [
    "source_type",
    "source_url",
    "keyword",
    "match_context",
    "notes",
]

r1_network_fields = [
    "request_index",
    "method",
    "resource_type",
    "url",
    "post_data",
    "response_status",
    "response_length",
    "contains_nfg_cmp_paneles",
    "contains_grupo_categoria",
    "contains_cod_primaria",
    "contains_codcompeticion",
    "contains_codgrupo",
    "contains_codtemporada",
    "contains_primera_federacion",
    "sample_text",
    "notes",
]

r1_summary_fields = [
    "check_name",
    "result",
    "details",
]

r1_script_rows = []
r1_match_rows = []
r1_network_rows = []
r1_summary_rows = []

keywords = [
    "NFG_CMP_Paneles",
    "grupo_categoria",
    "grupoCategoria",
    "cod_primaria",
    "CodCompeticion",
    "codcompeticion",
    "CodGrupo",
    "codgrupo",
    "CodTemporada",
    "codtemporada",
    "Primera Federación",
    "Primera Federacion",
    "Primera Federaci",
    "categoria",
    "categoría",
    "competicion",
    "competición",
    "grupo",
    "jornada",
]


def add_keyword_matches(source_type, source_url, text, notes):
    lower_text = text.lower()

    for keyword in keywords:
        keyword_lower = keyword.lower()
        start = 0

        while True:
            index = lower_text.find(keyword_lower, start)

            if index == -1:
                break

            context_start = max(index - 500, 0)
            context_end = min(index + len(keyword) + 500, len(text))
            context = text[context_start:context_end]

            r1_match_rows.append({
                "source_type": source_type,
                "source_url": source_url,
                "keyword": keyword,
                "match_context": clean_text(context, 1200),
                "notes": notes,
            })

            start = index + len(keyword_lower)


try:
    from playwright.sync_api import sync_playwright

    source_page_url = "https://marcadores.rfef.es/pnfg/?accion=1"

    captured_requests = []
    captured_responses = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        def on_request(request):
            try:
                captured_requests.append({
                    "method": request.method,
                    "resource_type": request.resource_type,
                    "url": request.url,
                    "post_data": request.post_data or "",
                })
            except Exception:
                pass

        def on_response(response):
            try:
                request = response.request
                url = request.url
                resource_type = request.resource_type

                if resource_type in ["xhr", "fetch", "document", "script"]:
                    try:
                        body = response.body()
                        text = body.decode("utf-8", errors="ignore")
                    except Exception:
                        text = ""

                    captured_responses.append({
                        "method": request.method,
                        "resource_type": resource_type,
                        "url": url,
                        "post_data": request.post_data or "",
                        "status": response.status,
                        "text": text,
                    })
            except Exception:
                pass

        page.on("request", on_request)
        page.on("response", on_response)

        page.goto(source_page_url, wait_until="networkidle", timeout=60000)

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

        page.wait_for_timeout(7000)

        page_html = page.content()
        page_text = page.inner_text("body")

        (EXPORT_DIR / "rfef_research_r1_page.html").write_text(
            page_html[:1000000],
            encoding="utf-8",
        )

        (EXPORT_DIR / "rfef_research_r1_page_text.txt").write_text(
            page_text[:500000],
            encoding="utf-8",
        )

        add_keyword_matches(
            "page_html",
            source_page_url,
            page_html,
            "Keyword found in main page HTML.",
        )

        add_keyword_matches(
            "page_text",
            source_page_url,
            page_text,
            "Keyword found in main page visible text.",
        )

        script_srcs = page.locator("script[src]")
        script_count = script_srcs.count()

        for script_index in range(script_count):
            script_url = ""

            try:
                script_el = script_srcs.nth(script_index)
                script_src = script_el.get_attribute("src") or ""
                script_url = urljoin(source_page_url, script_src)

                response = page.request.get(script_url, timeout=60000)
                script_body = response.body()
                script_text = script_body.decode("utf-8", errors="ignore")
                script_lower = script_text.lower()

                safe_script_name = re.sub(
                    r"[^A-Za-z0-9]+",
                    "_",
                    f"script_{script_index}",
                ).strip("_")

                script_path = EXPORT_DIR / f"rfef_research_r1_{safe_script_name}.js"
                script_path.write_text(script_text[:2000000], encoding="utf-8")

                r1_script_rows.append({
                    "source_page_url": source_page_url,
                    "script_index": str(script_index),
                    "script_url": script_url,
                    "download_status": str(response.status),
                    "script_length": str(len(script_text)),
                    "contains_nfg_cmp_paneles": str("nfg_cmp_paneles" in script_lower).lower(),
                    "contains_grupo_categoria": str("grupo_categoria" in script_lower or "grupocategoria" in script_lower).lower(),
                    "contains_cod_primaria": str("cod_primaria" in script_lower).lower(),
                    "contains_codcompeticion": str("codcompeticion" in script_lower).lower(),
                    "contains_codgrupo": str("codgrupo" in script_lower).lower(),
                    "contains_codtemporada": str("codtemporada" in script_lower).lower(),
                    "contains_primera_federacion": str(
                        "primera federación" in script_lower
                        or "primera federacion" in script_lower
                        or "primera federaci" in script_lower
                    ).lower(),
                    "contains_categoria": str("categoria" in script_lower or "categoría" in script_lower).lower(),
                    "contains_competicion": str("competicion" in script_lower or "competición" in script_lower).lower(),
                    "notes": "Script downloaded and scanned.",
                })

                add_keyword_matches(
                    "script",
                    script_url,
                    script_text,
                    f"Keyword found in downloaded script index {script_index}.",
                )

            except Exception as e:
                r1_script_rows.append({
                    "source_page_url": source_page_url,
                    "script_index": str(script_index),
                    "script_url": script_url,
                    "download_status": "",
                    "script_length": "0",
                    "contains_nfg_cmp_paneles": "false",
                    "contains_grupo_categoria": "false",
                    "contains_cod_primaria": "false",
                    "contains_codcompeticion": "false",
                    "contains_codgrupo": "false",
                    "contains_codtemporada": "false",
                    "contains_primera_federacion": "false",
                    "contains_categoria": "false",
                    "contains_competicion": "false",
                    "notes": f"Script download/scan failed: {type(e).__name__}: {e}",
                })

        browser.close()

    # Network response summary
    for index, response in enumerate(captured_responses):
        text = response.get("text", "")
        text_lower = text.lower()
        url_lower = response.get("url", "").lower()
        post_lower = response.get("post_data", "").lower()

        interesting = (
            "nfg_cmp_paneles" in url_lower
            or "nfg_cmp_paneles" in text_lower
            or "grupo_categoria" in text_lower
            or "grupo_categoria" in post_lower
            or "codcompeticion" in text_lower
            or "codgrupo" in text_lower
            or "codtemporada" in text_lower
            or "primera federación" in text_lower
            or "primera federacion" in text_lower
            or "primera federaci" in text_lower
        )

        if interesting:
            safe_response_name = re.sub(
                r"[^A-Za-z0-9]+",
                "_",
                f"network_response_{index}",
            ).strip("_")

            response_path = EXPORT_DIR / f"rfef_research_r1_{safe_response_name}.txt"
            response_path.write_text(text[:1000000], encoding="utf-8")

            r1_network_rows.append({
                "request_index": str(index),
                "method": response.get("method", ""),
                "resource_type": response.get("resource_type", ""),
                "url": response.get("url", ""),
                "post_data": response.get("post_data", ""),
                "response_status": str(response.get("status", "")),
                "response_length": str(len(text)),
                "contains_nfg_cmp_paneles": str("nfg_cmp_paneles" in url_lower or "nfg_cmp_paneles" in text_lower).lower(),
                "contains_grupo_categoria": str("grupo_categoria" in text_lower or "grupo_categoria" in post_lower).lower(),
                "contains_cod_primaria": str("cod_primaria" in text_lower or "cod_primaria" in post_lower).lower(),
                "contains_codcompeticion": str("codcompeticion" in text_lower).lower(),
                "contains_codgrupo": str("codgrupo" in text_lower).lower(),
                "contains_codtemporada": str("codtemporada" in text_lower).lower(),
                "contains_primera_federacion": str(
                    "primera federación" in text_lower
                    or "primera federacion" in text_lower
                    or "primera federaci" in text_lower
                ).lower(),
                "sample_text": clean_text(text, 2000),
                "notes": "Interesting network response captured.",
            })

            add_keyword_matches(
                "network_response",
                response.get("url", ""),
                text,
                f"Keyword found in captured network response index {index}.",
            )

except Exception as e:
    r1_summary_rows.append({
        "check_name": "r1_stage_error",
        "result": "failed",
        "details": f"{type(e).__name__}: {e}",
    })


write_csv(
    "rfef_research_r1_script_scan.csv",
    r1_script_fields,
    r1_script_rows,
)

write_csv(
    "rfef_research_r1_keyword_matches.csv",
    r1_match_fields,
    r1_match_rows,
)

write_csv(
    "rfef_research_r1_network_responses.csv",
    r1_network_fields,
    r1_network_rows,
)

r1_summary_rows.extend([
    {
        "check_name": "scripts_scanned",
        "result": str(len(r1_script_rows)),
        "details": "Downloaded script files from marcadores page.",
    },
    {
        "check_name": "keyword_matches",
        "result": str(len(r1_match_rows)),
        "details": "Keyword context matches across page, scripts and network responses.",
    },
    {
        "check_name": "interesting_network_responses",
        "result": str(len(r1_network_rows)),
        "details": "Network responses containing RFEF code/competition keywords.",
    },
])

write_csv(
    "rfef_research_r1_summary.csv",
    r1_summary_fields,
    r1_summary_rows,
)

print("RFEF Research Stage R1 complete.")
print(f"Scripts scanned: {len(r1_script_rows)}")
print(f"Keyword matches: {len(r1_match_rows)}")
print(f"Interesting network responses: {len(r1_network_rows)}")
# -----------------------------
# RFEF Research Stage R2:
# Test exact payloads discovered from marcadores page buttons
# -----------------------------

import urllib.parse

r2_fields = [
    "payload_name",
    "post_data",
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
    "contains_codtemporada",
    "sample_text",
    "notes",
]

r2_rows = []

r2_payloads = [
    {
        "payload_name": "Football masculino resultados exact button",
        "payload": {
            "cod_primaria": "3001668",
            "grupo_categoria": "900163684,901753363",
            "resultados": "1",
            "columna": "1",
            "extendido": "1",
            "no_paginacion": "1",
            "tipo_peticion": "2",
            "N_Ajax": "1",
        },
    },
    {
        "payload_name": "Football masculino clasificacion exact button",
        "payload": {
            "cod_primaria": "3001668",
            "grupo_categoria": "900163684,901753363",
            "clasificacion": "1",
            "columna": "1",
            "extendido": "1",
            "no_paginacion": "1",
            "tipo_competicion": "2",
            "tipo_peticion": "2",
            "N_Ajax": "1",
        },
    },
    {
        "payload_name": "Football masculino/femenino clasificacion exact button",
        "payload": {
            "cod_primaria": "3001668",
            "grupo_categoria": "900163685,900163686",
            "clasificacion": "1",
            "columna": "1",
            "extendido": "1",
            "no_paginacion": "1",
            "tipo_competicion": "2",
            "tipo_peticion": "1",
            "N_Ajax": "1",
        },
    },
    {
        "payload_name": "Football masculino/femenino resultados variant",
        "payload": {
            "cod_primaria": "3001668",
            "grupo_categoria": "900163685,900163686",
            "resultados": "1",
            "columna": "1",
            "extendido": "1",
            "no_paginacion": "1",
            "tipo_peticion": "1",
            "N_Ajax": "1",
        },
    },
]


def r2_safe_decode(response_body):
    for encoding in ["utf-8", "latin-1", "cp1252"]:
        try:
            return response_body.decode(encoding), encoding
        except Exception:
            pass
    return response_body.decode("utf-8", errors="ignore"), "utf-8-ignore"


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

        for payload_item in r2_payloads:
            payload_name = payload_item["payload_name"]
            payload = payload_item["payload"]
            post_data = urllib.parse.urlencode(payload)

            try:
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

                response_text, decode_method = r2_safe_decode(response.body())
                response_lower = response_text.lower()

                safe_name = re.sub(r"[^A-Za-z0-9]+", "_", payload_name).strip("_").lower()
                response_path = EXPORT_DIR / f"rfef_research_r2_{safe_name}.html"
                response_path.write_text(response_text[:1000000], encoding="utf-8")

                sample_text = re.sub(r"<[^>]+>", " ", response_text[:7000])
                sample_text = re.sub(r"\s+", " ", sample_text).strip()

                r2_rows.append({
                    "payload_name": payload_name,
                    "post_data": post_data,
                    "response_status": str(response.status),
                    "response_length": str(len(response_text)),
                    "contains_primera_federacion": str(
                        "primera federación" in response_lower
                        or "primera federacion" in response_lower
                        or "primera federaci" in response_lower
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
                    "contains_codtemporada": str("codtemporada" in response_lower).lower(),
                    "sample_text": sample_text,
                    "notes": f"Exact page-button payload tested. Decode method: {decode_method}",
                })

            except Exception as e:
                r2_rows.append({
                    "payload_name": payload_name,
                    "post_data": post_data,
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
                    "contains_codtemporada": "false",
                    "sample_text": "",
                    "notes": f"R2 payload failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    r2_rows.append({
        "payload_name": "stage_error",
        "post_data": "",
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
        "contains_codtemporada": "false",
        "sample_text": "",
        "notes": f"RFEF Research R2 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r2_exact_payload_tests.csv",
    r2_fields,
    r2_rows,
)

print(f"RFEF Research R2 tested {len(r2_rows)} exact payloads.")
# -----------------------------
# RFEF Research Stage R3:
# Parse exact classification payload response for Primera Federación regular group codes
# -----------------------------

r3_fields = [
    "item_type",
    "label_or_text",
    "href_or_action",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "contains_primera_federacion",
    "contains_liga_regular",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_codcompeticion",
    "contains_codgrupo",
    "contains_codtemporada",
    "notes",
]

r3_rows = []


def r3_extract_code(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


r3_patterns = {
    "cod_temporada": [
        r"CodTemporada=([0-9]+)",
        r"codtemporada=([0-9]+)",
        r"CodTemporada['\" ]*[:=]['\" ]*([0-9]+)",
        r"codtemporada['\" ]*[:=]['\" ]*([0-9]+)",
    ],
    "cod_competicion": [
        r"CodCompeticion=([0-9]+)",
        r"codcompeticion=([0-9]+)",
        r"CodCompeticion['\" ]*[:=]['\" ]*([0-9]+)",
        r"codcompeticion['\" ]*[:=]['\" ]*([0-9]+)",
    ],
    "cod_grupo": [
        r"CodGrupo=([0-9]+)",
        r"codgrupo=([0-9]+)",
        r"CodGrupo['\" ]*[:=]['\" ]*([0-9]+)",
        r"codgrupo['\" ]*[:=]['\" ]*([0-9]+)",
    ],
}

try:
    response_file = EXPORT_DIR / "rfef_research_r2_football_masculino_femenino_clasificacion_exact_button.html"

    if not response_file.exists():
        r3_rows.append({
            "item_type": "error",
            "label_or_text": "",
            "href_or_action": "",
            "cod_temporada": "",
            "cod_competicion": "",
            "cod_grupo": "",
            "contains_primera_federacion": "false",
            "contains_liga_regular": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_codcompeticion": "false",
            "contains_codgrupo": "false",
            "contains_codtemporada": "false",
            "notes": "Expected R2 classification response HTML file not found. Run R2 first.",
        })

    else:
        html = response_file.read_text(encoding="utf-8", errors="ignore")

        plain_text = re.sub(r"<[^>]+>", " ", html)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()

        plain_path = EXPORT_DIR / "rfef_research_r3_classification_response_plain_text.txt"
        plain_path.write_text(plain_text[:500000], encoding="utf-8")

        # Extract links.
        link_matches = re.findall(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        for href, raw_text in link_matches:
            label = re.sub(r"<[^>]+>", " ", raw_text)
            label = re.sub(r"\s+", " ", label).strip()

            combined = f"{label} {href}"
            combined_lower = combined.lower()

            if (
                "primera federación" in combined_lower
                or "primera federacion" in combined_lower
                or "liga regular" in combined_lower
                or "grupo 1" in combined_lower
                or "grupo 2" in combined_lower
                or "grupo i" in combined_lower
                or "grupo ii" in combined_lower
                or "codcompeticion" in combined_lower
                or "codgrupo" in combined_lower
                or "codtemporada" in combined_lower
            ):
                r3_rows.append({
                    "item_type": "link",
                    "label_or_text": label[:1500],
                    "href_or_action": href[:2000],
                    "cod_temporada": r3_extract_code(combined, r3_patterns["cod_temporada"]),
                    "cod_competicion": r3_extract_code(combined, r3_patterns["cod_competicion"]),
                    "cod_grupo": r3_extract_code(combined, r3_patterns["cod_grupo"]),
                    "contains_primera_federacion": str(
                        "primera federación" in combined_lower
                        or "primera federacion" in combined_lower
                        or "primera federaci" in combined_lower
                    ).lower(),
                    "contains_liga_regular": str(
                        "liga regular" in combined_lower
                        or "fase regular" in combined_lower
                    ).lower(),
                    "contains_grupo_1": str(
                        "grupo 1" in combined_lower
                        or "grupo i" in combined_lower
                    ).lower(),
                    "contains_grupo_2": str(
                        "grupo 2" in combined_lower
                        or "grupo ii" in combined_lower
                    ).lower(),
                    "contains_codcompeticion": str("codcompeticion" in combined_lower).lower(),
                    "contains_codgrupo": str("codgrupo" in combined_lower).lower(),
                    "contains_codtemporada": str("codtemporada" in combined_lower).lower(),
                    "notes": "Link extracted from R2 classification response.",
                })

        # Extract relevant HTML fragments.
        fragments = re.split(
            r"[\n\r]+|</a>|</button>|</div>|</li>|</tr>|</span>|</section>",
            html,
        )

        for fragment in fragments:
            fragment_lower = fragment.lower()

            if (
                "primera federación" in fragment_lower
                or "primera federacion" in fragment_lower
                or "primera federaci" in fragment_lower
                or "liga regular" in fragment_lower
                or "fase regular" in fragment_lower
                or "grupo 1" in fragment_lower
                or "grupo 2" in fragment_lower
                or "grupo i" in fragment_lower
                or "grupo ii" in fragment_lower
                or "codcompeticion" in fragment_lower
                or "codgrupo" in fragment_lower
                or "codtemporada" in fragment_lower
            ):
                label = re.sub(r"<[^>]+>", " ", fragment)
                label = re.sub(r"\s+", " ", label).strip()

                r3_rows.append({
                    "item_type": "html_fragment",
                    "label_or_text": label[:2000],
                    "href_or_action": fragment[:2500],
                    "cod_temporada": r3_extract_code(fragment, r3_patterns["cod_temporada"]),
                    "cod_competicion": r3_extract_code(fragment, r3_patterns["cod_competicion"]),
                    "cod_grupo": r3_extract_code(fragment, r3_patterns["cod_grupo"]),
                    "contains_primera_federacion": str(
                        "primera federación" in fragment_lower
                        or "primera federacion" in fragment_lower
                        or "primera federaci" in fragment_lower
                    ).lower(),
                    "contains_liga_regular": str(
                        "liga regular" in fragment_lower
                        or "fase regular" in fragment_lower
                    ).lower(),
                    "contains_grupo_1": str(
                        "grupo 1" in fragment_lower
                        or "grupo i" in fragment_lower
                    ).lower(),
                    "contains_grupo_2": str(
                        "grupo 2" in fragment_lower
                        or "grupo ii" in fragment_lower
                    ).lower(),
                    "contains_codcompeticion": str("codcompeticion" in fragment_lower).lower(),
                    "contains_codgrupo": str("codgrupo" in fragment_lower).lower(),
                    "contains_codtemporada": str("codtemporada" in fragment_lower).lower(),
                    "notes": "Relevant fragment extracted from R2 classification response.",
                })

except Exception as e:
    r3_rows.append({
        "item_type": "error",
        "label_or_text": "",
        "href_or_action": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "contains_primera_federacion": "false",
        "contains_liga_regular": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_codcompeticion": "false",
        "contains_codgrupo": "false",
        "contains_codtemporada": "false",
        "notes": f"RFEF Research R3 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r3_classification_code_links.csv",
    r3_fields,
    r3_rows,
)

print(f"RFEF Research R3 extracted {len(r3_rows)} classification code/link rows.")
# -----------------------------
# RFEF Research Stage R4:
# Test discovered Primera Federación regular group result URLs
# -----------------------------

r4_fields = [
    "group_name",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
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
    "contains_acta",
    "sample_text",
    "notes",
]

r4_rows = []

r4_tests = [
    {
        "group_name": "Primera Federación Fase Regular Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "jornadas": ["1", "38"],
    },
    {
        "group_name": "Primera Federación Fase Regular Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "jornadas": ["1", "38"],
    },
]

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for test in r4_tests:
            for cod_jornada in test["jornadas"]:
                test_url = (
                    "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
                    "?cod_primaria=1000120"
                    f"&CodTemporada={test['cod_temporada']}"
                    f"&CodJornada={cod_jornada}"
                    f"&CodCompeticion={test['cod_competicion']}"
                    f"&CodGrupo={test['cod_grupo']}"
                )

                try:
                    page = browser.new_page(
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        )
                    )

                    response = page.goto(test_url, wait_until="networkidle", timeout=60000)
                    status = response.status if response else ""

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
                    page_html_lower = page_html.lower()

                    safe_name = re.sub(
                        r"[^A-Za-z0-9]+",
                        "_",
                        f"{test['group_name']}_jornada_{cod_jornada}",
                    ).strip("_").lower()

                    html_path = EXPORT_DIR / f"rfef_research_r4_{safe_name}.html"
                    html_path.write_text(page_html[:500000], encoding="utf-8")

                    sample_text = re.sub(r"\s+", " ", page_text[:5000]).strip()

                    r4_rows.append({
                        "group_name": test["group_name"],
                        "cod_temporada": test["cod_temporada"],
                        "cod_competicion": test["cod_competicion"],
                        "cod_grupo": test["cod_grupo"],
                        "cod_jornada": cod_jornada,
                        "test_url": test_url,
                        "http_status": str(status),
                        "page_loaded": "true",
                        "contains_primera_federacion": str(
                            "primera federación" in page_text_lower
                            or "primera federacion" in page_text_lower
                            or "primera federación" in page_html_lower
                            or "primera federacion" in page_html_lower
                        ).lower(),
                        "contains_grupo_1": str(
                            "grupo 1" in page_text_lower
                            or "grupo i" in page_text_lower
                            or "grupo 1" in page_html_lower
                            or "grupo i" in page_html_lower
                        ).lower(),
                        "contains_grupo_2": str(
                            "grupo 2" in page_text_lower
                            or "grupo ii" in page_text_lower
                            or "grupo 2" in page_html_lower
                            or "grupo ii" in page_html_lower
                        ).lower(),
                        "contains_jornada": str(
                            "jornada" in page_text_lower
                            or "jornada" in page_html_lower
                        ).lower(),
                        "contains_local": str(
                            "local" in page_text_lower
                            or "local" in page_html_lower
                        ).lower(),
                        "contains_visitante": str(
                            "visitante" in page_text_lower
                            or "visitante" in page_html_lower
                        ).lower(),
                        "contains_resultado": str(
                            "resultado" in page_text_lower
                            or "resultados" in page_text_lower
                            or "resultado" in page_html_lower
                            or "resultados" in page_html_lower
                        ).lower(),
                        "contains_acta": str(
                            "acta" in page_text_lower
                            or "actas" in page_text_lower
                            or "acta" in page_html_lower
                            or "actas" in page_html_lower
                        ).lower(),
                        "sample_text": sample_text,
                        "notes": "Discovered Primera Federación group code tested through result URL.",
                    })

                    page.close()

                except Exception as e:
                    r4_rows.append({
                        "group_name": test["group_name"],
                        "cod_temporada": test["cod_temporada"],
                        "cod_competicion": test["cod_competicion"],
                        "cod_grupo": test["cod_grupo"],
                        "cod_jornada": cod_jornada,
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
                        "contains_acta": "false",
                        "sample_text": "",
                        "notes": f"R4 URL test failed: {type(e).__name__}: {e}",
                    })

        browser.close()

except Exception as e:
    r4_rows.append({
        "group_name": "stage_error",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
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
        "contains_acta": "false",
        "sample_text": "",
        "notes": f"RFEF Research R4 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r4_discovered_group_url_tests.csv",
    r4_fields,
    r4_rows,
)

print(f"RFEF Research R4 tested {len(r4_rows)} discovered group URLs.")
# -----------------------------
# RFEF Research Stage R5:
# Extract Jornada 1 from Primera Federación Grupo 1 and Grupo 2 into raw fixture rows
# -----------------------------

r5_fields = [
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "source_url",
    "raw_match_index",
    "raw_match_text",
    "home_team_name_source",
    "away_team_name_source",
    "home_score",
    "away_score",
    "fixture_date",
    "extraction_method",
    "data_confidence",
    "notes",
]

r5_rows = []

r5_tests = [
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": "1",
    },
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": "1",
    },
]


def r5_extract_score_line_candidates(page_text):
    """
    RFEF pages are not JSON like LaLiga. This first pass extracts likely match blocks
    from visible text, keeping raw text so we can inspect and refine.
    """
    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in page_text.splitlines()
        if re.sub(r"\s+", " ", line).strip()
    ]

    candidates = []

    for i, line in enumerate(lines):
        line_lower = line.lower()

        # Match lines usually contain a score pattern or fixture/result-related words nearby.
        has_score = bool(re.search(r"\b[0-9]{1,2}\s*[-–]\s*[0-9]{1,2}\b", line))
        has_vs = " - " in line or " v " in line_lower or " vs " in line_lower
        has_fixture_word = (
            "jornada" in line_lower
            or "acta" in line_lower
            or "resultado" in line_lower
            or "finalizado" in line_lower
        )

        if has_score or has_vs or has_fixture_word:
            start = max(i - 3, 0)
            end = min(i + 4, len(lines))
            block = " | ".join(lines[start:end])

            if block not in candidates:
                candidates.append(block)

    return candidates


def r5_try_parse_match_block(block):
    """
    Conservative first-pass parser. If it cannot confidently parse, it leaves fields blank
    and preserves raw_match_text for inspection.
    """
    home_team = ""
    away_team = ""
    home_score = ""
    away_score = ""
    fixture_date = ""

    # Try score formats like Team A 1-0 Team B or Team A 1 - 0 Team B.
    score_match = re.search(
        r"(.+?)\s+([0-9]{1,2})\s*[-–]\s*([0-9]{1,2})\s+(.+)",
        block,
    )

    if score_match:
        left = score_match.group(1).strip(" |-/")
        home_score = score_match.group(2)
        away_score = score_match.group(3)
        right = score_match.group(4).strip(" |-/")

        # Trim noisy prefixes/suffixes.
        home_team = left.split("|")[-1].strip()
        away_team = right.split("|")[0].strip()

    # Try date patterns.
    date_match = re.search(r"\b([0-9]{1,2}/[0-9]{1,2}/[0-9]{4})\b", block)
    if date_match:
        fixture_date = date_match.group(1)

    return home_team, away_team, home_score, away_score, fixture_date


try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for test in r5_tests:
            source_url = (
                "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
                "?cod_primaria=1000120"
                f"&CodTemporada={test['cod_temporada']}"
                f"&CodJornada={test['cod_jornada']}"
                f"&CodCompeticion={test['cod_competicion']}"
                f"&CodGrupo={test['cod_grupo']}"
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

                safe_name = re.sub(
                    r"[^A-Za-z0-9]+",
                    "_",
                    f"{test['competition_group']}_jornada_{test['cod_jornada']}",
                ).strip("_").lower()

                html_path = EXPORT_DIR / f"rfef_research_r5_{safe_name}.html"
                html_path.write_text(page_html[:700000], encoding="utf-8")

                text_path = EXPORT_DIR / f"rfef_research_r5_{safe_name}_text.txt"
                text_path.write_text(page_text[:300000], encoding="utf-8")

                candidates = r5_extract_score_line_candidates(page_text)

                if not candidates:
                    r5_rows.append({
                        "season_id": test["season_id"],
                        "competition_id": test["competition_id"],
                        "competition_name": test["competition_name"],
                        "competition_group": test["competition_group"],
                        "cod_temporada": test["cod_temporada"],
                        "cod_competicion": test["cod_competicion"],
                        "cod_grupo": test["cod_grupo"],
                        "cod_jornada": test["cod_jornada"],
                        "source_url": source_url,
                        "raw_match_index": "",
                        "raw_match_text": "",
                        "home_team_name_source": "",
                        "away_team_name_source": "",
                        "home_score": "",
                        "away_score": "",
                        "fixture_date": "",
                        "extraction_method": "visible_text_candidate_scan",
                        "data_confidence": "failed",
                        "notes": "No candidate match blocks found. Inspect saved text/html.",
                    })

                for index, block in enumerate(candidates):
                    home_team, away_team, home_score, away_score, fixture_date = r5_try_parse_match_block(block)

                    parsed_ok = bool(home_team and away_team and home_score != "" and away_score != "")

                    r5_rows.append({
                        "season_id": test["season_id"],
                        "competition_id": test["competition_id"],
                        "competition_name": test["competition_name"],
                        "competition_group": test["competition_group"],
                        "cod_temporada": test["cod_temporada"],
                        "cod_competicion": test["cod_competicion"],
                        "cod_grupo": test["cod_grupo"],
                        "cod_jornada": test["cod_jornada"],
                        "source_url": source_url,
                        "raw_match_index": str(index),
                        "raw_match_text": block,
                        "home_team_name_source": home_team,
                        "away_team_name_source": away_team,
                        "home_score": home_score,
                        "away_score": away_score,
                        "fixture_date": fixture_date,
                        "extraction_method": "visible_text_candidate_scan",
                        "data_confidence": "medium" if parsed_ok else "needs_review",
                        "notes": "First-pass RFEF visible-text extraction. Raw block retained for parser refinement.",
                    })

                page.close()

            except Exception as e:
                r5_rows.append({
                    "season_id": test["season_id"],
                    "competition_id": test["competition_id"],
                    "competition_name": test["competition_name"],
                    "competition_group": test["competition_group"],
                    "cod_temporada": test["cod_temporada"],
                    "cod_competicion": test["cod_competicion"],
                    "cod_grupo": test["cod_grupo"],
                    "cod_jornada": test["cod_jornada"],
                    "source_url": source_url,
                    "raw_match_index": "",
                    "raw_match_text": "",
                    "home_team_name_source": "",
                    "away_team_name_source": "",
                    "home_score": "",
                    "away_score": "",
                    "fixture_date": "",
                    "extraction_method": "visible_text_candidate_scan",
                    "data_confidence": "failed",
                    "notes": f"R5 extraction failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    r5_rows.append({
        "season_id": "",
        "competition_id": "",
        "competition_name": "",
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "source_url": "",
        "raw_match_index": "",
        "raw_match_text": "",
        "home_team_name_source": "",
        "away_team_name_source": "",
        "home_score": "",
        "away_score": "",
        "fixture_date": "",
        "extraction_method": "visible_text_candidate_scan",
        "data_confidence": "failed",
        "notes": f"RFEF Research R5 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r5_jornada_1_raw_fixture_candidates.csv",
    r5_fields,
    r5_rows,
)

# Validation summary
r5_validation_fields = [
    "check_name",
    "result",
    "details",
]

r5_group_1_rows = [
    row for row in r5_rows
    if row.get("competition_group") == "Grupo 1"
]

r5_group_2_rows = [
    row for row in r5_rows
    if row.get("competition_group") == "Grupo 2"
]

r5_medium_rows = [
    row for row in r5_rows
    if row.get("data_confidence") == "medium"
]

r5_validation_rows = [
    {
        "check_name": "total_candidate_rows",
        "result": str(len(r5_rows)),
        "details": "Expected roughly 20 candidate rows if both groups expose 10 matches each.",
    },
    {
        "check_name": "grupo_1_candidate_rows",
        "result": str(len(r5_group_1_rows)),
        "details": "Expected roughly 10.",
    },
    {
        "check_name": "grupo_2_candidate_rows",
        "result": str(len(r5_group_2_rows)),
        "details": "Expected roughly 10.",
    },
    {
        "check_name": "medium_confidence_parsed_rows",
        "result": str(len(r5_medium_rows)),
        "details": "Rows where a basic home/away/score parse succeeded.",
    },
]

write_csv(
    "rfef_research_r5_validation_summary.csv",
    r5_validation_fields,
    r5_validation_rows,
)

print(f"RFEF Research R5 extracted {len(r5_rows)} raw candidate rows.")
# -----------------------------
# RFEF Research Stage R6:
# Parse saved R5 Jornada 1 page text into structured fixture rows
# -----------------------------

r6_fields = [
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "fixture_index",
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

r6_rows = []

r6_sources = [
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": "1",
        "text_file": "rfef_research_r5_grupo_1_jornada_1_text.txt",
    },
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": "1",
        "text_file": "rfef_research_r5_grupo_2_jornada_1_text.txt",
    },
]


def r6_is_date(value):
    return bool(re.match(r"^[0-9]{2}-[0-9]{2}-[0-9]{4}$", value.strip()))


def r6_is_time(value):
    return bool(re.match(r"^[0-9]{1,2}:[0-9]{2}$", value.strip()))


def r6_is_score_marker(value):
    value = value.strip()
    return bool(
        value == "-"
        or re.match(r"^[0-9]{1,2}\s*-\s*[0-9]{1,2}$", value)
        or re.match(r"^[0-9]{1,2}\s*-$", value)
        or re.match(r"^-\s*[0-9]{1,2}$", value)
    )


def r6_parse_score(value):
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


def r6_clean_lines(text):
    lines = []

    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()

        if not cleaned:
            continue

        # Remove obvious page furniture.
        skip_values = {
            "Competiciones",
            "Acciones",
            "Calendario Clasificaciones y Resultados Búsqueda por competición",
            "Filtro de búsqueda Avanzado",
            "Siguiente",
            "Anterior",
            "Provisional Definitivo",
            "RESULTADOS",
            "Calendario Clasificación Tabla Cruzada Goleadores Porteros",
        }

        if cleaned in skip_values:
            continue

        if cleaned.startswith("Temporada "):
            continue

        if cleaned.startswith("Campeonato Nacional de Liga de Primera Federación"):
            continue

        if cleaned.startswith("Jornada "):
            continue

        lines.append(cleaned)

    return lines


def r6_parse_fixtures_from_lines(lines):
    fixtures = []
    i = 0

    while i < len(lines):
        # Look for pattern:
        # home_team, score_marker, date, time, away_team, venue, Árbitro:, referee
        if i + 5 < len(lines):
            home = lines[i]
            score_marker = lines[i + 1]
            date_value = lines[i + 2]
            time_value = lines[i + 3]
            away = lines[i + 4]
            venue = lines[i + 5]

            if (
                r6_is_score_marker(score_marker)
                and r6_is_date(date_value)
                and r6_is_time(time_value)
                and home.lower() != "árbitro:"
                and away.lower() != "árbitro:"
            ):
                home_score, away_score = r6_parse_score(score_marker)

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
                    "fixture_date": date_value,
                    "kickoff_time_local": time_value,
                    "venue_name_source": venue,
                    "referee": referee,
                    "raw_sequence": " | ".join(lines[i:i + consumed]),
                    "data_confidence": "high" if home and away and date_value and time_value else "needs_review",
                    "notes": "Parsed from RFEF saved visible text sequence.",
                })

                i += consumed
                continue

        i += 1

    return fixtures


try:
    for source in r6_sources:
        text_path = EXPORT_DIR / source["text_file"]

        if not text_path.exists():
            r6_rows.append({
                "season_id": source["season_id"],
                "competition_id": source["competition_id"],
                "competition_name": source["competition_name"],
                "competition_group": source["competition_group"],
                "cod_temporada": source["cod_temporada"],
                "cod_competicion": source["cod_competicion"],
                "cod_grupo": source["cod_grupo"],
                "cod_jornada": source["cod_jornada"],
                "fixture_index": "",
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
                "notes": f"Missing expected text file: {source['text_file']}",
            })
            continue

        text = text_path.read_text(encoding="utf-8", errors="ignore")
        lines = r6_clean_lines(text)
        fixtures = r6_parse_fixtures_from_lines(lines)

        for fixture_index, fixture in enumerate(fixtures):
            row = {
                "season_id": source["season_id"],
                "competition_id": source["competition_id"],
                "competition_name": source["competition_name"],
                "competition_group": source["competition_group"],
                "cod_temporada": source["cod_temporada"],
                "cod_competicion": source["cod_competicion"],
                "cod_grupo": source["cod_grupo"],
                "cod_jornada": source["cod_jornada"],
                "fixture_index": str(fixture_index),
            }
            row.update(fixture)
            r6_rows.append(row)

except Exception as e:
    r6_rows.append({
        "season_id": "",
        "competition_id": "",
        "competition_name": "",
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "fixture_index": "",
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
        "notes": f"RFEF Research R6 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r6_jornada_1_parsed_fixtures.csv",
    r6_fields,
    r6_rows,
)

# Validation
r6_validation_fields = [
    "check_name",
    "result",
    "details",
]

r6_group_1_rows = [
    row for row in r6_rows
    if row.get("competition_group") == "Grupo 1"
]

r6_group_2_rows = [
    row for row in r6_rows
    if row.get("competition_group") == "Grupo 2"
]

r6_high_rows = [
    row for row in r6_rows
    if row.get("data_confidence") == "high"
]

r6_validation_rows = [
    {
        "check_name": "total_fixture_rows",
        "result": str(len(r6_rows)),
        "details": "Expected 20.",
    },
    {
        "check_name": "grupo_1_fixture_rows",
        "result": str(len(r6_group_1_rows)),
        "details": "Expected 10.",
    },
    {
        "check_name": "grupo_2_fixture_rows",
        "result": str(len(r6_group_2_rows)),
        "details": "Expected 10.",
    },
    {
        "check_name": "high_confidence_rows",
        "result": str(len(r6_high_rows)),
        "details": "Expected 20 if all fixtures parsed.",
    },
]

write_csv(
    "rfef_research_r6_validation_summary.csv",
    r6_validation_fields,
    r6_validation_rows,
)

print(f"RFEF Research R6 parsed {len(r6_rows)} fixture rows.")
# -----------------------------
# RFEF Research Stage R7:
# Extract all 38 jornadas for Primera Federación Grupo 1 and Grupo 2
# -----------------------------

r7_fields = [
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

r7_rows = []

r7_groups = [
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
    },
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
    },
]


def r7_is_date(value):
    return bool(re.match(r"^[0-9]{2}-[0-9]{2}-[0-9]{4}$", value.strip()))


def r7_is_time(value):
    return bool(re.match(r"^[0-9]{1,2}:[0-9]{2}$", value.strip()))


def r7_is_score_marker(value):
    value = value.strip()
    return bool(
        value == "-"
        or re.match(r"^[0-9]{1,2}\s*-\s*[0-9]{1,2}$", value)
        or re.match(r"^[0-9]{1,2}\s*-$", value)
        or re.match(r"^-\s*[0-9]{1,2}$", value)
    )


def r7_parse_score(value):
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


def r7_clean_lines(text):
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


def r7_parse_fixtures_from_lines(lines):
    fixtures = []
    i = 0

    while i < len(lines):
        # Pattern:
        # home_team, score_marker, date, time, away_team, venue, optional Árbitro:, optional referee
        if i + 5 < len(lines):
            home = lines[i]
            score_marker = lines[i + 1]
            date_value = lines[i + 2]
            time_value = lines[i + 3]
            away = lines[i + 4]
            venue = lines[i + 5]

            if (
                r7_is_score_marker(score_marker)
                and r7_is_date(date_value)
                and r7_is_time(time_value)
                and home.lower() != "árbitro:"
                and away.lower() != "árbitro:"
            ):
                home_score, away_score = r7_parse_score(score_marker)

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
                    "fixture_date": date_value,
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


try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for group in r7_groups:
            for jornada in range(1, 39):
                cod_jornada = str(jornada)

                source_url = (
                    "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
                    "?cod_primaria=1000120"
                    f"&CodTemporada={group['cod_temporada']}"
                    f"&CodJornada={cod_jornada}"
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

                    page_text = page.inner_text("body")
                    page_html = page.content()

                    safe_name = re.sub(
                        r"[^A-Za-z0-9]+",
                        "_",
                        f"{group['competition_group']}_jornada_{cod_jornada}",
                    ).strip("_").lower()

                    html_path = EXPORT_DIR / f"rfef_research_r7_{safe_name}.html"
                    html_path.write_text(page_html[:700000], encoding="utf-8")

                    text_path = EXPORT_DIR / f"rfef_research_r7_{safe_name}_text.txt"
                    text_path.write_text(page_text[:300000], encoding="utf-8")

                    lines = r7_clean_lines(page_text)
                    fixtures = r7_parse_fixtures_from_lines(lines)

                    if not fixtures:
                        r7_rows.append({
                            "season_id": group["season_id"],
                            "competition_id": group["competition_id"],
                            "competition_name": group["competition_name"],
                            "competition_group": group["competition_group"],
                            "cod_temporada": group["cod_temporada"],
                            "cod_competicion": group["cod_competicion"],
                            "cod_grupo": group["cod_grupo"],
                            "cod_jornada": cod_jornada,
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
                        r7_rows.append({
                            "season_id": group["season_id"],
                            "competition_id": group["competition_id"],
                            "competition_name": group["competition_name"],
                            "competition_group": group["competition_group"],
                            "cod_temporada": group["cod_temporada"],
                            "cod_competicion": group["cod_competicion"],
                            "cod_grupo": group["cod_grupo"],
                            "cod_jornada": cod_jornada,
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
                        })

                    page.close()

                except Exception as e:
                    r7_rows.append({
                        "season_id": group["season_id"],
                        "competition_id": group["competition_id"],
                        "competition_name": group["competition_name"],
                        "competition_group": group["competition_group"],
                        "cod_temporada": group["cod_temporada"],
                        "cod_competicion": group["cod_competicion"],
                        "cod_grupo": group["cod_grupo"],
                        "cod_jornada": cod_jornada,
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
                        "notes": f"R7 extraction failed: {type(e).__name__}: {e}",
                    })

        browser.close()

except Exception as e:
    r7_rows.append({
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
        "notes": f"RFEF Research R7 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r7_all_jornadas_raw_fixtures.csv",
    r7_fields,
    r7_rows,
)

# Validation
r7_validation_fields = [
    "check_name",
    "result",
    "details",
]

r7_group_1_rows = [
    row for row in r7_rows
    if row.get("competition_group") == "Grupo 1"
    and row.get("data_confidence") != "failed"
]

r7_group_2_rows = [
    row for row in r7_rows
    if row.get("competition_group") == "Grupo 2"
    and row.get("data_confidence") != "failed"
]

r7_failed_rows = [
    row for row in r7_rows
    if row.get("data_confidence") == "failed"
]

r7_high_rows = [
    row for row in r7_rows
    if row.get("data_confidence") == "high"
]

r7_rows_by_group_jornada = {}

for row in r7_rows:
    key = f"{row.get('competition_group')}|J{row.get('cod_jornada')}"
    if row.get("data_confidence") != "failed":
        r7_rows_by_group_jornada[key] = r7_rows_by_group_jornada.get(key, 0) + 1

unexpected_jornada_counts = [
    f"{key}={count}"
    for key, count in sorted(r7_rows_by_group_jornada.items())
    if count != 10
]

r7_validation_rows = [
    {
        "check_name": "total_fixture_rows_non_failed",
        "result": str(len([row for row in r7_rows if row.get("data_confidence") != "failed"])),
        "details": "Expected 760: 38 jornadas x 10 fixtures x 2 groups.",
    },
    {
        "check_name": "grupo_1_fixture_rows_non_failed",
        "result": str(len(r7_group_1_rows)),
        "details": "Expected 380.",
    },
    {
        "check_name": "grupo_2_fixture_rows_non_failed",
        "result": str(len(r7_group_2_rows)),
        "details": "Expected 380.",
    },
    {
        "check_name": "high_confidence_rows",
        "result": str(len(r7_high_rows)),
        "details": "Expected 760 if all fixtures parsed cleanly.",
    },
    {
        "check_name": "failed_rows",
        "result": str(len(r7_failed_rows)),
        "details": "Expected 0.",
    },
    {
        "check_name": "unexpected_jornada_counts",
        "result": str(len(unexpected_jornada_counts)),
        "details": "|".join(unexpected_jornada_counts[:100]),
    },
]

write_csv(
    "rfef_research_r7_validation_summary.csv",
    r7_validation_fields,
    r7_validation_rows,
)

print(f"RFEF Research R7 produced {len(r7_rows)} rows.")
# -----------------------------
# RFEF Research Stage R8:
# Diagnose why Grupo 1 Jornada 23+ and Grupo 2 pages are not parsing
# -----------------------------

r8_fields = [
    "test_name",
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "source_url",
    "page_loaded",
    "page_text_length",
    "contains_primera_federacion",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_jornada",
    "contains_resultado",
    "contains_no_data",
    "candidate_sequence_count",
    "parsed_fixture_count",
    "first_80_lines",
    "notes",
]

r8_rows = []

r8_tests = [
    {
        "test_name": "Grupo 1 Jornada 22 working comparison",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": "22",
    },
    {
        "test_name": "Grupo 1 Jornada 23 failing comparison",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": "23",
    },
    {
        "test_name": "Grupo 2 Jornada 1 failing comparison",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": "1",
    },
    {
        "test_name": "Grupo 2 Jornada 22 comparison",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": "22",
    },
]


def r8_clean_lines(text):
    lines = []

    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if cleaned:
            lines.append(cleaned)

    return lines


def r8_is_date(value):
    return bool(re.match(r"^[0-9]{2}-[0-9]{2}-[0-9]{4}$", value.strip()))


def r8_is_time(value):
    return bool(re.match(r"^[0-9]{1,2}:[0-9]{2}$", value.strip()))


def r8_is_score_marker(value):
    value = value.strip()
    return bool(
        value == "-"
        or re.match(r"^[0-9]{1,2}\s*-\s*[0-9]{1,2}$", value)
        or re.match(r"^[0-9]{1,2}\s*-$", value)
        or re.match(r"^-\s*[0-9]{1,2}$", value)
    )


def r8_count_candidate_sequences(lines):
    count = 0

    for i in range(len(lines)):
        if i + 5 < len(lines):
            score_marker = lines[i + 1]
            date_value = lines[i + 2]
            time_value = lines[i + 3]

            if (
                r8_is_score_marker(score_marker)
                and r8_is_date(date_value)
                and r8_is_time(time_value)
            ):
                count += 1

    return count


try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for test in r8_tests:
            source_url = (
                "https://resultados.rfef.es/pnfg/NPcd/NFG_CmpJornada"
                "?cod_primaria=1000120"
                f"&CodTemporada={test['cod_temporada']}"
                f"&CodJornada={test['cod_jornada']}"
                f"&CodCompeticion={test['cod_competicion']}"
                f"&CodGrupo={test['cod_grupo']}"
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

                page_text = page.inner_text("body")
                page_html = page.content()
                page_text_lower = page_text.lower()
                page_html_lower = page_html.lower()

                safe_name = re.sub(
                    r"[^A-Za-z0-9]+",
                    "_",
                    test["test_name"],
                ).strip("_").lower()

                html_path = EXPORT_DIR / f"rfef_research_r8_{safe_name}.html"
                html_path.write_text(page_html[:700000], encoding="utf-8")

                text_path = EXPORT_DIR / f"rfef_research_r8_{safe_name}_text.txt"
                text_path.write_text(page_text[:300000], encoding="utf-8")

                lines = r8_clean_lines(page_text)

                first_80_lines = " | ".join(lines[:80])
                candidate_sequence_count = r8_count_candidate_sequences(lines)

                contains_no_data = (
                    "no hay datos" in page_text_lower
                    or "sin datos" in page_text_lower
                    or "no existen" in page_text_lower
                    or "no se encontraron" in page_text_lower
                    or "no se han encontrado" in page_text_lower
                )

                r8_rows.append({
                    "test_name": test["test_name"],
                    "competition_group": test["competition_group"],
                    "cod_temporada": test["cod_temporada"],
                    "cod_competicion": test["cod_competicion"],
                    "cod_grupo": test["cod_grupo"],
                    "cod_jornada": test["cod_jornada"],
                    "source_url": source_url,
                    "page_loaded": "true",
                    "page_text_length": str(len(page_text)),
                    "contains_primera_federacion": str(
                        "primera federación" in page_text_lower
                        or "primera federacion" in page_text_lower
                        or "primera federación" in page_html_lower
                        or "primera federacion" in page_html_lower
                    ).lower(),
                    "contains_grupo_1": str(
                        "grupo 1" in page_text_lower
                        or "grupo i" in page_text_lower
                        or "grupo 1" in page_html_lower
                        or "grupo i" in page_html_lower
                    ).lower(),
                    "contains_grupo_2": str(
                        "grupo 2" in page_text_lower
                        or "grupo ii" in page_text_lower
                        or "grupo 2" in page_html_lower
                        or "grupo ii" in page_html_lower
                    ).lower(),
                    "contains_jornada": str("jornada" in page_text_lower or "jornada" in page_html_lower).lower(),
                    "contains_resultado": str(
                        "resultado" in page_text_lower
                        or "resultados" in page_text_lower
                        or "resultado" in page_html_lower
                        or "resultados" in page_html_lower
                    ).lower(),
                    "contains_no_data": str(contains_no_data).lower(),
                    "candidate_sequence_count": str(candidate_sequence_count),
                    "parsed_fixture_count": str(candidate_sequence_count),
                    "first_80_lines": first_80_lines[:5000],
                    "notes": "Diagnostic comparison of working and failing RFEF pages. Full text/html saved.",
                })

                page.close()

            except Exception as e:
                r8_rows.append({
                    "test_name": test["test_name"],
                    "competition_group": test["competition_group"],
                    "cod_temporada": test["cod_temporada"],
                    "cod_competicion": test["cod_competicion"],
                    "cod_grupo": test["cod_grupo"],
                    "cod_jornada": test["cod_jornada"],
                    "source_url": source_url,
                    "page_loaded": "false",
                    "page_text_length": "0",
                    "contains_primera_federacion": "false",
                    "contains_grupo_1": "false",
                    "contains_grupo_2": "false",
                    "contains_jornada": "false",
                    "contains_resultado": "false",
                    "contains_no_data": "false",
                    "candidate_sequence_count": "0",
                    "parsed_fixture_count": "0",
                    "first_80_lines": "",
                    "notes": f"R8 diagnostic failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    r8_rows.append({
        "test_name": "stage_error",
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "source_url": "",
        "page_loaded": "false",
        "page_text_length": "0",
        "contains_primera_federacion": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_jornada": "false",
        "contains_resultado": "false",
        "contains_no_data": "false",
        "candidate_sequence_count": "0",
        "parsed_fixture_count": "0",
        "first_80_lines": "",
        "notes": f"RFEF Research R8 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r8_failed_page_diagnostics.csv",
    r8_fields,
    r8_rows,
)

print(f"RFEF Research R8 produced {len(r8_rows)} diagnostic rows.")
# -----------------------------
# RFEF Research Stage R9:
# Extract exact jornada/calendar/result actions from R2 classification response
# -----------------------------

r9_fields = [
    "item_type",
    "label_or_text",
    "href_or_action",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "contains_primera_federacion",
    "contains_fase_regular",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_calendario",
    "contains_jornada",
    "contains_resultado",
    "route_hint",
    "notes",
]

r9_rows = []


def r9_extract_code(text, code_name):
    patterns = {
        "cod_temporada": [
            r"CodTemporada=([0-9]+)",
            r"codtemporada=([0-9]+)",
            r"CodTemporada['\" ]*[:=]['\" ]*([0-9]+)",
            r"codtemporada['\" ]*[:=]['\" ]*([0-9]+)",
            r"CodTemporada\\?['\" ]*[:,]\\?['\" ]*([0-9]+)",
        ],
        "cod_competicion": [
            r"CodCompeticion=([0-9]+)",
            r"codcompeticion=([0-9]+)",
            r"CodCompeticion['\" ]*[:=]['\" ]*([0-9]+)",
            r"codcompeticion['\" ]*[:=]['\" ]*([0-9]+)",
            r"CodCompeticion\\?['\" ]*[:,]\\?['\" ]*([0-9]+)",
        ],
        "cod_grupo": [
            r"CodGrupo=([0-9]+)",
            r"codgrupo=([0-9]+)",
            r"CodGrupo['\" ]*[:=]['\" ]*([0-9]+)",
            r"codgrupo['\" ]*[:=]['\" ]*([0-9]+)",
            r"CodGrupo\\?['\" ]*[:,]\\?['\" ]*([0-9]+)",
        ],
        "cod_jornada": [
            r"CodJornada=([0-9]+)",
            r"codjornada=([0-9]+)",
            r"CodJornada['\" ]*[:=]['\" ]*([0-9]+)",
            r"codjornada['\" ]*[:=]['\" ]*([0-9]+)",
            r"CodJornada\\?['\" ]*[:,]\\?['\" ]*([0-9]+)",
        ],
    }

    for pattern in patterns[code_name]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)

    return ""


def r9_flags(text):
    lower = text.lower()

    return {
        "contains_primera_federacion": str(
            "primera federación" in lower
            or "primera federacion" in lower
            or "primera federaci" in lower
        ).lower(),
        "contains_fase_regular": str(
            "fase regular" in lower
            or "liga regular" in lower
        ).lower(),
        "contains_grupo_1": str(
            "grupo 1" in lower
            or "grupo i" in lower
        ).lower(),
        "contains_grupo_2": str(
            "grupo 2" in lower
            or "grupo ii" in lower
        ).lower(),
        "contains_calendario": str("calendario" in lower).lower(),
        "contains_jornada": str("jornada" in lower).lower(),
        "contains_resultado": str(
            "resultado" in lower
            or "resultados" in lower
        ).lower(),
    }


def r9_route_hint(text):
    lower = text.lower()

    hints = []

    for token in [
        "nfg_cmpjornada",
        "nfg_viscalendario_vis",
        "nfg_viscalendario",
        "nfg_visclasificacion",
        "nfg_cmpacta",
        "nfg_visacta",
        "nfg_cmp",
        "jornada",
        "calendario",
        "resultados",
    ]:
        if token in lower:
            hints.append(token)

    return "|".join(hints)


try:
    response_file = EXPORT_DIR / "rfef_research_r2_football_masculino_femenino_clasificacion_exact_button.html"

    if not response_file.exists():
        r9_rows.append({
            "item_type": "error",
            "label_or_text": "",
            "href_or_action": "",
            "cod_temporada": "",
            "cod_competicion": "",
            "cod_grupo": "",
            "cod_jornada": "",
            "contains_primera_federacion": "false",
            "contains_fase_regular": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_calendario": "false",
            "contains_jornada": "false",
            "contains_resultado": "false",
            "route_hint": "",
            "notes": "Expected R2 classification response HTML file not found. Run R2 first.",
        })

    else:
        html = response_file.read_text(encoding="utf-8", errors="ignore")

        plain_text = re.sub(r"<[^>]+>", " ", html)
        plain_text = re.sub(r"\s+", " ", plain_text).strip()

        (EXPORT_DIR / "rfef_research_r9_classification_plain_text.txt").write_text(
            plain_text[:700000],
            encoding="utf-8",
        )

        # 1. Links
        link_matches = re.findall(
            r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>',
            html,
            re.IGNORECASE | re.DOTALL,
        )

        for href, raw_text in link_matches:
            label = re.sub(r"<[^>]+>", " ", raw_text)
            label = re.sub(r"\s+", " ", label).strip()
            combined = f"{label} {href}"

            lower = combined.lower()

            if (
                "primera federaci" in lower
                or "fase regular" in lower
                or "liga regular" in lower
                or "grupo 1" in lower
                or "grupo 2" in lower
                or "grupo i" in lower
                or "grupo ii" in lower
                or "calendario" in lower
                or "jornada" in lower
                or "resultado" in lower
                or "codcompeticion" in lower
                or "codgrupo" in lower
                or "codtemporada" in lower
                or "nfg_" in lower
            ):
                flags = r9_flags(combined)

                r9_rows.append({
                    "item_type": "link",
                    "label_or_text": label[:2000],
                    "href_or_action": href[:3000],
                    "cod_temporada": r9_extract_code(combined, "cod_temporada"),
                    "cod_competicion": r9_extract_code(combined, "cod_competicion"),
                    "cod_grupo": r9_extract_code(combined, "cod_grupo"),
                    "cod_jornada": r9_extract_code(combined, "cod_jornada"),
                    **flags,
                    "route_hint": r9_route_hint(combined),
                    "notes": "Link extracted from R2 classification response.",
                })

        # 2. Onclicks and data/action attributes
        attr_matches = []

        for attr_name in ["onclick", "data-url", "data-href", "href", "action"]:
            attr_matches.extend([
                (attr_name, value)
                for value in re.findall(
                    rf'{attr_name}=["\']([^"\']+)["\']',
                    html,
                    re.IGNORECASE | re.DOTALL,
                )
            ])

        for attr_name, value in attr_matches:
            combined = value
            lower = combined.lower()

            if (
                "primera federaci" in lower
                or "fase regular" in lower
                or "liga regular" in lower
                or "grupo 1" in lower
                or "grupo 2" in lower
                or "grupo i" in lower
                or "grupo ii" in lower
                or "calendario" in lower
                or "jornada" in lower
                or "resultado" in lower
                or "codcompeticion" in lower
                or "codgrupo" in lower
                or "codtemporada" in lower
                or "nfg_" in lower
            ):
                flags = r9_flags(combined)

                r9_rows.append({
                    "item_type": f"attribute:{attr_name}",
                    "label_or_text": "",
                    "href_or_action": value[:3000],
                    "cod_temporada": r9_extract_code(combined, "cod_temporada"),
                    "cod_competicion": r9_extract_code(combined, "cod_competicion"),
                    "cod_grupo": r9_extract_code(combined, "cod_grupo"),
                    "cod_jornada": r9_extract_code(combined, "cod_jornada"),
                    **flags,
                    "route_hint": r9_route_hint(combined),
                    "notes": f"{attr_name} attribute extracted from R2 classification response.",
                })

        # 3. Context windows around the two discovered group codes and route names.
        search_terms = [
            "23289295",
            "23289296",
            "23289297",
            "CodCompeticion",
            "CodGrupo",
            "CodTemporada",
            "NFG_CmpJornada",
            "NFG_VisCalendario",
            "Calendario",
            "Jornada",
            "Grupo 1",
            "Grupo 2",
            "Fase Regular",
            "Primera Federación",
        ]

        for term in search_terms:
            lower_html = html.lower()
            lower_term = term.lower()
            start = 0

            while True:
                index = lower_html.find(lower_term, start)

                if index == -1:
                    break

                context_start = max(index - 1200, 0)
                context_end = min(index + 1800, len(html))
                fragment = html[context_start:context_end]

                label = re.sub(r"<[^>]+>", " ", fragment)
                label = re.sub(r"\s+", " ", label).strip()

                flags = r9_flags(fragment)

                r9_rows.append({
                    "item_type": "context_window",
                    "label_or_text": label[:2500],
                    "href_or_action": fragment[:3500],
                    "cod_temporada": r9_extract_code(fragment, "cod_temporada"),
                    "cod_competicion": r9_extract_code(fragment, "cod_competicion"),
                    "cod_grupo": r9_extract_code(fragment, "cod_grupo"),
                    "cod_jornada": r9_extract_code(fragment, "cod_jornada"),
                    **flags,
                    "route_hint": r9_route_hint(fragment),
                    "notes": f"Context window around term: {term}",
                })

                start = index + len(lower_term)

        # 4. Deduplicate rough exact duplicates.
        seen = set()
        deduped = []

        for row in r9_rows:
            key = (
                row.get("item_type", ""),
                row.get("href_or_action", "")[:500],
                row.get("cod_temporada", ""),
                row.get("cod_competicion", ""),
                row.get("cod_grupo", ""),
                row.get("cod_jornada", ""),
            )

            if key in seen:
                continue

            seen.add(key)
            deduped.append(row)

        r9_rows = deduped

except Exception as e:
    r9_rows.append({
        "item_type": "error",
        "label_or_text": "",
        "href_or_action": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "contains_primera_federacion": "false",
        "contains_fase_regular": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_calendario": "false",
        "contains_jornada": "false",
        "contains_resultado": "false",
        "route_hint": "",
        "notes": f"RFEF Research R9 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r9_exact_jornada_calendar_actions.csv",
    r9_fields,
    r9_rows,
)

print(f"RFEF Research R9 extracted {len(r9_rows)} exact jornada/calendar action candidates.")
# -----------------------------
# RFEF Research Stage R10:
# Test exact R9 calendar/result routes on both RFEF hosts
# -----------------------------

r10_fields = [
    "test_name",
    "host",
    "route_type",
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "test_url",
    "http_status",
    "page_loaded",
    "page_text_length",
    "contains_primera_federacion",
    "contains_jornada",
    "contains_calendario",
    "contains_resultado",
    "candidate_sequence_count",
    "first_100_lines",
    "notes",
]

r10_rows = []


def r10_clean_lines(text):
    lines = []
    for line in text.splitlines():
        cleaned = re.sub(r"\s+", " ", line).strip()
        if cleaned:
            lines.append(cleaned)
    return lines


def r10_is_date(value):
    return bool(re.match(r"^[0-9]{2}-[0-9]{2}-[0-9]{4}$", value.strip()))


def r10_is_time(value):
    return bool(re.match(r"^[0-9]{1,2}:[0-9]{2}$", value.strip()))


def r10_is_score_marker(value):
    value = value.strip()
    return bool(
        value == "-"
        or re.match(r"^[0-9]{1,2}\s*-\s*[0-9]{1,2}$", value)
        or re.match(r"^[0-9]{1,2}\s*-$", value)
        or re.match(r"^-\s*[0-9]{1,2}$", value)
    )


def r10_count_candidate_sequences(lines):
    count = 0

    for i in range(len(lines)):
        if i + 5 < len(lines):
            score_marker = lines[i + 1]
            date_value = lines[i + 2]
            time_value = lines[i + 3]

            if (
                r10_is_score_marker(score_marker)
                and r10_is_date(date_value)
                and r10_is_time(time_value)
            ):
                count += 1

    return count


r10_routes = [
    {
        "route_type": "Calendario",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": "38",
        "path": "/pnfg/NPcd/NFG_VisCalendario_Vis?cod_primaria=1000120&codtemporada=21&codJornada=38&codcompeticion=23289295&codgrupo=23289296",
    },
    {
        "route_type": "Resultados",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
        "cod_jornada": "38",
        "path": "/pnfg/NPcd/NFG_CmpJornada?cod_primaria=1000120&CodTemporada=21&CodJornada=38&CodCompeticion=23289295&CodGrupo=23289296",
    },
    {
        "route_type": "Calendario",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": "38",
        "path": "/pnfg/NPcd/NFG_VisCalendario_Vis?cod_primaria=1000120&codtemporada=21&codJornada=38&codcompeticion=23289295&codgrupo=23289297",
    },
    {
        "route_type": "Resultados",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
        "cod_jornada": "38",
        "path": "/pnfg/NPcd/NFG_CmpJornada?cod_primaria=1000120&CodTemporada=21&CodJornada=38&CodCompeticion=23289295&CodGrupo=23289297",
    },
]

r10_hosts = [
    "https://resultados.rfef.es",
    "https://marcadores.rfef.es",
]

try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for host in r10_hosts:
            for route in r10_routes:
                test_url = host + route["path"]
                test_name = f"{route['competition_group']} {route['route_type']} on {host}"

                try:
                    page = browser.new_page(
                        user_agent=(
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        )
                    )

                    response = page.goto(test_url, wait_until="networkidle", timeout=60000)
                    status = response.status if response else ""

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

                    page_text = page.inner_text("body")
                    page_html = page.content()

                    page_text_lower = page_text.lower()
                    page_html_lower = page_html.lower()

                    safe_name = re.sub(
                        r"[^A-Za-z0-9]+",
                        "_",
                        test_name,
                    ).strip("_").lower()

                    html_path = EXPORT_DIR / f"rfef_research_r10_{safe_name}.html"
                    html_path.write_text(page_html[:800000], encoding="utf-8")

                    text_path = EXPORT_DIR / f"rfef_research_r10_{safe_name}_text.txt"
                    text_path.write_text(page_text[:500000], encoding="utf-8")

                    lines = r10_clean_lines(page_text)
                    candidate_sequence_count = r10_count_candidate_sequences(lines)
                    first_100_lines = " | ".join(lines[:100])

                    r10_rows.append({
                        "test_name": test_name,
                        "host": host,
                        "route_type": route["route_type"],
                        "competition_group": route["competition_group"],
                        "cod_temporada": route["cod_temporada"],
                        "cod_competicion": route["cod_competicion"],
                        "cod_grupo": route["cod_grupo"],
                        "cod_jornada": route["cod_jornada"],
                        "test_url": test_url,
                        "http_status": str(status),
                        "page_loaded": "true",
                        "page_text_length": str(len(page_text)),
                        "contains_primera_federacion": str(
                            "primera federación" in page_text_lower
                            or "primera federacion" in page_text_lower
                            or "primera federación" in page_html_lower
                            or "primera federacion" in page_html_lower
                        ).lower(),
                        "contains_jornada": str(
                            "jornada" in page_text_lower
                            or "jornada" in page_html_lower
                        ).lower(),
                        "contains_calendario": str(
                            "calendario" in page_text_lower
                            or "calendario" in page_html_lower
                        ).lower(),
                        "contains_resultado": str(
                            "resultado" in page_text_lower
                            or "resultados" in page_text_lower
                            or "resultado" in page_html_lower
                            or "resultados" in page_html_lower
                        ).lower(),
                        "candidate_sequence_count": str(candidate_sequence_count),
                        "first_100_lines": first_100_lines[:6000],
                        "notes": "Exact R9 route tested on both RFEF hosts.",
                    })

                    page.close()

                except Exception as e:
                    r10_rows.append({
                        "test_name": test_name,
                        "host": host,
                        "route_type": route["route_type"],
                        "competition_group": route["competition_group"],
                        "cod_temporada": route["cod_temporada"],
                        "cod_competicion": route["cod_competicion"],
                        "cod_grupo": route["cod_grupo"],
                        "cod_jornada": route["cod_jornada"],
                        "test_url": test_url,
                        "http_status": "",
                        "page_loaded": "false",
                        "page_text_length": "0",
                        "contains_primera_federacion": "false",
                        "contains_jornada": "false",
                        "contains_calendario": "false",
                        "contains_resultado": "false",
                        "candidate_sequence_count": "0",
                        "first_100_lines": "",
                        "notes": f"R10 exact route test failed: {type(e).__name__}: {e}",
                    })

        browser.close()

except Exception as e:
    r10_rows.append({
        "test_name": "stage_error",
        "host": "",
        "route_type": "",
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "test_url": "",
        "http_status": "",
        "page_loaded": "false",
        "page_text_length": "0",
        "contains_primera_federacion": "false",
        "contains_jornada": "false",
        "contains_calendario": "false",
        "contains_resultado": "false",
        "candidate_sequence_count": "0",
        "first_100_lines": "",
        "notes": f"RFEF Research R10 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r10_exact_route_host_tests.csv",
    r10_fields,
    r10_rows,
)

print(f"RFEF Research R10 tested {len(r10_rows)} exact route/host combinations.")
# -----------------------------
# RFEF Research Stage R11:
# Fetch and parse full Calendario pages for Primera Federación Grupo 1 and Grupo 2
# -----------------------------

r11_fields = [
    "season_id",
    "competition_id",
    "competition_name",
    "competition_group",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "source_url",
    "fixture_index",
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

r11_rows = []

r11_groups = [
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 1",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289296",
    },
    {
        "season_id": "2025-26",
        "competition_id": "PRIMERA_FEDERACION",
        "competition_name": "Primera Federación",
        "competition_group": "Grupo 2",
        "cod_temporada": "21",
        "cod_competicion": "23289295",
        "cod_grupo": "23289297",
    },
]


def r11_is_date(value):
    return bool(re.match(r"^[0-9]{2}-[0-9]{2}-[0-9]{4}$", value.strip()))


def r11_is_time(value):
    return bool(re.match(r"^[0-9]{1,2}:[0-9]{2}$", value.strip()))


def r11_is_score_marker(value):
    value = value.strip()
    return bool(
        value == "-"
        or re.match(r"^[0-9]{1,2}\s*-\s*[0-9]{1,2}$", value)
        or re.match(r"^[0-9]{1,2}\s*-$", value)
        or re.match(r"^-\s*[0-9]{1,2}$", value)
    )


def r11_parse_score(value):
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


def r11_clean_lines(text):
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


def r11_parse_fixtures_from_lines(lines):
    fixtures = []
    i = 0

    while i < len(lines):
        # Same visible sequence as R6/R7:
        # home_team, score_marker, date, time, away_team, venue, optional Árbitro:, optional referee
        if i + 5 < len(lines):
            home = lines[i]
            score_marker = lines[i + 1]
            date_value = lines[i + 2]
            time_value = lines[i + 3]
            away = lines[i + 4]
            venue = lines[i + 5]

            if (
                r11_is_score_marker(score_marker)
                and r11_is_date(date_value)
                and r11_is_time(time_value)
                and home.lower() != "árbitro:"
                and away.lower() != "árbitro:"
            ):
                home_score, away_score = r11_parse_score(score_marker)

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
                    "fixture_date": date_value,
                    "kickoff_time_local": time_value,
                    "venue_name_source": venue,
                    "referee": referee,
                    "raw_sequence": " | ".join(lines[i:i + consumed]),
                    "data_confidence": "high" if home and away and date_value and time_value else "needs_review",
                    "notes": "Parsed from RFEF Calendario visible text sequence.",
                })

                i += consumed
                continue

        i += 1

    return fixtures


try:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for group in r11_groups:
            source_url = (
                "https://resultados.rfef.es/pnfg/NPcd/NFG_VisCalendario_Vis"
                "?cod_primaria=1000120"
                f"&codtemporada={group['cod_temporada']}"
                "&codJornada=38"
                f"&codcompeticion={group['cod_competicion']}"
                f"&codgrupo={group['cod_grupo']}"
            )

            try:
                page = browser.new_page(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                )

                # Establish session first on the RFEF panel page.
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

                page.goto(source_url, wait_until="networkidle", timeout=60000)
                page.wait_for_timeout(3000)

                page_text = page.inner_text("body")
                page_html = page.content()

                safe_name = re.sub(
                    r"[^A-Za-z0-9]+",
                    "_",
                    f"{group['competition_group']}_calendario_full",
                ).strip("_").lower()

                html_path = EXPORT_DIR / f"rfef_research_r11_{safe_name}.html"
                html_path.write_text(page_html[:1000000], encoding="utf-8")

                text_path = EXPORT_DIR / f"rfef_research_r11_{safe_name}_text.txt"
                text_path.write_text(page_text[:700000], encoding="utf-8")

                lines = r11_clean_lines(page_text)
                fixtures = r11_parse_fixtures_from_lines(lines)

                if not fixtures:
                    r11_rows.append({
                        "season_id": group["season_id"],
                        "competition_id": group["competition_id"],
                        "competition_name": group["competition_name"],
                        "competition_group": group["competition_group"],
                        "cod_temporada": group["cod_temporada"],
                        "cod_competicion": group["cod_competicion"],
                        "cod_grupo": group["cod_grupo"],
                        "source_url": source_url,
                        "fixture_index": "",
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
                        "notes": "No fixtures parsed from Calendario page. Inspect saved text/html.",
                    })

                for fixture_index, fixture in enumerate(fixtures):
                    r11_rows.append({
                        "season_id": group["season_id"],
                        "competition_id": group["competition_id"],
                        "competition_name": group["competition_name"],
                        "competition_group": group["competition_group"],
                        "cod_temporada": group["cod_temporada"],
                        "cod_competicion": group["cod_competicion"],
                        "cod_grupo": group["cod_grupo"],
                        "source_url": source_url,
                        "fixture_index": str(fixture_index),
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
                    })

                page.close()

            except Exception as e:
                r11_rows.append({
                    "season_id": group["season_id"],
                    "competition_id": group["competition_id"],
                    "competition_name": group["competition_name"],
                    "competition_group": group["competition_group"],
                    "cod_temporada": group["cod_temporada"],
                    "cod_competicion": group["cod_competicion"],
                    "cod_grupo": group["cod_grupo"],
                    "source_url": source_url,
                    "fixture_index": "",
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
                    "notes": f"R11 Calendario extraction failed: {type(e).__name__}: {e}",
                })

        browser.close()

except Exception as e:
    r11_rows.append({
        "season_id": "",
        "competition_id": "",
        "competition_name": "",
        "competition_group": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "source_url": "",
        "fixture_index": "",
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
        "notes": f"RFEF Research R11 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r11_full_calendar_parsed_fixtures.csv",
    r11_fields,
    r11_rows,
)

# Validation
r11_validation_fields = [
    "check_name",
    "result",
    "details",
]

r11_group_1_rows = [
    row for row in r11_rows
    if row.get("competition_group") == "Grupo 1"
    and row.get("data_confidence") != "failed"
]

r11_group_2_rows = [
    row for row in r11_rows
    if row.get("competition_group") == "Grupo 2"
    and row.get("data_confidence") != "failed"
]

r11_high_rows = [
    row for row in r11_rows
    if row.get("data_confidence") == "high"
]

r11_failed_rows = [
    row for row in r11_rows
    if row.get("data_confidence") == "failed"
]

r11_validation_rows = [
    {
        "check_name": "total_fixture_rows_non_failed",
        "result": str(len([row for row in r11_rows if row.get("data_confidence") != "failed"])),
        "details": "Expected up to 760 if full calendar exposes all fixtures for both groups.",
    },
    {
        "check_name": "grupo_1_fixture_rows_non_failed",
        "result": str(len(r11_group_1_rows)),
        "details": "Expected up to 380.",
    },
    {
        "check_name": "grupo_2_fixture_rows_non_failed",
        "result": str(len(r11_group_2_rows)),
        "details": "Expected up to 380.",
    },
    {
        "check_name": "high_confidence_rows",
        "result": str(len(r11_high_rows)),
        "details": "High-confidence parsed calendar fixtures.",
    },
    {
        "check_name": "failed_rows",
        "result": str(len(r11_failed_rows)),
        "details": "Expected 0 if both calendar pages parse.",
    },
]

write_csv(
    "rfef_research_r11_validation_summary.csv",
    r11_validation_fields,
    r11_validation_rows,
)

print(f"RFEF Research R11 produced {len(r11_rows)} rows.")
# RFEF Research Stage R12:
# Extract every competition/group/season code pair from the R2 classification response
# -----------------------------

r12_fields = [
    "row_type",
    "nearby_label",
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "contains_primera_federacion",
    "contains_fase_regular",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_play_off",
    "contains_segunda",
    "route_hint",
    "raw_context",
    "notes",
]

r12_rows = []


def r12_extract_all_codes(context):
    patterns = {
        "cod_temporada": [
            r"CodTemporada=([0-9]+)",
            r"codtemporada=([0-9]+)",
            r"CodTemporada['\" ]*[:=]['\" ]*([0-9]+)",
            r"codtemporada['\" ]*[:=]['\" ]*([0-9]+)",
        ],
        "cod_competicion": [
            r"CodCompeticion=([0-9]+)",
            r"codcompeticion=([0-9]+)",
            r"CodCompeticion['\" ]*[:=]['\" ]*([0-9]+)",
            r"codcompeticion['\" ]*[:=]['\" ]*([0-9]+)",
        ],
        "cod_grupo": [
            r"CodGrupo=([0-9]+)",
            r"codgrupo=([0-9]+)",
            r"CodGrupo['\" ]*[:=]['\" ]*([0-9]+)",
            r"codgrupo['\" ]*[:=]['\" ]*([0-9]+)",
        ],
        "cod_jornada": [
            r"CodJornada=([0-9]+)",
            r"codjornada=([0-9]+)",
            r"CodJornada['\" ]*[:=]['\" ]*([0-9]+)",
            r"codjornada['\" ]*[:=]['\" ]*([0-9]+)",
        ],
    }

    extracted = {}

    for key, pattern_list in patterns.items():
        values = []
        for pattern in pattern_list:
            values.extend(re.findall(pattern, context, re.IGNORECASE))
        extracted[key] = sorted(set(values))

    return extracted


def r12_flags(text):
    lower = text.lower()

    return {
        "contains_primera_federacion": str(
            "primera federación" in lower
            or "primera federacion" in lower
            or "primera federaci" in lower
        ).lower(),
        "contains_fase_regular": str(
            "fase regular" in lower
            or "liga regular" in lower
        ).lower(),
        "contains_grupo_1": str(
            "grupo 1" in lower
            or "grupo i" in lower
        ).lower(),
        "contains_grupo_2": str(
            "grupo 2" in lower
            or "grupo ii" in lower
        ).lower(),
        "contains_play_off": str(
            "play off" in lower
            or "play-off" in lower
            or "playoff" in lower
        ).lower(),
        "contains_segunda": str(
            "segunda división" in lower
            or "segunda division" in lower
            or "hypermotion" in lower
        ).lower(),
    }


def r12_route_hint(text):
    lower = text.lower()
    hints = []

    for token in [
        "nfg_cmpjornada",
        "nfg_viscalendario_vis",
        "nfg_viscalendario",
        "nfg_visclasificacion",
        "nfg_cmpacta",
        "nfg_visacta",
        "calendario",
        "jornada",
        "resultados",
        "clasificacion",
        "clasificación",
    ]:
        if token in lower:
            hints.append(token)

    return "|".join(hints)


try:
    response_file = EXPORT_DIR / "rfef_research_r2_football_masculino_femenino_clasificacion_exact_button.html"

    if not response_file.exists():
        r12_rows.append({
            "row_type": "error",
            "nearby_label": "",
            "cod_temporada": "",
            "cod_competicion": "",
            "cod_grupo": "",
            "cod_jornada": "",
            "contains_primera_federacion": "false",
            "contains_fase_regular": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_play_off": "false",
            "contains_segunda": "false",
            "route_hint": "",
            "raw_context": "",
            "notes": "Expected R2 classification response HTML file not found. Run R2 first.",
        })

    else:
        html = response_file.read_text(encoding="utf-8", errors="ignore")

        # Break into useful chunks around links/buttons/divs.
        fragments = re.split(
            r"[\n\r]+|</a>|</button>|</div>|</li>|</tr>|</span>|</section>",
            html,
        )

        seen = set()

        for fragment in fragments:
            fragment_lower = fragment.lower()

            has_relevant_text = (
                "primera federaci" in fragment_lower
                or "fase regular" in fragment_lower
                or "liga regular" in fragment_lower
                or "grupo 1" in fragment_lower
                or "grupo 2" in fragment_lower
                or "grupo i" in fragment_lower
                or "grupo ii" in fragment_lower
                or "codcompeticion" in fragment_lower
                or "codgrupo" in fragment_lower
                or "codtemporada" in fragment_lower
                or "nfg_" in fragment_lower
            )

            if not has_relevant_text:
                continue

            cleaned = re.sub(r"<[^>]+>", " ", fragment)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()

            codes = r12_extract_all_codes(fragment)
            flags = r12_flags(fragment)

            # If a fragment has multiple values, output all combinations.
            temporadas = codes["cod_temporada"] or [""]
            competiciones = codes["cod_competicion"] or [""]
            grupos = codes["cod_grupo"] or [""]
            jornadas = codes["cod_jornada"] or [""]

            for temporada in temporadas:
                for competicion in competiciones:
                    for grupo in grupos:
                        for jornada in jornadas:
                            key = (
                                cleaned[:300],
                                temporada,
                                competicion,
                                grupo,
                                jornada,
                                r12_route_hint(fragment),
                            )

                            if key in seen:
                                continue

                            seen.add(key)

                            r12_rows.append({
                                "row_type": "fragment",
                                "nearby_label": cleaned[:1500],
                                "cod_temporada": temporada,
                                "cod_competicion": competicion,
                                "cod_grupo": grupo,
                                "cod_jornada": jornada,
                                **flags,
                                "route_hint": r12_route_hint(fragment),
                                "raw_context": fragment[:3000],
                                "notes": "Code/context fragment extracted from R2 classification response.",
                            })

        # Also create context windows around every occurrence of CodCompeticion/CodGrupo values.
        search_terms = [
            "CodCompeticion",
            "codcompeticion",
            "CodGrupo",
            "codgrupo",
            "CodTemporada",
            "codtemporada",
            "23289295",
            "23289296",
            "23289297",
        ]

        for term in search_terms:
            lower_html = html.lower()
            lower_term = term.lower()
            start = 0

            while True:
                index = lower_html.find(lower_term, start)

                if index == -1:
                    break

                context_start = max(index - 1500, 0)
                context_end = min(index + 2500, len(html))
                context = html[context_start:context_end]

                cleaned = re.sub(r"<[^>]+>", " ", context)
                cleaned = re.sub(r"\s+", " ", cleaned).strip()

                codes = r12_extract_all_codes(context)
                flags = r12_flags(context)

                temporadas = codes["cod_temporada"] or [""]
                competiciones = codes["cod_competicion"] or [""]
                grupos = codes["cod_grupo"] or [""]
                jornadas = codes["cod_jornada"] or [""]

                for temporada in temporadas:
                    for competicion in competiciones:
                        for grupo in grupos:
                            for jornada in jornadas:
                                key = (
                                    "context",
                                    term,
                                    temporada,
                                    competicion,
                                    grupo,
                                    jornada,
                                    cleaned[:200],
                                )

                                if key in seen:
                                    continue

                                seen.add(key)

                                r12_rows.append({
                                    "row_type": "context_window",
                                    "nearby_label": cleaned[:1500],
                                    "cod_temporada": temporada,
                                    "cod_competicion": competicion,
                                    "cod_grupo": grupo,
                                    "cod_jornada": jornada,
                                    **flags,
                                    "route_hint": r12_route_hint(context),
                                    "raw_context": context[:4000],
                                    "notes": f"Context window around term: {term}",
                                })

                start = index + len(lower_term)

except Exception as e:
    r12_rows.append({
        "row_type": "error",
        "nearby_label": "",
        "cod_temporada": "",
        "cod_competicion": "",
        "cod_grupo": "",
        "cod_jornada": "",
        "contains_primera_federacion": "false",
        "contains_fase_regular": "false",
        "contains_grupo_1": "false",
        "contains_grupo_2": "false",
        "contains_play_off": "false",
        "contains_segunda": "false",
        "route_hint": "",
        "raw_context": "",
        "notes": f"RFEF Research R12 failed: {type(e).__name__}: {e}",
    })

write_csv(
    "rfef_research_r12_all_classification_code_pairs.csv",
    r12_fields,
    r12_rows,
)

# Create deduped code-pair summary
r12_summary_fields = [
    "cod_temporada",
    "cod_competicion",
    "cod_grupo",
    "cod_jornada",
    "occurrences",
    "contains_primera_federacion",
    "contains_fase_regular",
    "contains_grupo_1",
    "contains_grupo_2",
    "contains_play_off",
    "contains_segunda",
    "route_hints",
    "best_label",
]

summary = {}

for row in r12_rows:
    key = (
        row.get("cod_temporada", ""),
        row.get("cod_competicion", ""),
        row.get("cod_grupo", ""),
        row.get("cod_jornada", ""),
    )

    if not any(key):
        continue

    if key not in summary:
        summary[key] = {
            "cod_temporada": key[0],
            "cod_competicion": key[1],
            "cod_grupo": key[2],
            "cod_jornada": key[3],
            "occurrences": 0,
            "contains_primera_federacion": "false",
            "contains_fase_regular": "false",
            "contains_grupo_1": "false",
            "contains_grupo_2": "false",
            "contains_play_off": "false",
            "contains_segunda": "false",
            "route_hints": set(),
            "best_label": "",
        }

    summary[key]["occurrences"] += 1

    for flag in [
        "contains_primera_federacion",
        "contains_fase_regular",
        "contains_grupo_1",
        "contains_grupo_2",
        "contains_play_off",
        "contains_segunda",
    ]:
        if row.get(flag) == "true":
            summary[key][flag] = "true"

    if row.get("route_hint"):
        summary[key]["route_hints"].add(row.get("route_hint"))

    if len(row.get("nearby_label", "")) > len(summary[key]["best_label"]):
        summary[key]["best_label"] = row.get("nearby_label", "")

r12_summary_rows = []

for item in summary.values():
    r12_summary_rows.append({
        "cod_temporada": item["cod_temporada"],
        "cod_competicion": item["cod_competicion"],
        "cod_grupo": item["cod_grupo"],
        "cod_jornada": item["cod_jornada"],
        "occurrences": str(item["occurrences"]),
        "contains_primera_federacion": item["contains_primera_federacion"],
        "contains_fase_regular": item["contains_fase_regular"],
        "contains_grupo_1": item["contains_grupo_1"],
        "contains_grupo_2": item["contains_grupo_2"],
        "contains_play_off": item["contains_play_off"],
        "contains_segunda": item["contains_segunda"],
        "route_hints": "|".join(sorted(item["route_hints"])),
        "best_label": item["best_label"][:2000],
    })

r12_summary_rows = sorted(
    r12_summary_rows,
    key=lambda row: (
        row["cod_competicion"],
        row["cod_grupo"],
        row["cod_jornada"],
    ),
)

write_csv(
    "rfef_research_r12_code_pair_summary.csv",
    r12_summary_fields,
    r12_summary_rows,
)

print(f"RFEF Research R12 extracted {len(r12_rows)} code/context rows.")
print(f"RFEF Research R12 summarised {len(r12_summary_rows)} code pairs.")
write_csv(
    "primerafed_2025_26_failed_pages_audit.csv",
    failure_audit_fields,
    failure_audit_rows,
)

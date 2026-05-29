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

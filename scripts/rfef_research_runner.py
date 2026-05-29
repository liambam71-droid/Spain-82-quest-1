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

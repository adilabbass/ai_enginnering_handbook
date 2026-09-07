from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    )
}

IRRELEVANT_TAGS = ["script", "style", "nav", "footer", "header", "aside", "form", "noscript", "svg", "img"]


def parse_html(html: str, url: str, max_chars: int = 5_000) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else "No title"

    text = ""
    if soup.body:
        for tag in soup.body(IRRELEVANT_TAGS):
            tag.decompose()
        text = soup.body.get_text(separator="\n", strip=True)

    return {
        "site": url,
        "content": (title + "\n\n" + text)[:max_chars],
    }


def stock_data() -> list[dict[str, str]]:
    TARGETS = [
        "https://dps.psx.com.pk/",
        "https://www.psx.com.pk/market-summary/",
        "https://www.psx.com.pk/",
    ]

    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            extra_http_headers=HEADERS,
            viewport={"width": 1280, "height": 800},
        )
        page = context.new_page()

        for url in TARGETS:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                page.wait_for_timeout(3000)
                html = page.content()
                results.append(parse_html(html, url))
            except Exception as e:
                results.append({"site": url, "content": f"Error: {e}"})

        browser.close()

    return results
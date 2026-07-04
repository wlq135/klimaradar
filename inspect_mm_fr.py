import asyncio
from playwright.async_api import async_playwright

URLS = {
    "mediamarkt_fr": "https://www.mediamarkt.fr/fr/search.html?query=climatiseur+mobile",
}


async def inspect(name, url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="fr-FR",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)
            html = await page.content()
            with open(f"inspect_{name}.html", "w", encoding="utf-8") as f:
                f.write(html)
            print(f"[{name}] saved ({len(html)} chars)")
        except Exception as e:
            print(f"[{name}] error: {e}")
        finally:
            await browser.close()


async def main():
    for name, url in URLS.items():
        await inspect(name, url)


if __name__ == "__main__":
    asyncio.run(main())

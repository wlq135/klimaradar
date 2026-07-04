import asyncio
from playwright.async_api import async_playwright

URLS = {
    "amazon_de": "https://www.amazon.de/s?k=mobile+klimaanlage",
}


async def inspect(name, url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
        )
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Scroll to bottom a couple of times to trigger lazy loading
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 800)")
                await page.wait_for_timeout(2000)
            try:
                await page.wait_for_selector("span.a-price", timeout=15000)
                print(f"[{name}] price selector found")
            except Exception as e:
                print(f"[{name}] price selector not found: {e}")
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

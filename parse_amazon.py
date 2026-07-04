import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

with open("inspect_amazon_de.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "lxml")

items = soup.select('div[data-component-type="s-search-result"]')
print(f"Total items: {len(items)}")
for idx, item in enumerate(items[:10], start=1):
    asin = item.get("data-asin")
    title_a = item.select_one("a.a-link-normal.s-line-clamp-2")
    title = title_a.get_text(strip=True) if title_a else None
    link = title_a.get("href") if title_a else None
    price_el = item.select_one("span.a-price span.a-offscreen")
    price = price_el.get_text(strip=True) if price_el else None
    img = item.select_one("img.s-image")
    img_url = img.get("src") if img else None
    print(f"{idx}. ASIN={asin}")
    print(f"   title: {title}")
    print(f"   price: {price}")
    print(f"   link:  {link[:80] if link else None}")
    print(f"   img:   {img_url[:80] if img_url else None}")

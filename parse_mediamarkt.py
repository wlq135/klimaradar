import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

with open("inspect_mediamarkt_de.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "lxml")

print("title:", soup.title.get_text() if soup.title else "none")
# Try common selectors
selectors = {
    "product": "article.Product",
    "product2": "[data-test='product']",
    "product3": "div.Product",
    "product4": "li.Product",
}
for name, sel in selectors.items():
    items = soup.select(sel)
    print(f"{name} ({sel}): {len(items)}")

# Print a snippet around a known product title
if soup.get_text().find("Klimaanlage") > 0:
    print("Klimaanlage found in page")

# Try to find elements containing 'Klimaanlage'
for el in soup.find_all(string=lambda t: t and "Klimaanlage" in t):
    parent = el.parent
    print(f"text: {el.strip()[:100]} | tag: {parent.name} | class: {parent.get('class')}")
    break

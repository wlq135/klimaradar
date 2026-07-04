import sys
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding="utf-8")

with open("inspect_billiger_de.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "lxml")

print("title:", soup.title.get_text() if soup.title else "none")
print("first 200 text:", soup.get_text(strip=True)[:200])
# try to find product containers
for cls in ["product-item", "product", "offer", "item"]:
    items = soup.find_all(class_=cls)
    print(f"class {cls}: {len(items)}")

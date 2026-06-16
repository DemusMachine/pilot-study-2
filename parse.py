import os
import requests
from playwright.sync_api import sync_playwright

URL         = "https://www.matouk.com/shop/table/placemats"
SAVE_FOLDER = "images"

if not os.path.exists(SAVE_FOLDER):
    print("Error: 'images' folder not found")
    exit()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

def get_all_primary_images(page):
    return page.evaluate("""
        () => Array.from(document.querySelectorAll('img'))
              .filter(img => img.className && img.className.includes('_3YlSt'))
              .map(img => ({
                  src:        img.src || img.dataset.src || '',
                  alt:        img.alt || '',
                  opacity:    parseFloat(window.getComputedStyle(img).opacity),
                  display:    window.getComputedStyle(img).display,
                  visibility: window.getComputedStyle(img).visibility
              }))
    """)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page    = browser.new_page(
        viewport    = {"width": 1440, "height": 900},
        user_agent  = HEADERS["User-Agent"]
    )

    print("Loading page...")
    page.goto(URL, wait_until="domcontentloaded", timeout=30_000)
    page.wait_for_timeout(3000)   

    print("Scrolling to load all products...")
    prev_count = 0
    stale_rounds = 0

    while stale_rounds < 3:          
        page.evaluate("window.scrollBy(0, 1200)")
        page.wait_for_timeout(1500)

        current = get_all_primary_images(page)
        new_count = len([i for i in current if i["opacity"] > 0.5])

        print(f"  Products visible so far: {new_count}")

        if new_count == prev_count:
            stale_rounds += 1
        else:
            stale_rounds = 0
            prev_count = new_count

    
    all_imgs = get_all_primary_images(page)
    browser.close()


primary = [
    img for img in all_imgs
    if img["src"]
    and not img["src"].startswith("data:")
    and img["display"]    != "none"
    and img["visibility"] != "hidden"
    and img["opacity"]    >  0.5
]

seen = set()
unique = []
for img in primary:
    if img["src"] not in seen:
        seen.add(img["src"])
        unique.append(img)

print(f"\nFound {len(unique)} unique primary images. Downloading...")

count = 1
for item in unique:
    if count > 100:
        break
    try:
        data     = requests.get(item["src"], headers=HEADERS, timeout=10).content
        filename = f"P{count:02d}.jpg"
        with open(os.path.join(SAVE_FOLDER, filename), "wb") as f:
            f.write(data)
        print(f"P{count:02d}")
        count += 1
    except Exception as e:
        print(f"  Error on image {count}: {e}")

print(f"\nDone! {count - 1} images saved to '{SAVE_FOLDER}/'")
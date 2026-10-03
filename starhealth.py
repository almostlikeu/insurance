import asyncio
import json
from playwright.async_api import async_playwright

async def scrape_practo():
    urls = [
        "https://www.practo.com/moradabad/hospitals",
        "https://www.practo.com/moradabad/clinics"
    ]
    
    results = []

    async with async_playwright() as p:
        # Launch with standard user arguments to avoid automation flags
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        for url in urls:
            category = "hospital" if "hospitals" in url else "clinic"
            print(f"Navigating to {url}...")
            
            try:
                await page.goto(url, wait_until="networkidle", timeout=45000)
                await page.wait_for_timeout(3000)

                # Query all primary h2 tags (which Practo uses for facility titles)
                cards = await page.query_selector_all("h2")
                
                for h2 in cards:
                    name = (await h2.inner_text()).strip()
                    # Skip common navigation headings
                    if not name or any(skip in name.lower() for skip in ["filter", "top", "looking for", "feedback", "frequently", "about"]):
                        continue
                    
                    results.append({
                        "name": name,
                        "category": category,
                        "locality": "Moradabad",
                        "source": "Practo"
                    })
            except Exception as e:
                print(f"Error accessing {url}: {e}")

        await browser.close()

    # Deduplicate
    unique = {item["name"]: item for item in results}.values()
    final_list = list(unique)
    
    print(f"Successfully scraped {len(final_list)} entries from Practo.")
    with open("practo_moradabad.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(scrape_practo())
import asyncio
import json
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

url = "https://www.surf-forecast.com/breaks/Saltstein/forecasts/latest"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 2500, "height": 1400})
        page = await context.new_page()

        print("Åpner nettsiden...")
        await page.goto(url, wait_until="domcontentloaded")

        # 1. Cookie-banner
        cookie_knapp_selector = "#accept-btn > span"
        try:
            await page.wait_for_selector(cookie_knapp_selector, timeout=5000)
            await page.click(cookie_knapp_selector)
            print("Aksepterte cookies.")
        except Exception:
            pass

        await page.wait_for_timeout(1000)

        # 2. Utvid tabellen til time-for-time
        try:
            knapp_selector = "button.forecast-table-days__button:nth-child(2), button[data-action='toggle-hourly']"
            await page.wait_for_selector(knapp_selector, state="visible", timeout=7000)
            await page.click(knapp_selector, force=True)
            print("Klikket på knappen for å utvide tabellen.")
        except Exception as e:
            print(f"Kunne ikke trykke på utvidelsesknappen (mulig den allerede er utvidet): {e}")

        # 3. Vent på at tabellen oppdateres
        tabell = page.locator(".forecast-table__content")
        await tabell.wait_for(state="visible")
        await page.wait_for_timeout(1000)

        # 4. Hent HTML
        html = await page.content()
        await browser.close()

    # 5. Parse data med BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    tr_list = soup.select(".forecast-table__table > tbody > tr")
    row_tid = soup.select_one(".forecast-table__table > thead > tr:nth-child(3)")

    surf_data_dict = {}

    if len(tr_list) >= 5 and row_tid:
        row_periode = tr_list[2]
        row_energi = tr_list[4]

        tid_tds = row_tid.select("td")

        for idx, td in enumerate(tid_tds):
            data_index = idx + 2

            span_tid = td.select_one("div:nth-child(1) > span:nth-child(1)")
            tid_str = span_tid.get_text(strip=True) if span_tid else "--"

            td_periode = row_periode.select_one(
                f"td:nth-child({data_index}) > div:nth-child(1) > div:nth-child(3)"
            )
            periode_str = td_periode.get_text(strip=True) if td_periode else "0"

            td_energi = row_energi.select_one(f"td:nth-child({data_index})")
            energi_str = td_energi.get_text(strip=True) if td_energi else "0"

            # Vask periode
            periode_str = periode_str.strip()
            if not periode_str or periode_str == "-" or not periode_str.replace(".", "", 1).isdigit():
                periode_str = "0"

            # Vask energi
            energi_str = energi_str.strip()
            if not energi_str or energi_str == "-":
                energi_str = "0"

            try:
                periode_num = float(periode_str)
            except ValueError:
                periode_num = 0.0

            try:
                energi_num = float(energi_str)
            except ValueError:
                energi_num = 0.0

            # Sjekk om forholdene er gode (setter is_good = True for grønn ramme)
            is_good = (periode_num >= 2.0 and energi_num > 0)

            # Lagre i dict med klokkeslett som nøkkel (eks "12 AM", "1 PM")
            surf_data_dict[tid_str] = {
                "energi": energi_str,
                "periode": periode_str,
                "is_good": is_good
            }

            # Stopp ved "11 PM"
            tid_ren = tid_str.strip().upper()
            if tid_ren in ["11 PM", "11PM", "23", "23:00"]:
                break

    # Skriv data direkte til surf_data.js
    with open("surf_data.js", "w", encoding="utf-8") as f:
        f.write(f"window.SURF_DATA = {json.dumps(surf_data_dict, indent=2)};\n")

    print(f"Suksess! Genererte surf_data.js med {len(surf_data_dict)} datapunkter.")

if __name__ == "__main__":
    asyncio.run(main())

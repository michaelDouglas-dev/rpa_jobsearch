import asyncio
import ctypes
from playwright.async_api import async_playwright, Error as PlaywrightError
from .config import COUNTRY, SEARCH_TERM, USE_PERSISTENT_BROWSER, BROWSER_PROFILE_PATH, BROWSER, DEBUG, WAIT_TIME, FROM_AGE
from .database import get_or_create, insert_job
from .pages.glassdoor_page import GlassdoorPage

# New imports for real maximization
import pygetwindow as gw
import time

async def maximize_window(page):
    """Try maximize via Playwright and pygetwindow fallback."""
    try:
        session = await page.context.new_cdp_session(page)
        await session.send("Browser.setWindowBounds", {
            "windowId": 1,
            "bounds": {"windowState": "maximized"}
        })
    except Exception:
        try:
            time.sleep(1)
            wins = gw.getWindowsWithTitle("Glassdoor")
            if wins:
                win = wins[0]
                win.maximize()
        except Exception as e:
            print("⚠️ Could not maximize window:", e)

async def search_glassdoor():
    try:
        country_id = get_or_create("countries", "name", COUNTRY)
        job_title_id = get_or_create("job_titles", "title", SEARCH_TERM)

        async with async_playwright() as p:
            args = ["--disable-blink-features=AutomationControlled", "--disable-infobars"]

            if USE_PERSISTENT_BROWSER and BROWSER_PROFILE_PATH:
                browser_context = await p.chromium.launch_persistent_context(
                    user_data_dir=BROWSER_PROFILE_PATH,
                    channel=BROWSER.lower(),
                    headless=False,
                    args=args
                )
                page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
            else:
                browser_context = await p.chromium.launch(headless=False, channel=BROWSER.lower(), args=args)
                page = await browser_context.new_page()

            # Maximize
            await maximize_window(page)

            print("Navigating directly to Glassdoor jobs page...")
            await page.goto("https://www.glassdoor.co.uk/Job/index.htm")
            gd = GlassdoorPage(page, wait_time=WAIT_TIME)

            if not await gd.is_logged_in():
                print("⚠️ Login required. Please log in manually and click OK.")
                ctypes.windll.user32.MessageBoxW(
                    0,
                    "Login required on Glassdoor. Please log in manually and click OK.",
                    "RPA Login",
                    0
                )

            await gd.wait(WAIT_TIME)
            await gd.search_job(SEARCH_TERM, COUNTRY)
            await gd.close_modal_if_exists()

            current_url = page.url
            if "?" in current_url:
                full_url = f"{current_url}&sortBy=date_desc&fromAge={FROM_AGE}"
            else:
                full_url = f"{current_url}?sortBy=date_desc&fromAge={FROM_AGE}"

            print(f"Navigating to filtered URL: {full_url}")
            await page.goto(full_url)
            await gd.wait(WAIT_TIME)

            await gd.load_all_jobs()
            await gd.close_modal_if_exists()

            jobs = await gd.get_jobs()
            print(f"Total jobs scraped: {len(jobs)}")

            for job in jobs:
                insert_job(country_id, job_title_id, job['title'], job['company'], job['location'], job['description'])
                print(f"Saved: {job['title']} - {job['company']}")

            if not (USE_PERSISTENT_BROWSER and BROWSER_PROFILE_PATH):
                await browser_context.close()

    except PlaywrightError as e:
        print("Playwright error:", e)
    except Exception as e:
        import traceback
        print("Unexpected error:", e)
        traceback.print_exc()

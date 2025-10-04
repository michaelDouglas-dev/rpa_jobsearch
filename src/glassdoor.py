# src/glassdoor.py  (MODIFIED)
import asyncio
import time
from playwright.async_api import async_playwright, Error as PlaywrightError
from .config import COUNTRY as CFG_COUNTRY, SEARCH_TERM as CFG_SEARCH_TERM, USE_PERSISTENT_BROWSER, BROWSER_PROFILE_PATH, BROWSER, DEBUG, WAIT_TIME, FROM_AGE
from .database import get_or_create, insert_job, get_search_params, get_keywords_for_title
from .pages.glassdoor_page import GlassdoorPage
from .utils import controls, ui
from .utils.window import maximize_and_set_viewport

async def search_glassdoor():
    controls.start_listeners()

    db_params = get_search_params()
    COUNTRY = db_params[0] if db_params else CFG_COUNTRY
    SEARCH_TERM = db_params[1] if db_params else CFG_SEARCH_TERM

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

            # maximize and set viewport to actual window bounds
            await maximize_and_set_viewport(page, title_hint="Glassdoor")

            print("Navigating directly to Glassdoor jobs page...")
            await page.goto("https://www.glassdoor.co.uk/Job/index.htm")
            gd = GlassdoorPage(page, wait_time=WAIT_TIME)

            if not await gd.is_logged_in():
                ui.show_msgbox("RPA Login", "Login required on Glassdoor. Please log in manually and click OK.")

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

            # ensure modal closed after load
            await gd.close_modal_if_exists()

            # get keywords for the job_title_id and pass to get_jobs
            keywords = get_keywords_for_title(job_title_id)
            print(f"Total keywords scraped: {keywords}")
            
            jobs = await gd.get_jobs(keywords=keywords)
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

from ..utils.base_page import BasePage
import ctypes
import asyncio

class GlassdoorPage(BasePage):
    MODAL_SELECTOR = '.modal_ModalContainer__GGVJc'
    SHOW_MORE_BUTTON = '[data-test="load-more"]'
    SHOW_MORE_CTA = '[data-test="show-more-cta"]'
    TRACKING_LINK = '[class*="trackingLink"]'
    JOB_CARD_SELECTOR = '.jobCard'
    TITLE_SELECTOR_PART = '[class*="jobTitle"]'
    COMPANY_SELECTOR_PART = '[class*="EmployerProfile"]'
    LOCATION_SELECTOR_PART = '[class*="JobCard_location"]'
    DESCRIPTION_SELECTOR_PART = '[class*="jobDescription"]'

    async def accept_cookies(self):
        await self.safe_click('button:has-text("Accept")')

    async def is_logged_in(self) -> bool:
        el = await self.find_element('[aria-label="profile"]')
        return el is not None

    async def search_job(self, job_title: str, country: str):
        await self.fill_input('[aria-labelledby="searchBar-jobTitle_label"]', job_title)
        await self.fill_input('[aria-labelledby="searchBar-location_label"]', country)
        await self.page.keyboard.press("Enter")
        await self.wait()

    async def close_modal_if_exists(self):
        # Reinforced modal close: multiple strategies
        modal = await self.find_element(self.MODAL_SELECTOR, timeout=2000)
        if modal:
            try:
                await self.page.evaluate("""(sel) => {
                    const m = document.querySelector(sel);
                    if (m) {
                        const btn = m.querySelector('button') || m.querySelector('[aria-label="close"]');
                        if (btn) btn.click();
                        else m.remove();
                    }
                }""", self.MODAL_SELECTOR)
                await self.wait()
            except Exception:
                pass

    async def load_all_jobs(self):
        while True:
            btn = await self.find_element(self.SHOW_MORE_BUTTON)
            if not btn:
                break
            clicked = await self.safe_click(self.SHOW_MORE_BUTTON)
            if not clicked:
                break
            await self.wait()

    async def get_jobs(self):
        job_cards = await self.find_elements(self.JOB_CARD_SELECTOR)
        results = []

        for job in job_cards:
            title_el = await job.query_selector(self.TITLE_SELECTOR_PART)
            company_el = await job.query_selector(self.COMPANY_SELECTOR_PART)
            location_el = await job.query_selector(self.LOCATION_SELECTOR_PART)

            title = (await title_el.inner_text()).strip() if title_el else ""
            company = (await company_el.inner_text()).strip() if company_el else ""
            location = (await location_el.inner_text()).strip() if location_el else ""

            tracking = await job.query_selector(self.TRACKING_LINK)
            description = ""
            if tracking:
                try:
                    await tracking.scroll_into_view_if_needed()
                except Exception:
                    pass
                try:
                    await self.page.evaluate("(el) => el.click()", tracking)
                except Exception:
                    try:
                        await tracking.click()
                    except Exception:
                        pass

                await asyncio.sleep(2)
                await self.close_modal_if_exists()

                show_more_cta = await self.find_element(self.SHOW_MORE_CTA)
                if show_more_cta:
                    await self.safe_click(self.SHOW_MORE_CTA)
                    await asyncio.sleep(1)

                desc_el = await self.find_element(self.DESCRIPTION_SELECTOR_PART)
                if desc_el:
                    try:
                        description = (await desc_el.inner_text()).strip()
                    except Exception:
                        description = ""

            ctypes.windll.user32.MessageBoxW(
                0,
                f"Title: {title}\nCompany: {company}\nLocation: {location}\n\nDescription:\n{description}",
                "Job Validation",
                0
            )

            results.append({
                "title": title,
                "company": company,
                "location": location,
                "description": description
            })

        return results

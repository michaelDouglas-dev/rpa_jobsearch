from playwright.async_api import Page, Error as PlaywrightError
from typing import Optional, List
import asyncio

DEFAULT_CLICK_RETRIES = 8
DEFAULT_CLICK_WAIT = 0.5

class BasePage:
    def __init__(self, page: Page, wait_time: float = 3.0):
        self.page = page
        self.wait_time = wait_time

    async def wait(self, seconds: float = None):
        await asyncio.sleep(seconds or self.wait_time)

    async def find_element(self, selector: str, timeout: int = 5000) -> Optional[object]:
        try:
            return await self.page.wait_for_selector(selector, timeout=timeout)
        except PlaywrightError:
            return None

    async def find_elements(self, selector: str, timeout: int = 5000) -> List[object]:
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            return await self.page.query_selector_all(selector)
        except PlaywrightError:
            return []

    async def click(self, selector: str) -> bool:
        el = await self.find_element(selector)
        if not el:
            return False
        try:
            await el.click()
            return True
        except PlaywrightError:
            return False

    async def safe_click(self, selector: str, retries: int = DEFAULT_CLICK_RETRIES, retry_wait: float = DEFAULT_CLICK_WAIT, force: bool = True) -> bool:
        for attempt in range(retries):
            el = await self.find_element(selector, timeout=2000)
            if not el:
                await asyncio.sleep(retry_wait)
                continue
            try:
                try:
                    await el.wait_for_element_state("visible", timeout=2000)
                except PlaywrightError:
                    pass
                await el.click()
                return True
            except PlaywrightError:
                try:
                    await el.scroll_into_view_if_needed()
                except PlaywrightError:
                    pass
                await asyncio.sleep(retry_wait)
                if attempt == retries - 1:
                    try:
                        await self.page.evaluate("(el) => el.click()", el)
                        return True
                    except PlaywrightError:
                        try:
                            await el.click(force=force)
                            return True
                        except PlaywrightError:
                            pass
        return False

    async def fill_input(self, selector: str, text: str) -> bool:
        el = await self.find_element(selector)
        if not el:
            return False
        try:
            await el.fill(text)
            return True
        except PlaywrightError:
            try:
                await self.page.evaluate("""(sel, val) => { document.querySelector(sel).value = val; }""", selector, text)
                return True
            except PlaywrightError:
                return False

    async def get_text(self, selector: str) -> str:
        el = await self.find_element(selector)
        if not el:
            return ""
        try:
            return (await el.inner_text()).strip()
        except PlaywrightError:
            return ""

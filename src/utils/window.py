# src/utils/window.py  (NEW)
"""
Reusable window utilities for Windows OS.
Provides maximize_and_set_viewport(page, title_hint=None) which:
 - attempts CDP maximize and reads window bounds
 - sets Playwright page viewport to the browser window's inner size
 - falls back to pywinauto to maximize the window and then sets viewport by reading window rect
This module is designed to be reusable across projects.
"""

from typing import Optional
import time

async def cdp_maximize_and_get_bounds(page):
    """Use CDP to maximize and return bounds {left, top, width, height} or None."""
    try:
        session = await page.context.new_cdp_session(page)
        info = await session.send("Browser.getWindowForTarget")
        window_id = info.get("windowId")
        if window_id is None:
            return None
        await session.send("Browser.setWindowBounds", {"windowId": window_id, "bounds": {"windowState": "maximized"}})
        # small pause then get bounds
        time.sleep(0.5)
        bounds = await session.send("Browser.getWindowBounds", {"windowId": window_id})
        return bounds.get("bounds")
    except Exception:
        return None

def pywinauto_maximize_and_get_bounds(title_hint: Optional[str] = None):
    """Fallback using pywinauto to maximize window and return bounds dict or None."""
    try:
        from pywinauto import Desktop
    except Exception:
        return None
    try:
        desktop = Desktop(backend="uia")
        # if title hint provided, use it; else take first browser-like window
        windows = desktop.windows()
        target = None
        if title_hint:
            for w in windows:
                try:
                    if title_hint.lower() in w.window_text().lower():
                        target = w
                        break
                except Exception:
                    continue
        if not target:
            # fallback heuristics: choose first window with Chrome/Edge/Glassdoor in title
            for w in windows:
                try:
                    t = w.window_text().lower()
                    if any(k in t for k in ("chrome", "edge", "glassdoor", "brave")):
                        target = w
                        break
                except Exception:
                    continue
        if not target:
            return None
        target.maximize()
        rect = target.rectangle()
        bounds = {"left": rect.left, "top": rect.top, "width": rect.width(), "height": rect.height()}
        return bounds
    except Exception:
        return None

async def maximize_and_set_viewport(page, title_hint: Optional[str] = None):
    """
    Maximize the browser window and set Playwright page viewport to the window inner size.
    Returns True on success, False otherwise.
    """
    # Try CDP
    bounds = await cdp_maximize_and_get_bounds(page)
    if bounds:
        try:
            # bounds might be {"left":..,"top":..,"width":..,"height":..}
            width = bounds.get("width")
            height = bounds.get("height")
            if width and height:
                await page.set_viewport_size({"width": width, "height": height})
                return True
        except Exception:
            pass

    # Fallback to pywinauto
    bounds2 = pywinauto_maximize_and_get_bounds(title_hint)
    if bounds2:
        try:
            w = bounds2.get("width")
            h = bounds2.get("height")
            if w and h:
                await page.set_viewport_size({"width": w, "height": h})
                return True
        except Exception:
            pass

    # Last fallback: set large viewport
    try:
        await page.set_viewport_size({"width": 1920, "height": 1080})
        return True
    except Exception:
        return False

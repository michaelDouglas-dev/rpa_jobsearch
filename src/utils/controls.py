# src/utils/controls.py  (NEW)
import keyboard
import os
import threading
import time
from .shortcuts import SHORTCUTS
from .ui import show_overlay

# Global control state
_state = {
    "paused": False,
    "stop_event": None,   # overlay stop_event
    "restart_requested": False
}

def _kill_action():
    """Kill the process immediately."""
    os._exit(1)

def _restart_action():
    """Set restart flag so main can handle it (simple approach: exit with special code)."""
    _state["restart_requested"] = True
    os._exit(2)

def _pause_action():
    if not _state["paused"]:
        _state["paused"] = True
        # show overlay
        _state["stop_event"] = show_overlay("RPA PAUSED — Press Alt+. to RESUME")
    else:
        # if already paused, ignore
        pass

def _resume_action():
    if _state["paused"]:
        _state["paused"] = False
        if _state.get("stop_event"):
            _state["stop_event"].set()
            _state["stop_event"] = None

def install_hotkeys():
    """Install global hotkeys. Run this in a separate thread so it doesn't block."""
    # Kill
    keyboard.add_hotkey(SHORTCUTS["kill"], _kill_action, suppress=True)
    # Restart
    keyboard.add_hotkey(SHORTCUTS["restart"], _restart_action, suppress=True)
    # Pause (alt+< mapped to alt+comma)
    keyboard.add_hotkey(SHORTCUTS["pause"], _pause_action, suppress=True)
    # Resume
    keyboard.add_hotkey(SHORTCUTS["resume"], _resume_action, suppress=True)

def start_listeners():
    """Start hotkeys in a daemon thread."""
    thr = threading.Thread(target=install_hotkeys, daemon=True)
    thr.start()

def is_paused():
    return _state["paused"]

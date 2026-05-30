# ============================================================
# starfield_intelligent_gallery — Hotkey Overlay
# Author: Mark J. Latsha
# Location: Brentwood, CA 94513
# Email: Latsha2031@gmail.com
# Phone: 1-510-209-6474
#
# Description:
#   Listens for global hotkeys (if keyboard module installed).
#   Provides callbacks for slideshow, next/prev, etc.
#   Updated version aligned with starfield_gallery.py.
# ============================================================

import threading

class HotkeyOverlay:
    """
    Listens for global hotkeys (if keyboard module is installed).
    """

    def __init__(self):
        self.enabled = False
        self.callbacks = {}

    def register(self, key, callback):
        """
        Register a hotkey callback.
        """
        self.callbacks[key] = callback

    def start(self):
        """
        Begin listening for hotkeys in a background thread.
        """

        try:
            import keyboard
        except:
            print("HotkeyOverlay: keyboard module not available.")
            return

        self.enabled = True

        def listen():
            while self.enabled:
                for key, cb in self.callbacks.items():
                    if keyboard.is_pressed(key):
                        cb()

        thread = threading.Thread(target=listen, daemon=True)
        thread.start()

    def stop(self):
        self.enabled = False

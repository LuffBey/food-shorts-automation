#!/usr/bin/env python3
"""Send one ordinary OS-level left click to visible Chromium on X11 display :99.

Diagnostic helper only. It uses X11 focus, pointer movement, and XTEST button events;
it does not use CDP Input.dispatchMouseEvent, stealth, spoofing, proxying, or retries.
Usage: DISPLAY=:99 python3 click_generate_visible_ui.py X Y [WINDOW_ID]
"""
import ctypes
import ctypes.util
import os
import sys
import time


def click_generate_visible_ui(x: int, y: int, window_id: int) -> None:
    x11 = ctypes.CDLL(ctypes.util.find_library("X11"))
    xtst = ctypes.CDLL(ctypes.util.find_library("Xtst"))
    x11.XOpenDisplay.restype = ctypes.c_void_p
    display = x11.XOpenDisplay(os.environ.get("DISPLAY", ":99").encode())
    if not display:
        raise RuntimeError("Could not open X11 display")
    try:
        # Lift/focus the existing visible Chromium surface without altering browser DOM.
        x11.XRaiseWindow(ctypes.c_void_p(display), ctypes.c_ulong(window_id))
        x11.XSetInputFocus(ctypes.c_void_p(display), ctypes.c_ulong(window_id), 1, 0)
        x11.XFlush(ctypes.c_void_p(display))
        time.sleep(0.20)
        # Root coordinates. Motion precedes one and only one primary-button click.
        # XWarpPointer requires both a source and destination Window argument; use
        # the root window as the destination so X coordinates match noVNC's Xvfb surface.
        x11.XDefaultRootWindow.restype = ctypes.c_ulong
        root = x11.XDefaultRootWindow(ctypes.c_void_p(display))
        x11.XWarpPointer.argtypes = [
            ctypes.c_void_p, ctypes.c_ulong, ctypes.c_ulong,
            ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint,
            ctypes.c_int, ctypes.c_int,
        ]
        x11.XWarpPointer.restype = ctypes.c_int
        if not x11.XWarpPointer(ctypes.c_void_p(display), 0, root, 0, 0, 0, 0, int(x), int(y)):
            raise RuntimeError("Could not move X11 pointer")
        x11.XFlush(ctypes.c_void_p(display))
        time.sleep(0.15)
        if not xtst.XTestFakeButtonEvent(ctypes.c_void_p(display), 1, 1, 0):
            raise RuntimeError("Could not send X11 button press")
        x11.XFlush(ctypes.c_void_p(display))
        time.sleep(0.08)
        if not xtst.XTestFakeButtonEvent(ctypes.c_void_p(display), 1, 0, 0):
            raise RuntimeError("Could not send X11 button release")
        x11.XFlush(ctypes.c_void_p(display))
    finally:
        x11.XCloseDisplay(ctypes.c_void_p(display))


if __name__ == "__main__":
    if len(sys.argv) not in (3, 4):
        raise SystemExit("Usage: click_generate_visible_ui.py X Y [WINDOW_ID]")
    window = int(sys.argv[3], 0) if len(sys.argv) == 4 else 0x200003
    click_generate_visible_ui(int(sys.argv[1]), int(sys.argv[2]), window)
    print(f"OS-level single left click sent at ({sys.argv[1]}, {sys.argv[2]}) on window {hex(window)}")

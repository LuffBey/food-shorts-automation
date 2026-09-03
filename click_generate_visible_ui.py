#!/usr/bin/env python3
"""One fail-closed OS-level Generate click on visible Chromium/X11.

This diagnostic helper deliberately performs no CDP/DOM mouse input, browser
stealth/fingerprint change, proxy/VPN operation, CAPTCHA handling, or retry.
It receives fresh browser metrics measured via CDP immediately before the call,
uses XTEST motion on the X11 root surface, proves the pointer maps back inside
the DOM Generate rectangle, then sends exactly one primary-button click.

Usage:
  DISPLAY=:99 python3 click_generate_visible_ui.py \
    WINDOW_ID ROOT_X ROOT_Y SCREEN_X SCREEN_Y OUTER_W OUTER_H INNER_W INNER_H \
    DPR RECT_LEFT RECT_TOP RECT_WIDTH RECT_HEIGHT
"""
import ctypes
import ctypes.util
import json
import os
import sys
import time


class X11ClickError(RuntimeError):
    pass


def configure_apis(x11, xtst):
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    x11.XCloseDisplay.restype = ctypes.c_int
    x11.XRaiseWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x11.XRaiseWindow.restype = ctypes.c_int
    x11.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    x11.XSetInputFocus.restype = ctypes.c_int
    x11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
    x11.XSync.restype = ctypes.c_int
    x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    x11.XDefaultRootWindow.restype = ctypes.c_ulong
    x11.XQueryPointer.argtypes = [
        ctypes.c_void_p, ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ulong),
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int),
        ctypes.POINTER(ctypes.c_uint),
    ]
    x11.XQueryPointer.restype = ctypes.c_int
    xtst.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
    xtst.XTestFakeMotionEvent.restype = ctypes.c_int
    xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    xtst.XTestFakeButtonEvent.restype = ctypes.c_int


def query_pointer(x11, display, root):
    root_return = ctypes.c_ulong()
    child_return = ctypes.c_ulong()
    root_x = ctypes.c_int()
    root_y = ctypes.c_int()
    win_x = ctypes.c_int()
    win_y = ctypes.c_int()
    mask = ctypes.c_uint()
    ok = x11.XQueryPointer(
        display, root, ctypes.byref(root_return), ctypes.byref(child_return),
        ctypes.byref(root_x), ctypes.byref(root_y), ctypes.byref(win_x),
        ctypes.byref(win_y), ctypes.byref(mask),
    )
    if not ok:
        raise X11ClickError("XQueryPointer failed")
    return {"root_x": root_x.value, "root_y": root_y.value}


def viewport_from_root(root_x, root_y, screen_x, screen_y, outer_w, outer_h, inner_w, inner_h):
    """Map root X11 coordinates to browser web-content viewport coordinates.

    This environment has no observed horizontal browser chrome offset; vertical
    chrome offset is derived fresh from outerHeight - innerHeight. The helper
    fails closed if outer/inner geometry is inconsistent.
    """
    chrome_x = outer_w - inner_w
    chrome_y = outer_h - inner_h
    if chrome_x < 0 or chrome_y < 0:
        raise X11ClickError("Invalid outer/inner browser geometry")
    # X chromium edge offset must not be guessed. It is split symmetrically only
    # if a nonzero horizontal delta appears; current measurement is zero.
    content_x = screen_x + chrome_x / 2
    content_y = screen_y + chrome_y
    return {
        "x": root_x - content_x,
        "y": root_y - content_y,
        "content_origin_root": {"x": content_x, "y": content_y},
        "chrome": {"x": chrome_x, "y": chrome_y},
    }


def main(args):
    if len(args) != 14:
        raise SystemExit(__doc__)
    window_id, root_x, root_y, screen_x, screen_y, outer_w, outer_h, inner_w, inner_h, dpr, left, top, width, height = args
    window_id = int(window_id, 0)
    root_x, root_y, screen_x, screen_y, outer_w, outer_h, inner_w, inner_h = map(int, (root_x, root_y, screen_x, screen_y, outer_w, outer_h, inner_w, inner_h))
    dpr, left, top, width, height = map(float, (dpr, left, top, width, height))
    if dpr != 1:
        raise X11ClickError(f"Unsupported DPR {dpr}; coordinate conversion must be explicitly extended")
    if width <= 0 or height <= 0:
        raise X11ClickError("Invalid Generate DOM rectangle")

    x11 = ctypes.CDLL(ctypes.util.find_library("X11"))
    xtst = ctypes.CDLL(ctypes.util.find_library("Xtst"))
    configure_apis(x11, xtst)
    display = x11.XOpenDisplay(os.environ.get("DISPLAY", ":99").encode())
    if not display:
        raise X11ClickError("Could not open X11 display")
    try:
        root = x11.XDefaultRootWindow(display)
        x11.XRaiseWindow(display, window_id)
        x11.XSetInputFocus(display, window_id, 1, 0)
        x11.XSync(display, False)

        before = query_pointer(x11, display, root)
        if not xtst.XTestFakeMotionEvent(display, 0, root_x, root_y, 0):
            raise X11ClickError("XTestFakeMotionEvent failed")
        x11.XSync(display, False)
        moved = query_pointer(x11, display, root)
        viewport = viewport_from_root(moved["root_x"], moved["root_y"], screen_x, screen_y, outer_w, outer_h, inner_w, inner_h)
        inside = left <= viewport["x"] <= left + width and top <= viewport["y"] <= top + height
        evidence = {
            "window_id": hex(window_id), "pointer_before": before,
            "target_root": {"x": root_x, "y": root_y}, "pointer_after_motion": moved,
            "pointer_viewport": {"x": viewport["x"], "y": viewport["y"]},
            "content_origin_root": viewport["content_origin_root"], "chrome_offset": viewport["chrome"],
            "generate_rect": {"left": left, "top": top, "width": width, "height": height},
            "inside_generate_rect": inside,
        }
        print(json.dumps(evidence, ensure_ascii=False))
        if moved != {"root_x": root_x, "root_y": root_y} or not inside:
            raise X11ClickError("Fail closed: pointer does not map inside the Generate DOM rectangle")

        if not xtst.XTestFakeButtonEvent(display, 1, True, 0):
            raise X11ClickError("XTestFakeButtonEvent press failed")
        x11.XSync(display, False)
        time.sleep(0.12)
        if not xtst.XTestFakeButtonEvent(display, 1, False, 0):
            raise X11ClickError("XTestFakeButtonEvent release failed")
        x11.XSync(display, False)
        print(json.dumps({"click_sent": True, "button": 1, "click_count": 1}, ensure_ascii=False))
    finally:
        x11.XCloseDisplay(display)


if __name__ == "__main__":
    main(sys.argv[1:])

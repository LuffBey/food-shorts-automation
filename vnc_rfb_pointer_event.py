#!/usr/bin/env python3
"""Send one standard RFB/VNC PointerEvent sequence to an existing VNC server.

This is a transparent diagnostic helper for the same x11vnc input pipeline used
by noVNC. It does not use CDP mouse input, XTEST, DOM events, stealth,
fingerprint/proxy/VPN changes, CAPTCHA handling, or retries.

Usage:
  python3 vnc_rfb_pointer_event.py HOST PORT X Y [HOLD_MS]

It opens a normal shared RFB 3.8 session, sends:
  PointerEvent(X, Y, buttonMask=0)       # move
  short wait
  PointerEvent(X, Y, buttonMask=1)       # left down
  HOLD_MS wait (default 120ms)
  PointerEvent(X, Y, buttonMask=0)       # left up
"""
import socket
import struct
import sys
import time


class RFBError(RuntimeError):
    pass


def recv_exact(sock, count):
    data = bytearray()
    while len(data) < count:
        chunk = sock.recv(count - len(data))
        if not chunk:
            raise RFBError("VNC server closed the connection")
        data.extend(chunk)
    return bytes(data)


def negotiate_none_security(sock):
    version = recv_exact(sock, 12)
    if not version.startswith(b"RFB "):
        raise RFBError(f"Not an RFB server: {version!r}")
    # x11vnc supports modern RFB negotiation. We deliberately choose standard 3.8.
    sock.sendall(b"RFB 003.008\n")
    count = recv_exact(sock, 1)[0]
    if count == 0:
        length = struct.unpack(">I", recv_exact(sock, 4))[0]
        raise RFBError("VNC security negotiation failed: " + recv_exact(sock, length).decode(errors="replace"))
    types = recv_exact(sock, count)
    if 1 not in types:
        raise RFBError(f"VNC server does not offer standard None authentication: {list(types)}")
    sock.sendall(b"\x01")
    result = struct.unpack(">I", recv_exact(sock, 4))[0]
    if result != 0:
        raise RFBError(f"VNC None authentication rejected with code {result}")


def read_server_init(sock):
    sock.sendall(b"\x01")  # shared session; preserve noVNC user session.
    width, height = struct.unpack(">HH", recv_exact(sock, 4))
    pixel_format = recv_exact(sock, 16)
    name_length = struct.unpack(">I", recv_exact(sock, 4))[0]
    name = recv_exact(sock, name_length).decode(errors="replace")
    return {"framebuffer": {"width": width, "height": height}, "name": name, "pixel_format_bytes": len(pixel_format)}


def pointer_event(sock, x, y, button_mask):
    # RFB Client-to-Server PointerEvent: type=5, padding=0, mask, x, y.
    sock.sendall(struct.pack(">BBHH", 5, button_mask, x, y))


def main(args):
    if len(args) not in (4, 5):
        raise SystemExit(__doc__)
    host, port, x, y = args[:4]
    port, x, y = int(port), int(x), int(y)
    hold_ms = int(args[4]) if len(args) == 5 else 120
    if not (0 <= x <= 65535 and 0 <= y <= 65535):
        raise RFBError("RFB coordinates must fit unsigned 16-bit values")
    if not (100 <= hold_ms <= 1000):
        raise RFBError("Hold time must be 100–1000ms")

    with socket.create_connection((host, port), timeout=10) as sock:
        sock.settimeout(10)
        negotiate_none_security(sock)
        init = read_server_init(sock)
        if x >= init["framebuffer"]["width"] or y >= init["framebuffer"]["height"]:
            raise RFBError(f"Target {(x, y)} is outside framebuffer {init['framebuffer']}")
        pointer_event(sock, x, y, 0)
        time.sleep(0.12)
        pointer_event(sock, x, y, 1)
        time.sleep(hold_ms / 1000)
        pointer_event(sock, x, y, 0)
        print({
            "rfb_version": "3.8", "security": "None", "shared": True,
            "server": init, "sequence": [
                {"type": "PointerEvent", "x": x, "y": y, "buttonMask": 0},
                {"type": "PointerEvent", "x": x, "y": y, "buttonMask": 1, "hold_ms": hold_ms},
                {"type": "PointerEvent", "x": x, "y": y, "buttonMask": 0},
            ],
        })


if __name__ == "__main__":
    main(sys.argv[1:])

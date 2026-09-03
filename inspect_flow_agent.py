import socket
import json
import base64
import os
import time
import urllib.request

class FlowClient:
    def __init__(self, port=9222):
        self.port = port
        self.connect()

    def connect(self):
        pages = json.loads(urllib.request.urlopen(f'http://127.0.0.1:{self.port}/json/list').read().decode())
        flow_page = next((p for p in pages if 'flow/project' in p.get('url', '')), None)
        if not flow_page:
            flow_page = pages[0]
        ws_url = flow_page['webSocketDebuggerUrl']
        path = ws_url.split(str(self.port))[1]
        
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(('127.0.0.1', self.port))
        key = base64.b64encode(os.urandom(16)).decode('utf-8')
        req = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: 127.0.0.1:{self.port}\r\n"
            f"Upgrade: websocket\r\n"
            f"Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        self.s.sendall(req.encode())
        self.s.recv(4096)
        self.msg_id = 0

    def _send(self, text):
        data = text.encode('utf-8')
        length = len(data)
        frame = bytearray([0x81])
        if length <= 125:
            frame.append(0x80 | length)
        elif length <= 65535:
            frame.append(0x80 | 126)
            frame.extend(length.to_bytes(2, 'big'))
        mask = os.urandom(4)
        frame.extend(mask)
        masked_data = bytearray(b ^ mask[i % 4] for i, b in enumerate(data))
        frame.extend(masked_data)
        self.s.sendall(frame)

    def _recv(self):
        head = self.s.recv(2)
        if not head: return None
        length = head[1] & 0x7F
        if length == 126:
            length = int.from_bytes(self.s.recv(2), 'big')
        elif length == 127:
            length = int.from_bytes(self.s.recv(8), 'big')
        data = bytearray()
        while len(data) < length:
            chunk = self.s.recv(length - len(data))
            if not chunk: break
            data.extend(chunk)
        return data.decode('utf-8', errors='ignore')

    def cdp(self, method, params=None):
        self.msg_id += 1
        curr_id = self.msg_id
        payload = {'id': curr_id, 'method': method}
        if params: payload['params'] = params
        self._send(json.dumps(payload))
        while True:
            res_str = self._recv()
            if not res_str: break
            try:
                res = json.loads(res_str)
                if res.get('id') == curr_id:
                    return res
            except:
                pass
        return None

    def eval(self, expr):
        res = self.cdp('Runtime.evaluate', {'expression': expr, 'returnByValue': True, 'awaitPromise': True})
        return res.get('result', {}).get('result', {}).get('value')

    def screenshot(self, path):
        res = self.cdp('Page.captureScreenshot', {'format': 'png'})
        if res and 'result' in res and 'data' in res['result']:
            with open(path, 'wb') as f:
                f.write(base64.b64decode(res['result']['data']))
            print(f"Screenshot saved to {path}")

if __name__ == '__main__':
    c = FlowClient()
    print("Page Title:", c.eval("document.title"))
    print("Page URL:", c.eval("window.location.href"))
    
    # Inspect visible buttons, agent controls, tabs
    info = c.eval("""
    (() => {
        const buttons = Array.from(document.querySelectorAll('button, div[role="button"], span[role="button"], a[role="button"], div[contenteditable="true"]'))
            .map(b => ({
                tag: b.tagName,
                text: b.innerText ? b.innerText.trim() : '',
                ariaLabel: b.getAttribute('aria-label') || '',
                role: b.getAttribute('role') || '',
                className: b.className || ''
            })).filter(b => b.text || b.ariaLabel);
        return {
            buttons: buttons.slice(0, 50),
            allText: document.body.innerText.slice(0, 1000)
        };
    })()
    """)
    print("UI Info:", json.dumps(info, indent=2, ensure_ascii=False))
    c.screenshot('/root/hermes-projects/food-discovery-automation/flow_agent_initial.png')

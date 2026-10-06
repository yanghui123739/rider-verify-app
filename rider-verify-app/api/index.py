from http.server import BaseHTTPRequestHandler
import json
import os
import requests

# ⚠️ 注意：请确认这个地址和你 Coze 部署页面上的地址完全一致
COZE_API_URL = "https://5b9drw8vkm.coze.site/run"
COZE_TOKEN = os.environ.get("COZE_API_TOKEN")

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            image_data = data.get("image_data", "")

            if not image_data:
                self._send_json(400, {"error": "缺少图片数据"})
                return

            payload = {
                "order_image": {
                    "url": image_data,
                    "file_type": "image"
                }
            }

            headers = {
                "Authorization": f"Bearer {COZE_TOKEN}",
                "Content-Type": "application/json"
            }

            resp = requests.post(COZE_API_URL, json=payload, headers=headers, timeout=60)

            if resp.status_code != 200:
                self._send_json(resp.status_code, {"error": f"Coze 返回错误: {resp.text}"})
                return

            result = resp.json()
            self._send_json(200, result)

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

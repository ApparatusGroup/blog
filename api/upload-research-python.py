import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            data = json.loads(raw)

            title = (data.get("title") or "").strip()
            content = (data.get("content") or "").strip()
            user_id = (data.get("userId") or "").strip()

            if not title or not content or not user_id:
                return self._send(400, {"error": "Missing required fields"})

            root = Path(__file__).resolve().parent.parent
            os.chdir(root)
            if str(root) not in os.sys.path:
                os.sys.path.insert(0, str(root))

            from src.publisher import Publisher

            publisher = Publisher()
            publisher.publish({"title": title, "markdown": content})

            return self._send(200, {
                "success": True,
                "message": f"Article \"{title}\" published successfully"
            })
        except Exception as exc:
            return self._send(500, {
                "error": "Failed to publish article",
                "details": str(exc)
            })

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

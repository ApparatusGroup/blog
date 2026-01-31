import json
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path

MAX_BYTES = 3 * 1024 * 1024


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
            if content_length > MAX_BYTES:
                return self._send(413, {
                    "success": False,
                    "error": "Payload too large. Reduce total document size or number of sources and try again."
                })

            raw = self.rfile.read(content_length).decode("utf-8") if content_length else "{}"
            data = json.loads(raw)

            topic = (data.get("topic") or "").strip()
            if not topic:
                return self._send(400, {"success": False, "error": "Topic is required"})

            root = Path(__file__).resolve().parent.parent
            os.chdir(root)
            if str(root) not in os.sys.path:
                os.sys.path.insert(0, str(root))

            from src.advanced_writer import AdvancedWriter

            writer = AdvancedWriter()
            result = writer.generate(data)

            return self._send(200, {
                "success": True,
                "title": result.get("title", topic),
                "message": "Article generated and published successfully"
            })
        except Exception as exc:
            return self._send(500, {
                "success": False,
                "error": "Generation failed",
                "details": str(exc)
            })

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

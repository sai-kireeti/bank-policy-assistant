"""Bank Policy Assistant - simple backend server.

This server uses only the Python standard library, so it runs with
no install step. It serves the frontend page and one API route.

Routes:
  GET  /            -> static/index.html
  POST /api/ask     -> body: {"question": "..."}  returns answer and source
  GET  /api/ask?q=  -> same, for a quick test in the browser

Run it with:  python3 app.py
Then open:    http://127.0.0.1:8000
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from rag import ask

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "static", "index.html")
PORT = int(os.environ.get("PORT", "8000"))


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/ask":
            params = parse_qs(parsed.query)
            question = (params.get("q") or [""])[0]
            self._send_json(ask(question))
            return
        # Serve the frontend for / and /index.html, and for any other path
        # fall back to the frontend so the demo is easy to open.
        try:
            with open(INDEX_FILE, "rb") as fh:
                body = fh.read()
        except FileNotFoundError:
            self._send_json({"error": "index.html not found"}, status=404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/ask":
            self._send_json({"error": "not found"}, status=404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            data = json.loads(raw.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, status=400)
            return
        self._send_json(ask(str(data.get("question", ""))))

    def log_message(self, format, *args):
        # Keep the console clean and simple.
        print("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Bank Policy Assistant running at http://127.0.0.1:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json

HOST = "0.0.0.0"
PORT = 8000
BASE_DIR = Path(__file__).resolve().parent

PLANS = [
    {
        "name": "Starter",
        "price_eur": 6.90,
        "ram_gb": 2,
        "cpu_vcores": 1,
        "storage_gb": 20,
        "support": "Email (24h)",
        "best_for": "Bot piccoli e progetti personali",
    },
    {
        "name": "Pro",
        "price_eur": 14.90,
        "ram_gb": 6,
        "cpu_vcores": 2,
        "storage_gb": 60,
        "support": "Prioritario Discord + Email",
        "best_for": "Community attive e bot in produzione",
    },
    {
        "name": "Enterprise",
        "price_eur": 34.90,
        "ram_gb": 16,
        "cpu_vcores": 4,
        "storage_gb": 160,
        "support": "SLA dedicato + onboarding tecnico",
        "best_for": "Agenzie, SaaS e bot ad alto traffico",
    },
]


class BotHostHandler(BaseHTTPRequestHandler):
    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self.send_error(404, "Not found")
            return

        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            return self._send_file(BASE_DIR / "templates" / "index.html", "text/html; charset=utf-8")

        if self.path == "/static/styles.css":
            return self._send_file(BASE_DIR / "static" / "styles.css", "text/css; charset=utf-8")

        if self.path == "/static/script.js":
            return self._send_file(BASE_DIR / "static" / "script.js", "application/javascript; charset=utf-8")

        if self.path == "/api/plans":
            payload = json.dumps({"plans": PLANS}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_error(404, "Not found")


def run() -> None:
    server = ThreadingHTTPServer((HOST, PORT), BotHostHandler)
    print(f"BotHost Pro disponibile su http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    run()

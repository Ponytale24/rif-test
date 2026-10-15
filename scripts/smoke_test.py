"""Smoke-test a running RoX Hello World container (UI + REST API).

Usage:
    python scripts/smoke_test.py                       # http://localhost:8090
    python scripts/smoke_test.py http://host:port
"""

import json
import sys
import time
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8090").rstrip("/")


def request(method: str, path: str, body: dict | None = None) -> tuple[int, str]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        return res.status, res.read().decode()


def wait_for_health(timeout: float = 60) -> None:
    deadline = time.monotonic() + timeout
    while True:
        try:
            if request("GET", "/api/health")[0] == 200:
                return
        except OSError:
            pass
        if time.monotonic() > deadline:
            raise SystemExit(f"FAIL: {BASE}/api/health not reachable after {timeout}s")
        time.sleep(1)


def main() -> None:
    print(f"Testing {BASE}")
    wait_for_health()

    checks = []

    status, body = request("GET", "/")
    checks.append(("GET /  (UI)", status == 200 and "Hello World from RoX" in body))

    status, body = request("GET", "/api/health")
    checks.append(("GET /api/health", status == 200 and json.loads(body)["status"] == "ok"))

    status, body = request("GET", "/api/hello?name=KIT")
    checks.append(("GET /api/hello?name=KIT", status == 200 and json.loads(body)["message"] == "Hello, KIT!"))
    print("  /api/hello ->", body)

    status, body = request("POST", "/api/echo", {"message": "ping"})
    checks.append(("POST /api/echo", status == 200 and json.loads(body)["echo"] == "ping"))

    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not all(ok for _, ok in checks):
        raise SystemExit(1)
    print("All checks passed.")


if __name__ == "__main__":
    main()

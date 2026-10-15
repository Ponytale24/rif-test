"""RoX Hello World asset: a tiny web UI plus a REST API.

Stands in for a real (much heavier) application so the RoX KIT flow
source archive -> build -> run can be tested end to end.
"""

import os
import platform
import socket
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

APP_NAME = "rox-hello-world"
APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")
STARTED_AT = datetime.now(timezone.utc)

app = FastAPI(
    title="RoX Hello World",
    version=APP_VERSION,
    description="Minimal containerised test asset for the RoX KIT framework.",
)


class EchoRequest(BaseModel):
    message: str


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}


@app.get("/api/hello")
def hello(name: str = "RoX") -> dict:
    return {
        "message": f"Hello, {name}!",
        "app": APP_NAME,
        "version": APP_VERSION,
        "hostname": socket.gethostname(),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/echo")
def echo(request: EchoRequest) -> dict:
    return {"echo": request.message, "length": len(request.message)}


@app.get("/api/info")
def info() -> dict:
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "python": platform.python_version(),
        "platform": f"{platform.system().lower()}/{platform.machine()}",
        "started_at": STARTED_AT.isoformat(),
    }


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RoX Hello World</title>
  <style>
    :root { color-scheme: light dark; --accent: #2563eb; }
    body { font-family: system-ui, sans-serif; max-width: 640px; margin: 3rem auto; padding: 0 1rem; line-height: 1.5; }
    h1 { margin-bottom: .25rem; }
    .muted { opacity: .7; }
    form { display: flex; gap: .5rem; margin: 1.5rem 0 1rem; }
    input { flex: 1; padding: .5rem; font-size: 1rem; }
    button { padding: .5rem 1rem; font-size: 1rem; background: var(--accent); color: #fff; border: 0; border-radius: 4px; cursor: pointer; }
    pre { background: rgba(127,127,127,.12); padding: 1rem; border-radius: 4px; overflow-x: auto; }
    ul { padding-left: 1.2rem; }
  </style>
</head>
<body>
  <h1>Hello World from RoX</h1>
  <p class="muted">Version __VERSION__ &middot; deployed via a RoX KIT</p>

  <form id="hello-form">
    <input id="name" value="RoX" aria-label="Name">
    <button type="submit">Call /api/hello</button>
  </form>
  <pre id="out">Click the button to send a request to the REST API.</pre>

  <h2>API</h2>
  <ul>
    <li><code>GET /api/health</code></li>
    <li><code>GET /api/hello?name=...</code></li>
    <li><code>POST /api/echo</code> with <code>{"message": "..."}</code></li>
    <li><code>GET /api/info</code></li>
    <li><a href="/docs">OpenAPI docs (/docs)</a></li>
  </ul>

  <script>
    document.getElementById("hello-form").addEventListener("submit", async (e) => {
      e.preventDefault();
      const name = document.getElementById("name").value;
      const out = document.getElementById("out");
      try {
        const res = await fetch("/api/hello?name=" + encodeURIComponent(name));
        out.textContent = JSON.stringify(await res.json(), null, 2);
      } catch (err) {
        out.textContent = "Request failed: " + err;
      }
    });
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return INDEX_HTML.replace("__VERSION__", APP_VERSION)

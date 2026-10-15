# RoX Hello World – containerised test service

**RoX Hello World** is a minimal containerised software component that serves a
"Hello World" web user interface and a small HTTP REST API. It is a lightweight
stand-in for larger containerised robotics applications (for example ML-based
perception services with heavy dependencies). Use it to test the RoX KIT
workflow end to end: the asset is shipped as a source archive, built into a
Docker image by the KIT backend, started as a container, and then checked
through its web UI and REST API.

The asset has no robot, sensor, or ML model dependencies. It needs no input
data and stores no data.

## Asset summary

| Property | Value |
|---|---|
| Title | RoX Hello World |
| Identifier | `rox-hello-world` |
| Version | 0.1.0 |
| Asset kind | Software component (containerised web service) |
| Purpose | Test and demo asset for the RoX KIT framework (asset → KIT → run) |
| Keywords | RoX, KIT, hello world, test asset, REST API, web UI, Docker, container, FastAPI, Python |
| Publisher | *REPLACE: your organisation* |
| Contact point | *REPLACE: mailto:your-team@example.com* |
| License | MIT (https://opensource.org/licenses/MIT) |
| Technology readiness level (TRL) | 4 – validated in a lab environment |
| Relevant use cases | Testing the RoX KIT container workflow; onboarding new asset providers; verifying a KIT framework installation |
| Depends on | none |
| Produces asset | none |

## Delivery (operational metadata)

| Property | Value |
|---|---|
| Operational type | `container` |
| Distribution type | `archive` (source archive: a ZIP file containing the source code and exactly one `Dockerfile`; KIT representation `source_archive`) |
| Archive file | `rox-hello-world-src.zip` (ZIP, about 5 KB) |
| Image name | `rox-hello-world` |
| Image tag | `0.1.0` |
| Platforms | `linux/amd64`, `linux/arm64` |
| Base image | `python:3.12-slim` |
| Container port | `8000/tcp` (HTTP) |
| Suggested host port | `8090` |

The KIT backend downloads the archive, finds the single `Dockerfile`, and runs
`docker build` in its folder. Build arguments: `APP_VERSION` (default
`0.1.0`). Environment variables at runtime: `PORT` (default `8000`) and
`APP_VERSION`.

Run the container after the build:

```bash
docker run -d --name rox-hello-world -p 8090:8000 rox-hello-world:0.1.0
```

## Interfaces

Interface protocol: **REST** over HTTP, JSON responses. OpenAPI documentation
is generated at `/docs` (Swagger UI) and `/openapi.json`.

| Method | Path | Description | Response |
|---|---|---|---|
| GET | `/` | Hello World web UI with a button that calls the API | `text/html` |
| GET | `/api/health` | Health check | `{"status": "ok", "app": "rox-hello-world", "version": "0.1.0"}` |
| GET | `/api/hello?name=<text>` | Returns a greeting | `{"message": "Hello, <text>!", "app": ..., "version": ..., "hostname": ..., "timestamp": ...}` |
| POST | `/api/echo` | Echoes a JSON body `{"message": "<text>"}` | `{"echo": "<text>", "length": <int>}` |
| GET | `/api/info` | Version, Python version, platform and start time | `application/json` |
| GET | `/docs` | OpenAPI / Swagger UI | `text/html` |

Example requests:

```bash
curl http://localhost:8090/api/health
curl "http://localhost:8090/api/hello?name=RoX"
curl -X POST http://localhost:8090/api/echo -H "Content-Type: application/json" -d '{"message": "ping"}'
```

Inputs and outputs:

- Setup inputs: none (only the source archive)
- Setup outputs: Docker image `rox-hello-world:0.1.0`
- Runtime inputs: HTTP requests (query parameter `name`, JSON body `message`)
- Runtime outputs: HTML page and JSON responses
- Required object knowledge: none
- Supports continuous learning: no

## Requirements

Hardware requirements:

- `hardware.cpu.architecture in {amd64, arm64}`
- `hardware.memory >= 256 MB`
- `hardware.storage >= 300 MB` (image size, about 200 MB)
- No GPU, robot, sensor, or other device required

Software requirements:

- `software.runtime.docker required` (Docker Engine with BuildKit or the classic builder)
- `software.os = linux` (Linux containers; Docker Desktop on Windows/macOS works)
- `software.network.internet required for docker build` (pulls `python:3.12-slim` and PyPI packages `fastapi`, `uvicorn`)
- `software.network.port 8090 available` (host port; change it in the `docker run` command if taken)

Dataspace requirements:

- `dataspace.connector.dlr required`
- `dataspace.negotiation.dlr required for rox-hello-world-src.zip`

## Source layout

```
rox-hello-world/
├── Dockerfile          # the only Dockerfile in the archive
├── requirements.txt    # fastapi, uvicorn
└── app/
    └── main.py         # FastAPI application (UI + REST API)
```

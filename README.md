# RoX KIT demo: Hello World container asset

This demo tests the RoX ecosystem end to end with a tiny containerised Python
service that stands in for our real (much larger) application:

1. **Asset**: a FastAPI app with a Hello World web UI and a REST API, shipped
   as a **container / `source_archive`** (a ZIP containing a `Dockerfile`).
2. **Semantic model**: generated with RODEOS from
   [hello-asset/README.md](hello-asset/README.md).
3. **KIT**: pulls the archive from the dataspace, builds the image, starts the
   container, and runs a smoke test against the API.
4. **Check**: open the UI and send a request to the API.

Manual: https://rox-architecture.github.io/kit-user-manual/

## Repository layout

```
rif-test/
├── hello-asset/                 # the asset (this folder is what gets zipped)
│   ├── Dockerfile               # the ONLY Dockerfile in the repo (see below)
│   ├── requirements.txt
│   ├── app/main.py              # UI (/) + REST API (/api/*) + OpenAPI (/docs)
│   └── README.md                # asset description -> paste into RODEOS
├── kit/rox-hello-world-kit.json # KIT graph to import into the KIT GUI
├── scripts/
│   ├── package_asset.py         # build + validate dist/rox-hello-world-src.zip
│   ├── smoke_test.py            # test UI + API of a running container
│   └── local_kit_run.py         # dry-run the KIT locally, without the dataspace
└── dist/rox-hello-world-src.zip # generated
```

## How the KIT handles a `source_archive`

This comes from the KIT backend source
([`container_image.py`](https://github.com/rox-architecture/kit-framework-backend/blob/main/src/cee/node_plugins/dlr_dataspace/container_image.py)),
not the manual, which says little about it:

- The archive must be **ZIP or TAR**.
- It must contain **exactly one file named `Dockerfile`**, at any depth. Zero
  or two or more make the node fail. That is why the repo contains only one,
  so a GitHub "Download ZIP" of the whole repo also works.
- The build context is **the folder that contains the `Dockerfile`**. The
  image is tagged `image_name:image_tag` from the node parameters.
- The Docker daemon platform (for example `linux/amd64`) must be listed in the
  node's `platforms`.
- The container node **only builds** the image. Starting it is a separate
  **Bash Command** node (`docker run ...`). That node runs inside the KIT
  worker container but talks to the **host** Docker daemon through the mounted
  socket, so `-p 8090:8000` publishes on the host, and the UI is at
  `http://localhost:8090`.
- The worker's `localhost` is not the host's. The smoke-test node therefore
  uses `docker exec rox-hello-world ...` instead of `curl localhost:8090`.

Ports used by the KIT framework itself: 8080 (API), 8088 (GUI), 8087
(catalog), 5432 (Postgres). The demo uses **8090**.

---

## Step 0: Test locally (no RoX needed)

```bash
docker build -t rox-hello-world:0.1.0 hello-asset
```

```bash
docker run -d --name rox-hello-world -p 8090:8000 rox-hello-world:0.1.0
```

```bash
python scripts/smoke_test.py http://localhost:8090
```

Open http://localhost:8090 (UI) and http://localhost:8090/docs (API docs).
Clean up:

```bash
docker rm -f rox-hello-world
```

## Step 1: Build the source archive

```bash
python scripts/package_asset.py
```

This writes `dist/rox-hello-world-src.zip` and checks it the way the backend
does (exactly one `Dockerfile`, build context found). It also prints the size
and SHA-256. Use `--check some.zip` to validate any other archive, such as a
GitHub ZIP of our real application.

Optional: dry-run the whole KIT locally. This uses the local ZIP instead of
the dataspace, builds the image, and runs both Bash nodes from
`kit/rox-hello-world-kit.json`:

```bash
python scripts/local_kit_run.py
```

The smoke-test output lands in `artifacts/rox-hello-world/smoke-test.json`.

## Step 2: Publish the archive at a URL

The dataspace needs an accessible URL for the asset. Pick one:

- **GitHub release asset (recommended)**: push this repo, create a release,
  and attach `dist/rox-hello-world-src.zip`. URL:
  `https://github.com/<org>/<repo>/releases/download/v0.1.0/rox-hello-world-src.zip`
- **GitHub repo ZIP**: `https://github.com/<org>/<repo>/archive/refs/heads/main.zip`.
  This works because the repo has exactly one `Dockerfile`.
- Any other HTTP(S) location the DLR connector can reach.

## Step 3: Generate the semantic model with RODEOS

1. Open https://dataspace-dev-wallet.base-x-ecosystem.org/rodeos
2. Paste the **full content of [hello-asset/README.md](hello-asset/README.md)**
   into the text box and generate. First replace the *Publisher* and
   *Contact point* placeholders.
3. Check the generated values, especially these:

   | Field | Expected |
   |---|---|
   | `rodeos:coreType` | `Component` |
   | `rodeos:componentType` | `softwareComponent` |
   | `rodeos:softwareAssetType` | e.g. `integrationOrchestration` (no "test" type exists; pick what fits our real app) |
   | `rodeos:capabilityClass` | e.g. `processExecution` |
   | `rodeos:interfaceProtocols` | `REST` |
   | `rodeos:operationalType` | `container` |
   | `rodeos:distributionType` | `archive` |
   | `rodeos:imageName` / `rodeos:imageTag` | `rox-hello-world` / `0.1.0` |
   | `rodeos:platforms` | `linux/amd64`, `linux/arm64` |
   | `dcterms:license` | as you choose (README says MIT) |

4. Copy the resulting JSON.

## Step 4: Register the asset in the DLR dataspace

1. Log in to the DLR dataspace Web UI and open **My Assets**.
2. Paste the archive URL from Step 2 and click **Add Asset**.
3. Enable search engine metadata, click **import JSON**, paste the RODEOS JSON,
   and click **Apply**.
4. Fill in the required fields (filename `rox-hello-world-src.zip`,
   description).
5. Select policy **`group-rox-only`** and create the asset.
6. Note the **asset ID**, your **BPN**, and your **connector name**. Step 6
   needs them.

## Step 5: Install the KIT framework

Follow https://rox-architecture.github.io/kit-user-manual/installation/
(`kit-framework-deployment`, `.env` with `BASE_URL_DLR_CONNECTOR`,
`API_KEY_DLR_CONNECTOR`, `DOCKER_SOCKET_HOST`, `ARTIFACT_HOST_ROOT`, then
`docker compose --profile gui up -d`). The GUI is at http://localhost:8088.

## Step 6: Create the KIT

**Option A: import the prepared KIT.** In
[kit/rox-hello-world-kit.json](kit/rox-hello-world-kit.json), replace
`REPLACE_WITH_PROVIDER_BPN`, `REPLACE_WITH_CONNECTOR_NAME`, and
`REPLACE_WITH_ASSET_ID`. Then click **Import** in the GUI.

**Option B: build it in the GUI.** Add these nodes and connect them with
`dep → dep` edges in this order:

1. **CONTAINER** `rox-hello-world-src.zip`: `representation = source_archive`,
   `image_name = rox-hello-world`, `image_tag = 0.1.0`,
   `platforms = linux/amd64, linux/arm64`.
2. **Bash Command** "Run Hello World container":
   ```bash
   docker rm -f rox-hello-world >/dev/null 2>&1 || true
   docker run -d --name rox-hello-world --restart unless-stopped -p 8090:8000 rox-hello-world:0.1.0
   ```
3. **Bash Command** "Smoke test API": copy the `command` from the KIT JSON. It
   polls `/api/hello` through `docker exec` and writes
   `rox-hello-world/smoke-test.json` into the artifact root.

Then click **Save Graph** and check **Consolidated Requirements**.

## Step 7: Run the KIT and test

1. Negotiate `rox-hello-world-src.zip` (it shows a hand-shake icon when done).
2. Open the backend terminal (monitor icon) and switch to **Worker 1**.
3. Click **play**. Expect the log lines `Building image rox-hello-world:0.1.0`,
   then `Image stored locally`, then the container ID, then `API answered: {...}`.
4. Test:
   - UI: http://localhost:8090. Click **Call /api/hello**.
   - API:
     ```bash
     curl "http://localhost:8090/api/hello?name=KIT"
     ```
   - Or all checks at once:
     ```bash
     python scripts/smoke_test.py
     ```
   - Artifact explorer (folder icon): `rox-hello-world/smoke-test.json`
5. Clean up:
   ```bash
   docker rm -f rox-hello-world
   ```

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `Multiple Dockerfiles found in archive` | The archive has more than one file named `Dockerfile`. Rename the extras (e.g. `Dockerfile.dev`) or zip only the app folder. |
| `does not support Docker daemon platform` | Add the daemon's platform (`docker info` → OSType/Architecture) to `platforms`. |
| `port is already allocated` | Change `-p 8090:8000` in the run node (and the URLs). |
| No output in Worker 1 | Wrong `DOCKER_SOCKET_HOST` in the KIT `.env`. |
| Build fails on `pip install` | The host running the KIT needs internet access during the build. |

## Notes for the real application

- The source archive is built **on the consumer's machine** at KIT run time,
  so build time and network access (PyPI, base images) count against the run.
  For heavy ML dependencies, consider a slim archive whose `Dockerfile` pulls
  large model weights at build time. Another option is to ship the weights as
  separate `static_file` assets and mount them with `-v` in the run node, as
  the robot-arm example in the manual does.
- Keep exactly one `Dockerfile` in the archive.
- GPU: add `--gpus all` to the run node and a hardware requirement such as
  `hardware.compute.gpu required` to the asset README.

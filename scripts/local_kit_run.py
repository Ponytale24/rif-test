"""Dry-run the KIT locally, without the dataspace or the KIT framework.

Executes kit/rox-hello-world-kit.json in dependency order the way the KIT
backend would, except that the `dlr.container` node uses the local
dist/rox-hello-world-src.zip instead of pulling the asset from the dataspace:

  * dlr.container (source_archive): extract ZIP, find the single Dockerfile,
    `docker build` with its folder as context, tag image_name:image_tag
  * bash_command: run the command with `bash -lc`, ARTIFACT_ROOT=./artifacts

Usage:
    python scripts/package_asset.py
    python scripts/local_kit_run.py [--bash PATH_TO_BASH]
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import zipfile
from graphlib import TopologicalSorter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KIT_FILE = ROOT / "kit" / "rox-hello-world-kit.json"
ARCHIVE = ROOT / "dist" / "rox-hello-world-src.zip"
ARTIFACT_ROOT = ROOT / "artifacts"


def run_container_node(params: dict) -> None:
    if params["representation"] != "source_archive":
        raise SystemExit(f"local dry-run only supports source_archive, got {params['representation']!r}")
    if not ARCHIVE.exists():
        raise SystemExit(f"{ARCHIVE} missing - run scripts/package_asset.py first")

    tag = f"{params['image_name']}:{params['image_tag']}"
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(ARCHIVE) as zf:
            zf.extractall(tmp)
        dockerfiles = list(Path(tmp).rglob("Dockerfile"))
        if len(dockerfiles) != 1:
            raise SystemExit(f"expected exactly one Dockerfile, found {len(dockerfiles)}")
        print(f"Building image {tag}", flush=True)
        subprocess.run(["docker", "build", "-t", tag, str(dockerfiles[0].parent)], check=True)


def run_bash_node(params: dict, bash: str) -> None:
    env = {**os.environ, "ARTIFACT_ROOT": ARTIFACT_ROOT.as_posix(), "MSYS_NO_PATHCONV": "1"}
    subprocess.run([bash, "-lc", params["command"]], check=True, env=env,
                   timeout=params.get("timeout_seconds"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bash", default=shutil.which("bash"), help="bash executable (Git Bash on Windows)")
    args = parser.parse_args()
    if not args.bash:
        raise SystemExit("bash not found; pass --bash")

    kit = json.loads(KIT_FILE.read_text(encoding="utf-8"))
    nodes = {n["id"]: n for n in kit["nodes"]}
    graph = {node_id: set() for node_id in nodes}
    for edge in kit["edges"]:
        graph[edge["target"]].add(edge["source"])

    ARTIFACT_ROOT.mkdir(exist_ok=True)
    for node_id in TopologicalSorter(graph).static_order():
        node = nodes[node_id]
        params = node["data"]["params"]
        print(f"\n=== {node['data']['label']} ({params['type']}) ===", flush=True)
        if params["type"] == "dlr.container":
            run_container_node(params)
        elif params["type"] == "bash_command":
            run_bash_node(params, args.bash)
        else:
            raise SystemExit(f"node type {params['type']!r} not supported in local dry-run")

    print("\nKIT dry-run finished.")


if __name__ == "__main__":
    main()

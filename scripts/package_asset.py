"""Package hello-asset/ into a RoX `source_archive` (ZIP) and check it.

The check mirrors what the KIT backend does with a source archive
(kit-framework-backend, node_plugins/dlr_dataspace/container_image.py):
extract it, require exactly one file named "Dockerfile", and use that
file's directory as the Docker build context.

Usage:
    python scripts/package_asset.py            # writes dist/rox-hello-world-src.zip
    python scripts/package_asset.py --check FILE.zip   # only check an archive
"""

import argparse
import hashlib
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT / "hello-asset"
DIST_DIR = ROOT / "dist"
ARCHIVE_NAME = "rox-hello-world-src.zip"
TOP_LEVEL = "rox-hello-world"  # same layout as a GitHub "Download ZIP"
EXCLUDE_PARTS = {"__pycache__", ".venv", ".pytest_cache"}


def build_archive(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(
        p for p in ASSET_DIR.rglob("*")
        if p.is_file() and not EXCLUDE_PARTS.intersection(p.parts) and p.suffix != ".pyc"
    )
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = f"{TOP_LEVEL}/{path.relative_to(ASSET_DIR).as_posix()}"
            zf.write(path, arcname)
            print(f"  + {arcname}")


def check_archive(archive: Path) -> Path:
    """Return the build context relative to the archive root, like the backend."""
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp).resolve()
        with zipfile.ZipFile(archive) as zf:
            for member in zf.infolist():
                if not (dest / member.filename).resolve().is_relative_to(dest):
                    raise SystemExit(f"Unsafe path in archive: {member.filename!r}")
            zf.extractall(dest)

        dockerfiles = [p for p in dest.rglob("Dockerfile") if p.is_file()]
        if not dockerfiles:
            raise SystemExit("FAIL: no Dockerfile in archive")
        if len(dockerfiles) > 1:
            found = ", ".join(str(p.relative_to(dest)) for p in dockerfiles)
            raise SystemExit(f"FAIL: multiple Dockerfiles in archive: {found}")
        return dockerfiles[0].parent.relative_to(dest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", type=Path, help="only validate an existing archive")
    args = parser.parse_args()

    archive = args.check
    if archive is None:
        archive = DIST_DIR / ARCHIVE_NAME
        print(f"Packaging {ASSET_DIR} -> {archive}")
        build_archive(archive)

    context = check_archive(archive)
    sha256 = hashlib.sha256(archive.read_bytes()).hexdigest()
    print(f"OK: exactly one Dockerfile, build context = {context.as_posix()}/")
    print(f"size   = {archive.stat().st_size} bytes")
    print(f"sha256 = {sha256}")


if __name__ == "__main__":
    sys.exit(main())

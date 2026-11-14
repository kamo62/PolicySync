"""Standard-library-only installer; never reaches an index or downloads Python."""

import hashlib
import json
import platform
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def verify():
    manifest = json.loads((ROOT / "vendor/manifest.json").read_text())
    for name, digest in manifest["files"].items():
        path = ROOT / name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise SystemExit(f"Offline bundle integrity check failed: {name}")
    return manifest


def main():
    verify()
    if (
        sys.version_info[:2] != (3, 12)
        or platform.system() != "Linux"
        or platform.machine() not in {"x86_64", "AMD64"}
    ):
        raise SystemExit("This wheel bundle requires Linux x86_64 and CPython 3.12")
    libc, version = platform.libc_ver()
    if libc != "glibc" or tuple(map(int, version.split(".")[:2])) < (2, 28):
        raise SystemExit("This wheel bundle requires glibc 2.28 or newer (not Alpine/musl)")
    destination = ROOT / ".venv"
    if destination.exists():
        raise SystemExit(".venv already exists. Reuse it or move it aside before a fresh install")
    venv.EnvBuilder(with_pip=False).create(destination)
    python = destination / "bin/python"
    wheels = ROOT / "vendor/wheels/linux-x86_64"
    (pip_wheel,) = wheels.glob("pip-*.whl")
    bootstrap = (
        "import runpy,sys; sys.path.insert(0,sys.argv.pop(1)); "
        "runpy.run_module('pip',run_name='__main__')"
    )
    subprocess.run(
        [
            str(python),
            "-c",
            bootstrap,
            str(pip_wheel),
            "--isolated",
            "install",
            "--no-index",
            "--no-cache-dir",
            "--disable-pip-version-check",
            "--find-links",
            str(wheels),
            "--require-hashes",
            "-r",
            str(ROOT / "vendor/requirements-linux.txt"),
            "-r",
            str(ROOT / "vendor/bootstrap-pip.txt"),
        ],
        check=True,
        cwd=ROOT,
    )
    print("Offline environment installed. Run .venv/bin/python -m pytest -q")


if __name__ == "__main__":
    main()

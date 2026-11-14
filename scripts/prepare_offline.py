"""Online maintainer command: uv run --with pip python -m scripts.prepare_offline."""

import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

from packaging.markers import default_environment
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run(
        [
            "uv",
            "export",
            "--frozen",
            "--no-emit-project",
            "--no-annotate",
            "--no-header",
            "--output-file",
            "requirements.txt",
        ],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    environment = default_environment()
    environment.update(
        sys_platform="linux",
        platform_system="Linux",
        platform_machine="x86_64",
        python_version="3.12",
        python_full_version="3.12.0",
    )
    blocks = []
    for block in re.split(r"\n(?=\S)", (ROOT / "requirements.txt").read_text().strip()):
        first, *rest = block.splitlines()
        requirement = Requirement(first.rstrip("\\ "))
        if requirement.marker is None or requirement.marker.evaluate(environment):
            requirement.marker = None
            blocks.append(str(requirement) + (" \\\n" + "\n".join(rest) if rest else ""))
    target_requirements = ROOT / "vendor/requirements-linux.txt"
    target_requirements.write_text("\n".join(blocks) + "\n")
    wheels = ROOT / "vendor/wheels/linux-x86_64"
    wheels.mkdir(parents=True, exist_ok=True)
    if list(wheels.iterdir()):
        raise SystemExit("Wheel directory must be empty; review existing files before refreshing")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--only-binary=:all:",
            "--platform",
            "manylinux_2_28_x86_64",
            "--platform",
            "manylinux_2_24_x86_64",
            "--platform",
            "manylinux2014_x86_64",
            "--platform",
            "manylinux_2_17_x86_64",
            "--python-version",
            "3.12",
            "--implementation",
            "cp",
            "--abi",
            "cp312",
            "--require-hashes",
            "--dest",
            str(wheels),
            "-r",
            str(target_requirements),
        ],
        check=True,
    )
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "download",
            "--only-binary=:all:",
            "--no-deps",
            "--dest",
            str(wheels),
            "pip==26.3",
        ],
        check=True,
    )
    (pip_wheel,) = wheels.glob("pip-*.whl")
    bootstrap_requirements = ROOT / "vendor/bootstrap-pip.txt"
    bootstrap_requirements.write_text(
        "pip==26.3 --hash=sha256:" + hashlib.sha256(pip_wheel.read_bytes()).hexdigest() + "\n"
    )
    assets = {
        "htmx.min.js": "https://unpkg.com/htmx.org@2.0.11/dist/htmx.min.js",
        "HTMX-LICENSE.txt": "https://unpkg.com/htmx.org@2.0.11/LICENSE",
    }
    for name, url in assets.items():
        (ROOT / "app/static/vendor" / name).write_bytes(urllib.request.urlopen(url).read())
    paths = sorted(wheels.glob("*.whl")) + [
        target_requirements,
        bootstrap_requirements,
        ROOT / "requirements.txt",
        ROOT / "uv.lock",
        ROOT / "app/static/vendor/htmx.min.js",
        ROOT / "app/static/vendor/HTMX-LICENSE.txt",
    ]
    manifest = {
        "target": "CPython 3.12 / Linux x86_64 / glibc >= 2.28",
        "files": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths
        },
    }
    (ROOT / "vendor/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()

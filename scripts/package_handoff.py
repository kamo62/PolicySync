"""Package only project source and approved dependencies; never runtime state."""

import hashlib
import tarfile
from pathlib import Path

from scripts.install_offline import ROOT, verify


def main():
    verify()
    names = [
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "PolicySync_Technical_PRD_v2.0.md",
        "pyproject.toml",
        "uv.lock",
        "requirements.txt",
        ".python-version",
        ".env.example",
        ".editorconfig",
        ".gitignore",
        ".gitattributes",
        "alembic.ini",
    ]
    paths = [ROOT / name for name in names]
    for directory in ["app", "migrations", "scripts", "tests", "docs", "vendor", ".github"]:
        paths.extend(
            p
            for p in (ROOT / directory).rglob("*")
            if p.is_file()
            and "__pycache__" not in p.parts
            and p.suffix != ".pyc"
            and p.name.casefold() not in {"agents.md", "handoff.md", "tasks.md"}
        )
    if any(not p.is_file() for p in paths):
        raise SystemExit("A required handoff file is missing")
    destination = ROOT / "dist/policysync-offline-linux-x86_64-py312.tar.gz"
    destination.parent.mkdir(exist_ok=True)
    with tarfile.open(destination, "w:gz") as archive:
        for path in sorted(paths):
            archive.add(path, arcname=Path("PolicySync") / path.relative_to(ROOT), recursive=False)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix(destination.suffix + ".sha256").write_text(
        f"{digest}  {destination.name}\n"
    )
    print(f"{destination} ({destination.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

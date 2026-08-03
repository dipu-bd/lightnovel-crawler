"""Bump the version of the project."""

import argparse
from pathlib import Path

version_file = Path(__file__).parent.parent / "lncrawl" / "VERSION"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bump the version of the project.",
    )
    parser.add_argument(
        "type",
        type=str,
        help="The type of bump to perform.",
        choices=["major", "minor", "patch"],
    )
    args = parser.parse_args()

    current_version = version_file.read_text().strip()

    major, minor, patch = (int(p) for p in current_version.split("."))
    if args.type == "major":
        major, minor, patch = major + 1, 0, 0
    elif args.type == "minor":
        minor, patch = minor + 1, 0
    elif args.type == "patch":
        patch += 1

    new_version = f"{major}.{minor}.{patch}"
    version_file.write_text(new_version)

    print(f"Bumped {args.type}: {current_version} -> {new_version}")


if __name__ == "__main__":
    main()

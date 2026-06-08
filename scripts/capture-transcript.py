#!/usr/bin/env python3
"""
Capture an agent run's output text to the transcript directory structure.

Usage:
    python capture-transcript.py --stage P0 --framework _program --agent documentation-engineer --output-file <path>

Validates stage, framework, and agent identifiers; generates ISO8601 timestamp;
creates the transcript directory; copies the output file; and prints the relative
path (which becomes the transcript_ref in the registry entry).
"""

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def validate_stage(stage: str) -> bool:
    """Validate stage identifier against the exact set defined in STAGE_GATES.yaml."""
    valid_stages = {"P0", "P1", "S1f", "S3", "S4", "S5", "S6", "S7", "S8f", "S9",
                    "X1", "X2", "X3", "X4", "X5"}
    return stage in valid_stages


def validate_identifier(identifier: str) -> bool:
    """Validate framework or agent identifier format (alphanumeric, hyphen, underscore)."""
    pattern = r"^[a-zA-Z0-9_-]+$"
    return bool(re.match(pattern, identifier))


def get_repo_root() -> Path:
    """Get the git repository root directory."""
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        return Path(result.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Capture agent run output to transcript directory structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python capture-transcript.py --stage P0 --framework _program --agent documentation-engineer --output-file /tmp/output.txt
  python capture-transcript.py --stage S7 --framework nist-800-53 --agent data-scientist --output-file results.txt
        """,
    )

    parser.add_argument(
        "--stage",
        required=True,
        help="Stage identifier (e.g., P0, P1, S1f, S3, S4, S5, S6, S7, S8f, S9, X1, X2, X3, X4, X5)",
    )
    parser.add_argument(
        "--framework",
        required=True,
        help="Framework identifier (e.g., scf, nist-800-53, _program)",
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent name (e.g., documentation-engineer, data-scientist)",
    )
    parser.add_argument(
        "--output-file",
        required=True,
        help="Path to the agent output text file",
    )

    args = parser.parse_args()

    # Validate arguments
    if not validate_stage(args.stage):
        print(f"Error: Invalid stage identifier '{args.stage}'", file=sys.stderr)
        return 1

    if not validate_identifier(args.framework):
        print(f"Error: Invalid framework identifier '{args.framework}'", file=sys.stderr)
        return 1

    if not validate_identifier(args.agent):
        print(f"Error: Invalid agent identifier '{args.agent}'", file=sys.stderr)
        return 1

    # Check that output file exists and is readable
    output_path = Path(args.output_file)
    if not output_path.is_file():
        print(f"Error: Output file not found: {args.output_file}", file=sys.stderr)
        return 1

    # Generate ISO8601 timestamp in UTC
    now_utc: datetime = datetime.now(timezone.utc)
    timestamp: str = now_utc.strftime("%Y-%m-%d-%H-%M-%S")

    # Get repo root
    repo_root: Path = get_repo_root()

    # Construct target path
    target_dir: Path = repo_root / "transcripts" / args.stage / args.framework
    base_name: str = f"{args.agent}-{timestamp}"
    target_file: Path = target_dir / f"{base_name}.md"

    # Create directory if needed
    target_dir.mkdir(parents=True, exist_ok=True)

    # Collision handling: if path already exists, append -2, -3, etc.
    if target_file.exists():
        counter = 2
        while True:
            candidate = target_dir / f"{base_name}-{counter}.md"
            if not candidate.exists():
                target_file = candidate
                break
            counter += 1

    # Copy the output file to the target path
    try:
        target_file.write_text(output_path.read_text(encoding="utf-8"), encoding="utf-8")
    except (IOError, OSError) as e:
        print(f"Error: Failed to copy output file: {e}", file=sys.stderr)
        return 1

    # Compute relative path from repo root for display
    relative_path: str = str(target_file.relative_to(repo_root))

    # Print the relative path (becomes transcript_ref in registry entry)
    print(relative_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/bin/bash
set -euo pipefail

# Capture an agent run's output text to the transcript directory structure.
# Usage: ./scripts/capture-transcript.sh --stage P0 --framework _program --agent documentation-engineer --output-file <path>

show_usage() {
    cat << 'EOF'
Usage: capture-transcript.sh --stage STAGE --framework FRAMEWORK --agent AGENT --output-file OUTPUT_FILE

Captures an agent run's output text to transcripts/<stage>/<framework>/<agent>-<timestamp>.md

Options:
  --stage STAGE               Stage identifier (e.g., P0, P1, S1f, S3, S4, S5, S6, S7, S8f, S9, X1, X2, X3, X4, X5)
  --framework FRAMEWORK       Framework identifier (e.g., scf, nist-800-53, _program)
  --agent AGENT              Agent name (e.g., documentation-engineer, data-scientist)
  --output-file OUTPUT_FILE  Path to the agent output text file

Examples:
  ./scripts/capture-transcript.sh --stage P0 --framework _program --agent documentation-engineer --output-file /tmp/agent-output.txt
  ./scripts/capture-transcript.sh --stage S7 --framework nist-800-53 --agent data-scientist --output-file results.txt
EOF
}

# Parse arguments
stage=""
framework=""
agent=""
output_file=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --stage)
            stage="$2"
            shift 2
            ;;
        --framework)
            framework="$2"
            shift 2
            ;;
        --agent)
            agent="$2"
            shift 2
            ;;
        --output-file)
            output_file="$2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            show_usage
            exit 1
            ;;
    esac
done

# Validate arguments
if [[ -z "$stage" || -z "$framework" || -z "$agent" || -z "$output_file" ]]; then
    echo "Error: Missing required arguments" >&2
    show_usage
    exit 1
fi

# Validate stage identifier format — must match exactly the stages in STAGE_GATES.yaml
if ! [[ "$stage" =~ ^(P0|P1|S1f|S3|S4|S5|S6|S7|S8f|S9|X1|X2|X3|X4|X5)$ ]]; then
    echo "Error: Invalid stage identifier '$stage'. Valid stages: P0 P1 S1f S3 S4 S5 S6 S7 S8f S9 X1 X2 X3 X4 X5" >&2
    exit 1
fi

# Validate framework identifier format (alphanumeric, hyphen, underscore)
if ! [[ "$framework" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Error: Invalid framework identifier '$framework'" >&2
    exit 1
fi

# Validate agent identifier format (alphanumeric, hyphen, underscore)
if ! [[ "$agent" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    echo "Error: Invalid agent identifier '$agent'" >&2
    exit 1
fi

# Check that output file exists and is readable
if [[ ! -f "$output_file" ]]; then
    echo "Error: Output file not found: $output_file" >&2
    exit 1
fi

# Generate ISO8601 timestamp in UTC
timestamp=$(date -u +"%Y-%m-%d-%H-%M-%S")

# Construct target path
repo_root="$(git rev-parse --show-toplevel 2>/dev/null || echo '.')"
target_dir="${repo_root}/transcripts/${stage}/${framework}"
target_file="${target_dir}/${agent}-${timestamp}.md"

# Create directory if needed
mkdir -p "$target_dir"

# Collision handling: if path already exists, append -2, -3, etc.
final_file="$target_file"
if [[ -f "$final_file" ]]; then
    counter=2
    while [[ -f "${target_dir}/${agent}-${timestamp}-${counter}.md" ]]; do
        counter=$((counter + 1))
    done
    final_file="${target_dir}/${agent}-${timestamp}-${counter}.md"
fi

# Copy the output file to the target path
cp "$output_file" "$final_file"

# Compute relative path from repo root for display
relative_path="$(realpath --relative-to="$repo_root" "$final_file" 2>/dev/null || echo "${final_file#$repo_root/}")"

# Print the relative path (becomes transcript_ref in registry entry)
echo "$relative_path"

exit 0

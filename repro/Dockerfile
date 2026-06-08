# Reproducibility container for hc-grc
#
# Base image: python:3.11-slim
#
# IMPORTANT — Pin this digest before first production use:
#   docker pull python:3.11-slim
#   docker inspect python:3.11-slim --format='{{index .RepoDigests 0}}'
# Then replace the FROM line below with:
#   FROM python:3.11-slim@sha256:<digest>
#
# Use the pin-docker-digest GitHub Actions workflow (.github/workflows/pin-docker-digest.yml)
# to automate this: it pulls the image, retrieves the digest, and opens a PR updating this line.
# The pin is a deliberate human action — see docs/REPRODUCIBILITY.md for the pinning process.
#
FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements before source so Docker layer cache is efficient.
# requirements-dev.txt is the authoritative dependency file for this project.
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy project source
COPY . .

# Default: drop to bash so smoke scripts can be exec'd by the CI runner
CMD ["bash"]

"""
Qdrant connection helpers for HC-GRC.

ADR-0002 data sovereignty: Qdrant runs as a local Docker container (see
docker-compose.yml) on the Colima runtime. This module only provides connection
parameters, a client factory, and a health check — collection creation and
population are the Embedding Agent's responsibility (agents/02-data/embedding-agent).

Connection parameters come from configs/platform.yaml -> vector_store.
"""

from __future__ import annotations

from typing import Any

from ..config import load_platform_config


def _cfg() -> dict[str, Any]:
    return load_platform_config()["vector_store"]


def qdrant_url() -> str:
    """Return the Qdrant REST base URL, e.g. http://localhost:6333."""
    cfg = _cfg()
    return f"http://{cfg.get('host', 'localhost')}:{cfg.get('http_port', 6333)}"


def expected_collections() -> list[str]:
    """Return the platform's declared Qdrant collections."""
    return list(_cfg().get("collections", []))


def get_qdrant_client():
    """
    Construct a QdrantClient from platform config.

    Requires the `qdrant-client` package and a running Qdrant container.
    """
    from qdrant_client import QdrantClient

    cfg = _cfg()
    host = cfg.get("host", "localhost")
    if cfg.get("prefer_grpc", False):
        return QdrantClient(
            host=host,
            grpc_port=cfg.get("grpc_port", 6334),
            prefer_grpc=True,
        )
    return QdrantClient(host=host, port=cfg.get("http_port", 6333))


def qdrant_health() -> dict[str, Any]:
    """
    Probe the running Qdrant instance.

    Returns a dict with reachability, the server-reported collection names, and
    which expected collections are still missing. Raises if the client package
    is absent or the server is unreachable.
    """
    client = get_qdrant_client()
    present = sorted(c.name for c in client.get_collections().collections)
    expected = expected_collections()
    return {
        "url": qdrant_url(),
        "reachable": True,
        "collections_present": present,
        "collections_missing": [c for c in expected if c not in present],
    }


if __name__ == "__main__":  # pragma: no cover - operational entrypoint
    import json

    print(json.dumps(qdrant_health(), indent=2))

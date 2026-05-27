"""Re-export dependencies from app.core.deps for convenience."""

from app.core.deps import get_current_user, get_db, get_opensearch_client

__all__ = ["get_db", "get_current_user", "get_opensearch_client"]

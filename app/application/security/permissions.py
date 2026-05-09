from __future__ import annotations

from app.shared.context import RequestContext


class PermissionChecker:
    """Provider-neutral permission helper for application use cases."""

    def has_permission(self, context: RequestContext, permission: str) -> bool:
        return permission in context.actor.permissions

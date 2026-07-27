from .models import AuditLog


def log_activity(
    user,
    action,
    prompt,
    tool_used,
    success=True
):
    """
    Create an audit log entry.

    Parameters:
        user        -> request.user
        action      -> e.g. "Delete Client"
        prompt      -> Description of the action
        tool_used   -> Module/Tool name
        success     -> True/False
    """

    if not user or not user.is_authenticated:
        return

    AuditLog.objects.create(
        uid=user,
        action=action,
        prompt=prompt,
        tool_used=tool_used,
        success=success
    )
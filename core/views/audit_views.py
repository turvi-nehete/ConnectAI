from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from core.models import AuditLog


def audit(request):

    # Show only the logged-in user's audit logs
    logs = AuditLog.objects.select_related("uid").filter(
        uid=request.user
    ).order_by("-timestamp")

    # Search
    search = request.GET.get("search", "").strip()
    if search:
        logs = logs.filter(
            Q(prompt__icontains=search) |
            Q(action__icontains=search) |
            Q(uid__username__icontains=search) |
            Q(tool_used__icontains=search)
        )

    # Tool Filter
    tool = request.GET.get("tool", "All")
    if tool != "All":
        logs = logs.filter(tool_used=tool)

    # Summary Cards (only current user's logs)
    total_logs = AuditLog.objects.filter(
        uid=request.user
    ).count()

    successful = AuditLog.objects.filter(
        uid=request.user,
        success=True
    ).count()

    failed = AuditLog.objects.filter(
        uid=request.user,
        success=False
    ).count()

    today = AuditLog.objects.filter(
        uid=request.user,
        timestamp__date=timezone.localdate()
    ).count()

    # Pagination
    paginator = Paginator(logs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    available_tools = (
    AuditLog.objects
    .filter(uid=request.user)
    .values_list("tool_used", flat=True)
    .distinct()
    .order_by("tool_used")
)

    context = {
        "page_obj": page_obj,
        "total_logs": total_logs,
        "successful": successful,
        "failed": failed,
        "today": today,
        "search": search,
        "selected_tool": tool,
        "available_tools": available_tools,
    }

    return render(request, "audit.html", context)
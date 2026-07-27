from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from core.models import AuditLog


def audit(request):

    logs = AuditLog.objects.select_related("uid").order_by("-timestamp")

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

    # Summary Cards
    total_logs = AuditLog.objects.count()

    successful = AuditLog.objects.filter(
        success=True
    ).count()

    failed = AuditLog.objects.filter(
        success=False
    ).count()

    today = AuditLog.objects.filter(
        timestamp__date=timezone.localdate()
    ).count()

    # Pagination
    paginator = Paginator(logs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "total_logs": total_logs,
        "successful": successful,
        "failed": failed,
        "today": today,
        "search": search,
        "selected_tool": tool,
    }

    return render(request, "audit.html", context)
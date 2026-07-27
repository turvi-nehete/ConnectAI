from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.models import Client, Campaign, Meeting


@login_required
def dashboard(request):

    total_clients = Client.objects.filter(
        uid=request.user,
        is_active=True
    ).count()

    total_campaigns = Campaign.objects.filter(
        created_by=request.user
    ).count()

    upcoming_meetings = Meeting.objects.filter(
        uid=request.user,
        meeting_date__gte=timezone.localdate()
    ).count()

    recent_meetings = (
    Meeting.objects
    .filter(
        uid=request.user,
        meeting_date__gte=timezone.localdate()
    )
    .order_by("meeting_date", "meeting_time")[:5]
)

    recent_campaigns = (
        Campaign.objects
        .filter(created_by=request.user)
        .order_by("-created_at")[:5]
    )
    draft_campaigns = Campaign.objects.filter(
    created_by=request.user,
    status="draft"
    ).count()

    platinum_clients = Client.objects.filter(
    uid=request.user,
    customer_type="platinum",
    is_active=True
    ).count()

    return render(
        request,
        "dashboard.html",
        {
            "total_clients": total_clients,
            "total_campaigns": total_campaigns,
            "upcoming_meetings": upcoming_meetings,
            "recent_meetings": recent_meetings,
            "recent_campaigns": recent_campaigns,
            "draft_campaigns": draft_campaigns,
            "platinum_clients": platinum_clients,
        },
    )
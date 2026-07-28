from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from core.models import (
    Client,
    Campaign,
    Meeting,
    CampaignRecipient,
)


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

    campaign_recipients = CampaignRecipient.objects.filter(
    cam_id__created_by=request.user
)

    total_recipients = campaign_recipients.count()

    replied_recipients = campaign_recipients.filter(
      replied=True
    ).count()

    if total_recipients > 0:
      reply_rate = round(
        (replied_recipients / total_recipients) * 100,
        1
    )
    else:
      reply_rate = 0
    

    return render(
        request,
        "dashboard.html",
        {
            "total_clients": total_clients,
            "total_campaigns": total_campaigns,
            "upcoming_meetings": upcoming_meetings,
            "recent_meetings": recent_meetings,
            "recent_campaigns": recent_campaigns,
            "reply_rate": reply_rate,
    "replied_recipients": replied_recipients,
    "total_recipients": total_recipients,
        },
    )
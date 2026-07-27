from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q

from core.models import Campaign
from core.inbox import sync_all_replies


@login_required
def inbox(request):

    sync_all_replies()

    # -----------------------------
    # Main Campaigns
    # -----------------------------

    emails = (
        Campaign.objects.filter(
            created_by=request.user,
            is_reminder=False
        )
        .annotate(
            recipient_count=Count("recipients"),
            reply_count=Count(
                "recipients",
                filter=Q(recipients__replied=True)
            )
        )
        .order_by("-created_at")
    )

    search = request.GET.get("search")
    status = request.GET.get("status")

    if search:
        emails = emails.filter(
            Q(subj__icontains=search) |
            Q(cap_name__icontains=search)
        )

    if status == "sent":
        emails = emails.filter(status="sent")

    elif status == "replied":
        emails = emails.filter(
            recipients__replied=True
        ).distinct()

    elif status == "pending":
        emails = emails.exclude(
            recipients__replied=True
        ).distinct()

    elif status == "failed":
        emails = emails.filter(
            recipients__del_status="Failed"
        ).distinct()

    # -----------------------------
    # Follow-up Campaigns
    # -----------------------------

    followups = (
        Campaign.objects.filter(
            created_by=request.user,
            is_reminder=True
        )
        .annotate(
            recipient_count=Count("recipients"),
            reply_count=Count(
                "recipients",
                filter=Q(recipients__replied=True)
            )
        )
        .order_by("-created_at")
    )

    context = {

        "emails": emails,

        "followups": followups,

        "total_sent": emails.count(),

        "total_replies": sum(
            e.reply_count
            for e in emails
        ),

        "pending_replies": sum(
            e.recipient_count - e.reply_count
            for e in emails
        ),

        "failed": 0,

    }

    return render(
        request,
        "campaigns.html",
        context,
    )

from django.http import JsonResponse
from django.utils import timezone
from core.models import CampaignRecipient
from core.gmail import check_reply
from core.inbox import sync_all_replies


def sync_replies(request):

    updated = sync_all_replies()

    return JsonResponse({
        "updated": updated
    })


from django.shortcuts import get_object_or_404, render
from core.models import Campaign, CampaignRecipient

def email_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, cam_id=campaign_id)

    recipients = CampaignRecipient.objects.filter(cam_id=campaign)

    total = recipients.count()
    replied = recipients.filter(replied=True).count()
    pending = recipients.filter(replied=False, del_status="Sent").count()
    failed = recipients.filter(del_status="Failed").count()
    reminders = (
    Campaign.objects.filter(
        parent_campaign=campaign,
        is_reminder=True
    )
    .prefetch_related("recipients__cid")
    .order_by("-created_at")
)
    return render(request, "email_detail.html", {
    "campaign": campaign,
    "recipients": recipients,
    "total": total,
    "replied": replied,
    "pending": pending,
    "failed": failed,
    "reminders": reminders,
})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from core.models import Campaign, CampaignRecipient
from core.agents import generate_reminder_email


@login_required
def generate_reminder(request, campaign_id):

    campaign = get_object_or_404(
        Campaign,
        cam_id=campaign_id,
        created_by=request.user
    )

    pending_recipients = CampaignRecipient.objects.filter(
        cam_id=campaign,
        replied=False,
        del_status="Sent"
    )

    reminder = generate_reminder_email(
        campaign.mail_body
    )
    all_recipients = CampaignRecipient.objects.filter(
    cam_id=campaign
)

    return render(
        request,
        "reminder_preview.html",
        {
            "campaign": campaign,
            "pending_recipients": pending_recipients,
            "subject": reminder["subject"],
            "body": reminder["body"],
            "all_recipients": all_recipients,
        },
    )

import json
from django.http import JsonResponse
from core.gmail import send_bulk_email
from core.inbox import create_email_log

@login_required
def send_reminder(request, campaign_id):

    campaign = get_object_or_404(
        Campaign,
        cam_id=campaign_id,
        created_by=request.user,
    )

    data = json.loads(request.body)

    subject = data["subject"]

    body = data["body"]

    pending = CampaignRecipient.objects.filter(

        cam_id=campaign,

        replied=False,

        del_status="Sent",

    )

    recipients = []

    for r in pending:

        recipients.append({

            "id": r.cid.cid,

            "email": r.cid.c_mail,

        })

    result = send_bulk_email(

        recipients,

        subject,

        body,

    )

    create_email_log(

        cap_name=f"Reminder - {campaign.cap_name}",

        prompt="Reminder",

        subject=subject,

        body=body,

        recipients=recipients,

        result=result,

        user=request.user,

        is_reminder=True,

        parent_campaign=campaign,

    )

    return JsonResponse({

        "success": True,

        "message": f"Reminder sent to {result['total_sent']} recipients."

    })

@login_required
def reminder_detail(request, campaign_id):

    reminder = get_object_or_404(
        Campaign,
        cam_id=campaign_id,
        is_reminder=True,
        created_by=request.user,
    )

    recipients = CampaignRecipient.objects.filter(
        cam_id=reminder
    )

    return render(
        request,
        "reminder_detail.html",
        {
            "reminder": reminder,
            "recipients": recipients,
        },
    )
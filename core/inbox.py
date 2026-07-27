from django.utils import timezone
from core.models import Campaign, CampaignRecipient, Client


def create_email_log(
    user,
    subject,
    body,
    recipients,
    result,
    prompt="",
    cap_name=None,
    is_reminder=False,
    parent_campaign=None,
):
    """
    Creates one Campaign entry and CampaignRecipient
    entries for every recipient.
    Works for both normal campaigns and reminders.
    """

    campaign = Campaign.objects.create(
        cap_name=cap_name or subject,
        prompt=prompt,
        subj=subject,
        mail_body=body,
        created_by=user,
        status="sent",

        # NEW
        is_reminder=is_reminder,
        parent_campaign=parent_campaign,
    )

    # -----------------------------
    # Successful emails
    # -----------------------------

    for sent in result.get("sent", []):

        try:

            client = Client.objects.get(pk=sent["client_id"])

            CampaignRecipient.objects.create(
                cam_id=campaign,
                cid=client,
                del_status="Sent",
                sent_at=timezone.now(),
                replied=False,
                replied_message="",
                thread_id=sent.get("thread_id", ""),
                message_id=sent.get("message_id", ""),
            )

        except Client.DoesNotExist:
            continue

    # -----------------------------
    # Failed emails
    # -----------------------------

    for failed in result.get("failed", []):

        try:

            client = Client.objects.get(pk=failed["client_id"])

            CampaignRecipient.objects.create(
                cam_id=campaign,
                cid=client,
                del_status="Failed",
                replied=False,
                replied_message="",
            )

        except Client.DoesNotExist:
            continue

    return campaign

from django.utils import timezone
from core.models import CampaignRecipient
from core.gmail import check_reply

def sync_all_replies():

    print("=" * 50)
    print("SYNC FUNCTION CALLED")

    recipients = CampaignRecipient.objects.filter(replied=False)

    print("Recipients to check:", recipients.count())

    updated = 0

    for recipient in recipients:
        print("Checking:", recipient.rid, recipient.thread_id)

        if not recipient.thread_id:
            print("No thread id")
            continue

        result = check_reply(recipient.thread_id)

        print(result)

        if result["replied"]:
            recipient.replied = True
            recipient.replied_message = result["reply_text"]
            recipient.replied_at = timezone.now()
            recipient.save()

            updated += 1

    print("Updated:", updated)
    return updated
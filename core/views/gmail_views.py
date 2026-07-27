import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

from core.gmail import send_bulk_email
from core.inbox import create_email_log
from core.audit import log_activity

@login_required
@require_POST
def send_email(request):
    data = json.loads(request.body)

    print(data)
    print(data["recipients"])
    try:
        data = json.loads(request.body)

        subject = data.get("subject", "").strip()
        body = data.get("body", "").strip()
        recipients = data.get("recipients", [])

        if not subject:
            return JsonResponse(
                {"success": False, "error": "Subject is required."},
                status=400
            )

        if not body:
            return JsonResponse(
                {"success": False, "error": "Email body is required."},
                status=400
            )

        if not recipients:
            return JsonResponse(
                {"success": False, "error": "No recipients selected."},
                status=400
            )

        result = send_bulk_email(
            recipients=recipients,
            subject=subject,
            body=body
        )
        create_email_log(
          user=request.user,
          subject=subject,
          body=body,
          recipients=recipients,
          result=result
        )

        log_activity(
          request.user,
         "Send Email",
          subject,
          "Gmail API"
)

        return JsonResponse({
            "success": True,
            "message": "Emails processed successfully.",
            "result": result
        })

    except Exception as e:
        return JsonResponse(
            {
                "success": False,
                "error": str(e)
            },
            status=500
        )
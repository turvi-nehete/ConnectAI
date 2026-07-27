from django.urls import path

from .views import (
    audit_views,
    auth_views,
    client_views,
    gmail_views,
    ai_views,
    campaign_views,
    calendar_views,
    dashboard_views,
    views,
)

urlpatterns = [

    # Authentication 
    path("login/", auth_views.login_view, name="login"),
    path("register/", auth_views.register_view, name="register"),
    path("logout/", auth_views.logout_view),

    #clients
    path("clients/", client_views.clients,name="clients"),
    path("clients/edit/<int:cid>/",client_views.edit_client,name="edit_client"),
    path("clients/delete/<int:cid>/",client_views.delete_client,name="delete_client",),
    path("clients/filter/",client_views.get_recipients,name="get_recipients",),

    # Gmail
    path("send-gmail/", gmail_views.send_email),
    

    # AI
    path("ai_chat/", ai_views.chat,name="ai_chat"),
    path("generate-email/", ai_views.generate_email, name="generate_email"),
    path("generate-email-rag/",ai_views.generate_email_rag,name="generate_email_rag",),

    # INBOX (Campaign)
    path("campaigns/", campaign_views.inbox, name="campaigns"),
    path("sync-replies/", campaign_views.sync_replies, name="sync_replies"),
    path("inbox/<int:campaign_id>/",campaign_views.email_detail,name="email_detail"),
    path("campaign/<int:campaign_id>/reminder/", campaign_views.generate_reminder,name="generate_reminder"),
    path("campaign/<int:campaign_id>/send-reminder/",campaign_views.send_reminder,name="send_reminder"),
    path("reminder/<int:campaign_id>/",campaign_views.reminder_detail, name="reminder_detail",),

    # Calendar and meetings
    path("calendar/create/", calendar_views.create_meeting),
    path("meetings/",calendar_views.meetings,name="meetings"),
    path("calendar/update/<int:meeting_id>/",calendar_views.update_meeting,name="update_meeting"),
    path("calendar/events/",calendar_views.calendar_events,name="calendar_events"),
    path("calendar/meeting/<int:meeting_id>/",calendar_views.get_meeting_detail,name="get_meeting_detail",),

    # Dashboard
    path("dashboard/",dashboard_views.dashboard,name="dashboard",),

    #audit
    path("audit/",audit_views.audit,name="audit_log")

]

from datetime import datetime,timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from core.serializers import MeetingCreateSerializer
from core.google_calendar import (
    create_meeting as google_create_meeting,
    update_google_meeting,
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


from django.shortcuts import render
from core.models import Client, Meeting, MeetingParticipant
from django.utils import timezone

def meetings(request):

    clients = Client.objects.filter(
        is_active=True,
        uid=request.user
    ).order_by("comp_name")

    meetings = (
        Meeting.objects
        .filter(uid=request.user)
        .prefetch_related("participants__cid")
        .order_by("meeting_date", "meeting_time")
    )

    now = timezone.localtime()

    upcoming_meetings = []

    for meeting in meetings:

        meeting_start = timezone.make_aware(
            datetime.combine(
                meeting.meeting_date,
                meeting.meeting_time
            )
        )

        meeting_end = meeting_start + timedelta(
            minutes=meeting.duration_minutes
        )

        # Show meeting until it has completely finished
        if meeting_end >= now:
            upcoming_meetings.append(meeting)

    return render(
        request,
        "meetings.html",
        {
            "clients": clients,
            "meetings": meetings,
            "upcoming_meetings": upcoming_meetings,
        }
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_meeting(request):

    serializer = MeetingCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data

    start_datetime = datetime.combine(
        data["meeting_date"],
        data["meeting_time"]
    )

    clients = Client.objects.filter(
    cid__in=data["client_ids"],
    uid=request.user
)

    attendees = list(
        clients.values_list("c_mail", flat=True)
     )

    meeting_data = google_create_meeting(
    title=data["title"],
    agenda=data["agenda"],
    start_datetime=start_datetime,
    duration_minutes=data["duration_minutes"],
    attendees=attendees,
)

    meeting = Meeting.objects.create(
    title=data["title"],
    agenda=data["agenda"],
    meeting_date=data["meeting_date"],
    meeting_time=data["meeting_time"],
    duration_minutes=data["duration_minutes"],
    uid=request.user,
    google_event_id=meeting_data["event_id"],
    google_meet_link=meeting_data["meet_link"],
)
    
    for client in clients:

      MeetingParticipant.objects.create(
        mid=meeting,
        cid=client,
        status="pending"
    )
    log_activity(
       request.user,
       "Create Meeting",
       meeting.title,
       "Google Calendar"
)
    
      
    
    return Response(
    {
        "message": "Meeting created successfully.",
        "meeting_id": meeting.mid,
        **meeting_data,
    },
    status=status.HTTP_201_CREATED,
)


from core.audit import log_activity

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def calendar_events(request):

    meetings = Meeting.objects.filter(uid=request.user)

    events = []

    for meeting in meetings:

        events.append({
            "id": meeting.mid,
            "title": meeting.title,
            "start": f"{meeting.meeting_date}T{meeting.meeting_time}",
            "url": meeting.google_meet_link,
        })
    
    


    return Response(events)

from django.shortcuts import get_object_or_404
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_meeting_detail(request, meeting_id):

    meeting = get_object_or_404(
        Meeting,
        mid=meeting_id,
        uid=request.user
    )

    participants = []

    for participant in meeting.participants.all():

        participants.append({
            "company": participant.cid.comp_name,
            "contact": participant.cid.contactname,
            "email": participant.cid.c_mail,
        })

    return Response({
        "title": meeting.title,
        "agenda": meeting.agenda,
        "meeting_date": meeting.meeting_date,
        "meeting_time": meeting.meeting_time,
        "duration_minutes": meeting.duration_minutes,
        "google_meet_link": meeting.google_meet_link,
        "participants": participants,
    })


from django.shortcuts import get_object_or_404

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_meeting(request, meeting_id):

    serializer = MeetingCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    data = serializer.validated_data

    meeting = get_object_or_404(
        Meeting,
        mid=meeting_id,
        uid=request.user
    )

    start_datetime = datetime.combine(
        data["meeting_date"],
        data["meeting_time"]
    )

    clients = Client.objects.filter(
        cid__in=data["client_ids"],
        uid=request.user
    )

    attendees = list(
        clients.values_list("c_mail", flat=True)
    )

    google_data = update_google_meeting(
        google_event_id=meeting.google_event_id,
        title=data["title"],
        agenda=data["agenda"],
        start_datetime=start_datetime,
        duration_minutes=data["duration_minutes"],
        attendees=attendees,
    )

    # Update database
    meeting.title = data["title"]
    meeting.agenda = data["agenda"]
    meeting.meeting_date = data["meeting_date"]
    meeting.meeting_time = data["meeting_time"]
    meeting.duration_minutes = data["duration_minutes"]
    meeting.google_meet_link = google_data["meet_link"]

    meeting.save()

    # Remove old participants
    meeting.participants.all().delete()

    # Add updated participants
    for client in clients:
        MeetingParticipant.objects.create(
            mid=meeting,
            cid=client,
            status="pending"
        )

    log_activity(
        request.user,
        "Update Meeting",
        meeting.title,
        "Google Calendar"
    )

    return Response(
        {
            "message": "Meeting updated successfully.",
            "meeting_id": meeting.mid,
            **google_data,
        }
    )

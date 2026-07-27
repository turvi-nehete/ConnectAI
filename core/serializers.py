from rest_framework import serializers


class MeetingCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=255)

    agenda = serializers.CharField()

    meeting_date = serializers.DateField()

    meeting_time = serializers.TimeField()

    duration_minutes = serializers.IntegerField(
        default=30,
        min_value=1
    )

    client_ids = serializers.ListField(
    child=serializers.IntegerField(),
    required=False,
    default=list
)
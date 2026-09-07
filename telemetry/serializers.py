from rest_framework import serializers
from .models import TripSession

class TripSessionSerializer(serializers.ModelSerializer):
    class Meta :
        model = TripSession
        fields =['session_id','vehicle_type','mount_type','start_time','status']
        read_only_fields = ['session_id','start_time','status']


class BenchmarkUploadSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    outage_detected = serializers.BooleanField(default=False)
    outage_duration_seconds = serializers.FloatField(default=0.0)
    distance_in_outage_meters = serializers.FloatField(default=0.0)
    measured_drift_meters = serializers.FloatField(default=0.0)
    total_distance_meters = serializers.FloatField(default=0.0)
    trajectory_sample = serializers.ListField(child=serializers.DictField(),default=list)
    
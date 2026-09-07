from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import TripSession, BenchmarkReport
from .serializers import TripSessionSerializer, BenchmarkUploadSerializer
# Create your views here.
# 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_trip(request):
    serializer = TripSessionSerializer(data=request.data)
    if serializer.is_valid():
        trip = serializer.save(user=request.user)
        return Response({"session_id": trip.session_id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_summary(request):
    serializer = BenchmarkUploadSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    try:
        trip = TripSession.objects.get(session_id=data['session_id'], user=request.user, status='ACTIVE')
    except TripSession.DoesNotExist:
        return Response({"error":"Active trip not found"}, status=status.HTTP_404_NOT_FOUND)

    trip.status='COMPLETED'
    trip.end_time = timezone.now()
    trip.total_distance_meters = data['total_distance_meters']
    trip.save()

    benchmark = BenchmarkReport.objects.create(
        trip=trip,
        outage_detected = data['outage_detected'],
        outage_duration_seconds = data['distance_in_outage_meters'],
        measured_drift_meters = data['measured_drift_meters'],
        trajectory_sample = data['trajectory_sample']    
    )

    return Response({
        "drift_percentage":benchmark.drift_percentage,
        "benchmark_passed": benchmark.benchmark_passed
    },status=status.HTTP_200_OK)

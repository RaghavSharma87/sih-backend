import uuid
from django.db import models
from django.conf import settings

class TripSession(models.Model):
    VEHICLE_TYPES = [('car', 'Car'), ('two_wheeler', 'Two Wheeler')]
    MOUNT_TYPES = [('dashboard_mount', 'Dashboard Mount'), ('pocket', 'Pocket')]
    STATUS_CHOICES = [('ACTIVE', 'Active'), ('COMPLETED', 'Completed')]

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    mount_type = models.CharField(max_length=20, choices=MOUNT_TYPES)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_distance_meters = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

class BenchmarkReport(models.Model):
    trip = models.OneToOneField(TripSession, on_delete=models.CASCADE)
    outage_detected = models.BooleanField(default=False)
    outage_duration_seconds = models.FloatField(default=0.0)
    distance_in_outage_meters = models.FloatField(default=0.0)
    measured_drift_meters = models.FloatField(default=0.0)
    drift_percentage = models.FloatField(default=0.0)
    benchmark_passed = models.BooleanField(default=False)
    trajectory_sample = models.JSONField(default=list)

    def save(self, *args, **kwargs):
        if self.distance_in_outage_meters > 0:
            self.drift_percentage = (self.measured_drift_meters / self.distance_in_outage_meters) * 100.0
        else:
            self.drift_percentage = 0.0
        self.benchmark_passed = self.drift_percentage < 10.0
        super().save(*args, **kwargs)
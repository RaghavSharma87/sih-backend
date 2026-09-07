from django.contrib.gis.db import models
from django.utils.text import slugify

class MapRegion(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    bounding_box = models.PolygonField(srid=4326)
    tile_pack = models.FileField(upload_to='map_packs/tiles/')
    road_graph = models.FileField(upload_to='map_packs/graphs/')
    version = models.PositiveIntegerField(default=1)
    file_size_mb = models.FloatField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} (v{self.version})"

class BlackoutZone(models.Model):
    ZONE_TYPES = [
        ('TUNNEL', 'Tunnel'),
        ('UNDERPASS', 'Underpass'),
        ('PARKING', 'Underground Parking'),
        ('URBAN_CANYON', 'Urban Canyon'),
    ]

    name = models.CharField(max_length=255)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPES)
    region = models.ForeignKey(MapRegion, on_delete=models.CASCADE, related_name='blackout_zones')
    geometry = models.PolygonField(srid=4326)
    approx_length_meters = models.FloatField()
    
    entry_point = models.PointField(srid=4326, blank=True, null=True)
    exit_point = models.PointField(srid=4326, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_zone_type_display()})"
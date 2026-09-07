from rest_framework import serializers

from .models import BlackoutZone, MapRegion


class RouteRequestSerializer(serializers.Serializer):
    origin_lat = serializers.FloatField(min_value=-90.0, max_value=90.0)
    origin_lon = serializers.FloatField(min_value=-180.0, max_value=180.0)
    dest_lat = serializers.FloatField(min_value=-90.0, max_value=90.0)
    dest_lon = serializers.FloatField(min_value=-180.0, max_value=180.0)


class WayPointSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()



class BlackoutZoneSerializer(serializers.ModelSerializer):
    geometry = serializers.SerializerMethodField()
    entry_point = serializers.SerializerMethodField()
    exit_point = serializers.SerializerMethodField()

    class Meta:
        model = BlackoutZone
        fields = [
            "id",
            "name",
            "zone_type",
            "approx_length_meters",
            "geometry",
            "entry_point",
            "exit_point",
        ]

    def get_geometry(self, obj):
        # Swaps tuple from (lon, lat) to [lat, lon] for the exterior polygon ring
        if obj.geometry:
            return [[coord[1], coord[0]] for coord in obj.geometry.coords[0]]
        return []

    def get_entry_point(self, obj):
        # obj.y is latitude, obj.x is longitude
        if obj.entry_point:
            return [obj.entry_point.y, obj.entry_point.x]
        return None

    def get_exit_point(self, obj):
        if obj.exit_point:
            return [obj.exit_point.y, obj.exit_point.x]
        return None


class RouteResponseSerializer(serializers.Serializer):
    distance_meters = serializers.FloatField()
    duration_seconds = serializers.FloatField()
    geometry = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField())
    )
    intersecting_blackout_zones = BlackoutZoneSerializer(many=True)  # Updated reference


class MapRegionSerializer(serializers.ModelSerializer):
    # Fixed variable name to plural and updated serializer reference
    blackout_zones = BlackoutZoneSerializer(many=True, read_only=True)

    class Meta:
        model = MapRegion
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "bounding_box",
            "tile_pack",
            "road_graph",
            "version",
            "file_size_mb",
            "created_at",
            "updated_at",
            "blackout_zones",
        ]

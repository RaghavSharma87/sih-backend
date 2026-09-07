import requests
from django.contrib.gis.geos import Point, LineString
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import MapRegion, BlackoutZone
from .serializers import (
    MapRegionSerializer,
    BlackoutZoneSerializer,
    RouteRequestSerializer,
)

class MapRegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MapRegion.objects.all()
    serializer_class = MapRegionSerializer
    lookup_field = 'slug'
    permission_classes=[IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='check-location')
    def check_location(self, request):
        """
        Checks if a given coordinate (lat, lon) is inside a registered
        offline map region or currently within a blackout zone.
        """
        try:
            lat = float(request.query_params.get('lat'))
            lon = float(request.query_params.get('lon'))
        except (TypeError, ValueError):
            return Response(
                {"error": "Please provide valid 'lat' and 'lon' query parameters."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user_location = Point(lon, lat, srid=4326)
        
        region = MapRegion.objects.filter(bounding_box__contains=user_location).first()
        blackout_zone = BlackoutZone.objects.filter(geometry__contains=user_location).first()

        return Response({
            "in_region": region is not None,
            "region": MapRegionSerializer(region).data if region else None,
            "in_blackout_zone": blackout_zone is not None,
            "blackout_zone": BlackoutZoneSerializer(blackout_zone).data if blackout_zone else None
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='calculate-route')
    def calculate_route(self, request):
        """
        Calculates driving route via OSRM and checks for spatial
        intersections with any known BlackoutZones in PostGIS.
        """
        serializer = RouteRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        orig_lat, orig_lon = data['origin_lat'], data['origin_lon']
        dest_lat, dest_lon = data['dest_lat'], data['dest_lon']

        # OSRM expects coordinates in {lon},{lat} order
        osrm_url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{orig_lon},{orig_lat};{dest_lon},{dest_lat}"
            f"?overview=full&geometries=geojson"
        )
        
        try:
            response = requests.get(osrm_url, timeout=5)
            if response.status_code != 200:
                return Response(
                    {"error": "Routing engine returned a non-200 status code."},
                    status=status.HTTP_502_BAD_GATEWAY
                )
            
            osrm_data = response.json()
            if not osrm_data.get('routes'):
                return Response(
                    {"error": "No route found between the coordinates provided."},
                    status=status.HTTP_404_NOT_FOUND
                )

            primary_route = osrm_data['routes'][0]
            raw_coords = primary_route['geometry']['coordinates']  # [[lon, lat], ...]

        except Exception as e:
            return Response(
                {"error": f"Failed to reach routing service: {str(e)}"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        # Build PostGIS LineString (expects (lon, lat) tuples)
        route_linestring = LineString([tuple(coord) for coord in raw_coords], srid=4326)

        # Spatial search: Find any blackout zone the route passes through
        intersecting_zones = BlackoutZone.objects.filter(geometry__intersects=route_linestring)

        # Reformat coordinates to [lat, lon] for Leaflet / MapLibre compatibility
        leaflet_coords = [[coord[1], coord[0]] for coord in raw_coords]

        return Response({
            "distance_meters": primary_route['distance'],
            "duration_seconds": primary_route['duration'],
            "geometry": leaflet_coords,
            "has_blackout_zones": intersecting_zones.exists(),
            "intersecting_blackout_zones": BlackoutZoneSerializer(intersecting_zones, many=True).data
        }, status=status.HTTP_200_OK)
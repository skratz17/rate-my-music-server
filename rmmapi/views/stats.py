"""Stats ViewSet and Serializers"""
from rest_framework import serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.models import Rater, Artist, Song, List

class StatsSerializer(serializers.Serializer):
    users = serializers.IntegerField()
    artists = serializers.IntegerField()
    songs = serializers.IntegerField()
    lists = serializers.IntegerField()

class StatsViewSet(ViewSet):
    def list(self, request):
        """GET stats for RateMyMusic site"""
        data = {
            "users": Rater.objects.count(),
            "artists": Artist.objects.count(),
            "songs": Song.objects.count(),
            "lists": List.objects.count()
        }

        serializer = StatsSerializer(data)
        return Response(serializer.data)

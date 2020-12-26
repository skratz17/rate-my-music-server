"""Genre ViewSet and Serializers"""
from rest_framework import serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.models import Genre

class GenreSerializer(serializers.ModelSerializer):
    """JSON serializer for genre"""

    class Meta:
        model = Genre
        fields = ('id', 'name')

class GenreViewSet(ViewSet):
    def list(self, request):
        genres = Genre.objects.all()

        q = request.query_params.get('q', None)
        if q is not None:
            genres = self._filter_by_search_term(genres, q)

        count = len(genres)

        serializer = GenreSerializer(genres, many=True)
        return Response({
            "data": serializer.data,
            "count": count
        })

    def _filter_by_search_term(self, genres, q):
        """Given a Genres QuerySet, filter by those whose name contains search term q, case-insensitive"""
        return genres.filter(name__icontains=q)

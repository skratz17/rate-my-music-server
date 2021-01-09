"""Search ViewSet and Serializers"""
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.models import Artist, Song, List
from .artist import ArtistSerializer
from .song import SongSerializer
from .list import SimpleListSerializer

class SearchViewSet(ViewSet):
    def list(self, request):
        """GET results for search query across artist, songs, and lists"""
        search_term = self.request.query_params.get('q', None)

        artists = []
        songs = []
        lists = []

        if search_term is not None:
            artists = Artist.objects.filter(name__icontains=search_term)
            songs = Song.objects.filter(name__icontains=search_term)
            lists = List.objects.filter(name__icontains=search_term)

        artists = artists[0:25]
        songs = songs[0:25]
        lists = lists[0:25]

        artists_data = ArtistSerializer(artists, many=True)
        songs_data = SongSerializer(songs, many=True)
        lists_data = SimpleListSerializer(lists, many=True)

        return Response({
            "artists": artists_data.data,
            "songs": songs_data.data,
            "lists": lists_data.data
        })        

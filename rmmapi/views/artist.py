"""Artist ViewSet and Serializers"""
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.helpers import get_missing_keys
from rmmapi.models import Artist, Rater

class ArtistSerializer(serializers.ModelSerializer):
    """JSON serializer for artist"""
    class Meta:
        model = Artist
        fields = ('id', 'name', 'founded_year', 'description')

class ArtistViewSet(ViewSet):
    def create(self, request):
        """POST a new artist"""
        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        rater = Rater.objects.get(user=request.auth.user)

        artist = Artist(
            name=request.data['name'],
            description=request.data['description'],
            founded_year=request.data['founded_year'],
            creator=rater
        )

        try:
            artist.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ArtistSerializer(artist)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """GET an artist"""
        artist = get_object_or_404(Artist, pk=pk)

        serializer = ArtistSerializer(artist)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """PUT an artist"""
        artist = get_object_or_404(Artist, pk=pk)

        self.check_object_permissions(request, artist.creator)

        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        artist.name = request.data['name']
        artist.founded_year = request.data['founded_year']
        artist.description = request.data['description']

        try:
            artist.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ArtistSerializer(artist)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """DELETE an artist"""
        artist = get_object_or_404(Artist, pk=pk)
        
        self.check_object_permissions(request, artist.creator)

        artist.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """GET all artists"""
        artists = Artist.objects.all()

        q = request.query_params.get('q', None)

        if q is not None:
            artists = self._filter_by_search_term(artists, q)

        count = len(artists)

        serializer = ArtistSerializer(artists, many=True)
        return Response({
            "data": serializer.data,
            "count": count
        })

    def _validate(self):
        """Validate values sent in POST/PUT body - 
            ensure all required properties are present
        Returns: error message string if error found, False otherwise.
        """
        REQUIRED_KEYS = [ 'name', 'description', 'founded_year' ]

        missing_keys = get_missing_keys(self.request.data, REQUIRED_KEYS)
        if len(missing_keys) > 0:
                return f"Request body is missing the following required properties: {', '.join(missing_keys)}."

    def _filter_by_search_term(self, artists, q):
        """Given an artists QuerySet, return it filtered by artist name containing q"""
        return artists.filter(name__icontains=q)

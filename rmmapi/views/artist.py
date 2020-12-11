"""Artist ViewSet and Serializers"""
from django.core.exceptions import ValidationError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status, serializers
from rmmapi.models import Artist, Rater

class ArtistSerializer(serializers.ModelSerializer):
    """JSON serializer for artist"""
    class Meta:
        model = Artist
        fields = ('id', 'name', 'founded_year', 'description')

class ArtistViewSet(ViewSet):
    def create(self, request):
        """POST a new artist"""
        missing_keys = self._get_missing_keys()
        if len(missing_keys) > 0:
            return Response(
                { 'message': f"Request body is missing the following required properties: {', '.join(missing_keys)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

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
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response(
                {'message': 'No artist was found with that ID.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ArtistSerializer(artist)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def destroy(self, request, pk=None):
        """DELETE an artist"""
        try:
            artist = Artist.objects.get(pk=pk)
        except Artist.DoesNotExist:
            return Response(
                {'message': 'No artist was found with that ID.'},
                status=status.HTTP_404_NOT_FOUND
            )

        rater = Rater.objects.get(user=request.auth.user)
        if artist.creator != rater:
            return Response(
                {'message': 'An artist can only be deleted by its creator.'},
                status=status.HTTP_403_FORBIDDEN
            )

        artist.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def _get_missing_keys(self):
        """Given the request.data for a POST/PUT request, return a list containing the
        string values of all required keys that were not found in the request body"""
        REQUIRED_KEYS = [
            'name', 'description', 'founded_year'
        ]

        return [ key for key in REQUIRED_KEYS if not key in self.request.data ]
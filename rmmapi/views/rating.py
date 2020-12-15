"""Rating ViewSet and Serializers"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.models import Rating, Song, Rater
from rmmapi.helpers import get_missing_keys
from .rater import RaterSerializer

class RatingSerializer(serializers.ModelSerializer):
    """JSON serializer for rating"""
    rater = RaterSerializer()

    class Meta:
        model = Rating
        fields = ('id', 'rating', 'review', 'created_at', 'rater', 'song')
        depth = 1

class RatingViewSet(ViewSet):
    def create(self, request):
        """POST a new rating"""
        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        rater = Rater.objects.get(user=request.auth.user)
        try:
            Rating.objects.get(song_id=request.data['songId'], rater=rater)
            return Response({'message': 'User has already rated that song.'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

        rating = Rating(
            rating=request.data['rating'],
            review=request.data['review'],
            song_id=request.data['songId'],
            rater=rater,
            created_at=timezone.now()
        )

        try:
            rating.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RatingSerializer(rating)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """GET a single rating by id"""
        rating = get_object_or_404(Rating, pk=pk)

        serializer = RatingSerializer(rating)
        return Response(serializer.data)

    def _validate(self):
        """Validate values sent in POST/PUT body - 
            ensure all required properties are present,
            ensure song id refers to a valid song
        Returns: error message string if error found, False otherwise.
        """
        REQUIRED_KEYS = [ 'rating', 'review', 'songId' ]

        missing_keys = get_missing_keys(self.request.data, REQUIRED_KEYS)
        if len(missing_keys) > 0:
            return f"Request body is missing the following required properties: {', '.join(missing_keys)}."

        song_id = self.request.data['songId']
        try:
            Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return f"The song id {song_id} does not match an existing song."

        return False

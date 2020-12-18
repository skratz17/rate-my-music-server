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
            Rating.objects.get(song_id=request.data['song_id'], rater=rater)
            return Response({'message': 'User has already rated that song.'}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass

        rating = Rating(
            rating=request.data['rating'],
            review=request.data['review'],
            song_id=request.data['song_id'],
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

    def update(self, request, pk=None):
        """PUT a rating"""
        rating = get_object_or_404(Rating, pk=pk)

        self.check_object_permissions(request, rating.rater)

        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        rating.rating = request.data['rating']
        rating.review = request.data['review']
        rating.song_id = request.data['song_id']

        try:
            rating.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        serializer = RatingSerializer(rating)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        """DELETE a rating"""
        rating = get_object_or_404(Rating, pk=pk)

        self.check_object_permissions(request, rating.rater)

        rating.delete()
        return Response({}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """GET all ratings"""
        ratings = Rating.objects.all()

        user_id = request.query_params.get('userId', None)
        song_id = request.query_params.get('songId', None)

        if user_id is not None:
            ratings = ratings.filter(rater_id=user_id)
        
        if song_id is not None:
            ratings = ratings.filter(song_id=song_id)

        ratings = self._sort_by_query_string_param(ratings)

        serializer = RatingSerializer(ratings, many=True)
        return Response(serializer.data)

    def _validate(self):
        """Validate values sent in POST/PUT body - 
            ensure all required properties are present,
            ensure song id refers to a valid song
        Returns: error message string if error found, False otherwise.
        """
        REQUIRED_KEYS = [ 'rating', 'review', 'song_id' ]

        missing_keys = get_missing_keys(self.request.data, REQUIRED_KEYS)
        if len(missing_keys) > 0:
            return f"Request body is missing the following required properties: {', '.join(missing_keys)}."

        song_id = self.request.data['song_id']
        try:
            Song.objects.get(pk=song_id)
        except Song.DoesNotExist:
            return f"The song id {song_id} does not match an existing song."

        return False

    def _sort_by_query_string_param(self, ratings):
        """Sort ratings QuerySet by `orderBy` query string param"""
        orderable_fields_dict = {
            'rating': 'rating',
            'date': 'created_at'
        }

        order_by = self.request.query_params.get('orderBy', None)

        if order_by is not None and order_by in orderable_fields_dict:
            order_field = orderable_fields_dict[order_by]

            # sort in direction indicated by `direction` query string param
            # or ascending, by default
            direction = self.request.query_params.get('direction', 'asc')
            if direction == 'desc':
                order_field = '-' + order_field

            ratings = ratings.order_by(order_field)

        return ratings

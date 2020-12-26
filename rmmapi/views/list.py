"""List ViewSet and Serializers"""
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rmmapi.helpers import get_missing_keys, paginate
from rmmapi.models import List, Song, ListSong, Rater, ListFavorite
from .rater import RaterSerializer

class SongSerializer(serializers.ModelSerializer):
    """JSON serializer for a song"""
    class Meta:
        model = Song
        fields = ('id', 'name', 'year', 'artist', 'sources')
        depth = 1

class ListSongSerializer(serializers.ModelSerializer):
    """JSON serializer for ListSongs"""
    song = SongSerializer()
    class Meta:
        model = ListSong
        fields = ('id', 'song', 'description')

class ListSerializer(serializers.ModelSerializer):
    """JSON serializer for list"""
    songs = ListSongSerializer(many=True)
    creator = RaterSerializer()
    class Meta:
        model = List
        fields = ('id', 'name', 'description', 'songs', 'creator', 'fav_count', 'has_rater_favorited')

class SimpleListSerializer(serializers.ModelSerializer):
    """JSON serializer for list, sending fewer properties"""
    creator = RaterSerializer()
    class Meta:
        model = List
        fields = ('id', 'name', 'description', 'creator', 'fav_count')

class ListViewSet(ViewSet):
    def create(self, request):
        """POST a new list"""
        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data['name']
        description = request.data['description']
        songs = request.data['songs']
        rater = Rater.objects.get(user=request.auth.user)

        list = List(
            name=name,
            description=description,
            creator=rater,
            created_at=timezone.now()
        )

        list.has_rater_favorited = rater

        try:
            list.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        for song in songs:
            list_song = ListSong(
                list=list,
                song_id=song['id'],
                description=song['description']
            )
            try:
                list_song.save()
            except ValidationError as ex:
                return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        serializer = ListSerializer(list)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """GET a single list by id"""
        list = get_object_or_404(List, pk=pk)
        list.has_rater_favorited = Rater.objects.get(user=request.auth.user)

        serializer = ListSerializer(list)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """PUT a list"""
        list = get_object_or_404(List, pk=pk)

        self.check_object_permissions(request, list.creator)

        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        list.has_rater_favorited = Rater.objects.get(user=request.auth.user)

        name = request.data["name"]
        description = request.data["description"]
        songs = request.data["songs"]

        list.name = name
        list.description = description

        try:
            list.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        # delete any ListSong previously saved for this list that is not in the new songs list
        song_ids = [ song['id'] for song in songs ]
        list.songs.exclude(song_id__in=song_ids).delete()

        # then either create new ones that don't exist or update descriptions of ones that do
        for song in songs:
            try:
                list_song = ListSong.objects.get(list=list, song_id=song['id'])
            except ListSong.DoesNotExist:
                list_song = ListSong(
                    list=list,
                    song_id=song['id'],
                    description=song['description']
                )

            if song['description'] != list_song.description:
                list_song.description = song['description']
            
            try:
                list_song.save()
            except ValidationError as ex:
                return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = ListSerializer(list)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """DELETE a list by id"""
        list = get_object_or_404(List, pk=pk)

        self.check_object_permissions(request, list.creator)

        list.delete()
        return Response({}, status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """GET all lists"""
        lists = List.objects.all()

        song_id = request.query_params.get('songId', None)
        user_id = request.query_params.get('userId', None)
        favoritedBy = request.query_params.get('favoritedBy', None)
        page = request.query_params.get('page', None)
        pageSize = request.query_params.get('pageSize', 10)

        if song_id is not None:
            lists = lists.filter(songs__song_id=song_id).distinct()
        
        if user_id is not None:
            lists = lists.filter(creator_id=user_id)

        if favoritedBy is not None:
            lists = lists.filter(favorites__rater_id=favoritedBy)

        if page is not None:
            lists = paginate(lists, page, pageSize)

        serializer = SimpleListSerializer(lists, many=True)
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        list = get_object_or_404(List, pk=pk)
        rater = Rater.objects.get(user=request.auth.user)

        if request.method == 'POST':
            """POST a new ListFavorite"""
            try:
                ListFavorite.objects.get(rater=rater, list=list)
                return Response(
                    { 'message': 'User has already favorited this list.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            except ListFavorite.DoesNotExist:
                list_favorite = ListFavorite(
                    list=list,
                    rater=rater
                )

                try:
                    list_favorite.save()
                except ValidationError as ex:
                    return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        elif request.method == 'DELETE':
            """DELETE a ListFavorite"""
            try:
                list_favorite = ListFavorite.objects.get(rater=rater, list=list)
            except ListFavorite.DoesNotExist:
                return Response(
                    {'message': 'The user has not favorited that list.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            list_favorite.delete()
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    def _validate(self):
        """Validate values sent in POST/PUT body - 
            ensure all required properties are present,
            ensure all song objects include id and description keys,
            ensure all song IDs refer to existing objects
        Returns: error message string if error found, False otherwise.
        """
        REQUIRED_KEYS = [ 'name', 'description', 'songs' ]

        missing_keys = get_missing_keys(self.request.data, REQUIRED_KEYS)
        if len(missing_keys) > 0:
            return f"Request body is missing the following required properties: {', '.join(missing_keys)}."

        songs = self.request.data['songs']
        found_ids = []
        for song in songs:
            if 'id' not in song or 'description' not in song:
                return "All songs must contain `id` and `description` properties."
            song_id = song['id']

            try:
                Song.objects.get(pk=song_id)           
            except Song.DoesNotExist:
                return f"The song id {song_id} does not match an existing song."
            
            if song['id'] in found_ids:
                return "List cannot contain any duplicate songs."
            
            found_ids.append(song['id'])

        return False

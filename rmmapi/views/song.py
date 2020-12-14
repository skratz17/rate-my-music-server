"""Song ViewSet and Serializers"""
from rmmapi.views.genre import GenreSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.models import Artist, Genre, Rater, Song, SongGenre, SongSource

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')

class SongGenresSerializer(serializers.ModelSerializer):
    genre = GenreSerializer()
    class Meta:
        model = SongGenre
        fields = ('id', 'genre')

class SongSerializer(serializers.ModelSerializer):
    genres = SongGenresSerializer(many=True)
    class Meta:
        model = Song
        fields = ('id', 'name', 'year', 'artist', 'genres', 'sources', 'created_at')
        depth = 1

class SongViewSet(ViewSet):
    def create(self, request):
        """POST a new song"""
        missing_keys = self._get_missing_keys()
        if len(missing_keys) > 0:
            return Response(
                { 'message': f"Request body is missing the following required properties: {', '.join(missing_keys)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data['name']
        year = request.data['year']
        artist_id = request.data['artistId']
        genre_ids = request.data['genreIds']
        sources = request.data['sources']

        rater = Rater.objects.get(user=request.auth.user)

        song = Song(
            name=name,
            year=year,
            artist_id=artist_id,
            creator=rater,
            created_at=timezone.now()
        )

        try:
            song.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        for genre_id in genre_ids:
            song_genre = SongGenre(
                song=song,
                genre_id=genre_id
            )

            try:
                song_genre.save()
            except ValidationError as ex:
                return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        for source in sources:
            song_source = SongSource(
                song=song,
                service=source["service"],
                url=source["url"],
                isPrimary=source['isPrimary']
            )

            try:
                song_source.save()
            except ValidationError as ex:
                return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        serializer = SongSerializer(song) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """GET a single song by id"""
        song = get_object_or_404(Song, pk=pk)

        serializer = SongSerializer(song)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """PUT a song"""
        song = get_object_or_404(Song, pk=pk)

        self.check_object_permissions(request, song.creator)

        missing_keys = self._get_missing_keys()
        if len(missing_keys) > 0:
            return Response(
                { 'message': f"Request body is missing the following required properties: {', '.join(missing_keys)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data['name']
        year = request.data['year']
        artist_id = request.data['artistId']
        genre_ids = request.data['genreIds']
        sources = request.data['sources']

        song.name = name
        song.year = year
        song.artist_id = artist_id

        try:
            song.save()
        except ValidationError as ex:
            return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        # delete SongGenres where genre ids are no longer in the PUT body array
        song.genres.exclude(genre_id__in=genre_ids).delete()

        # then create new ones that don't already exist
        for genre_id in genre_ids:
            try:
                song.genres.get(genre_id=genre_id)
            except SongGenre.DoesNotExist:
                song_genre = SongGenre(
                    song=song,
                    genre_id=genre_id
                )

                try:
                    song_genre.save()
                except ValidationError as ex:
                    return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)

        urls = [ source['url'] for source in sources ]

        # delete SongSources where urls are no longer in the PUT body array
        song.sources.exclude(url__in=urls).delete()

        # then create new ones that don't already exist
        for source in sources:
            try:
                song_source = song.sources.get(url=source['url'])

                # if exists but isPrimary was flipped, update that in existing source
                if source['isPrimary'] != song_source.isPrimary:
                    song_source.isPrimary = source['isPrimary']
                    song_source.save()

            except SongSource.DoesNotExist:
                song_source = SongSource(
                    song=song,
                    service=source['service'],
                    url=source['url'],
                    isPrimary=source['isPrimary']
                )

                try:
                    song_source.save()
                except ValidationError as ex:
                    return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SongSerializer(song)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def _get_missing_keys(self):
        """Given the request.data for a POST/PUT request, return a list containing the
        string values of all required keys that were not found in the request body"""
        REQUIRED_KEYS = [
           'name', 'year', 'artistId', 'genreIds', 'sources'
        ]

        return [ key for key in REQUIRED_KEYS if not key in self.request.data ]

    def _validate(self):
        """Validate values sent in POST/PUT body - ensure all IDs refer to existing objects,
        and that all sources are objects with all required properties"""
        artist_id = self.request.data['artistId']

        try:
            Artist.objects.get(pk=artist_id)
        except Artist.DoesNotExist:
            return "`artistId` supplied does not match an existing artist." 

        genre_ids = self.request.data['genreIds']
        if len(genre_ids) == 0:
            return "You must specify at least one genre id in `genreIds` array."

        for genre_id in genre_ids:
            try:
                Genre.objects.get(pk=genre_id)
            except Genre.DoesNotExist:
                return f"The genre id {genre_id} does not match an existing genre."

        sources = self.request.data['sources']
        if len(sources) == 0:
            return "You must specify at least one source in `sources` array."

        for source in sources:
            if 'service' not in source or 'url' not in source or 'isPrimary' not in source:
                return "All sources must contain `service`, `url`, and `isPrimary` properties."

        primary_sources = [ source for source in sources if source['isPrimary'] == True ]
        if len(primary_sources) != 1:
            return "There must be one and only one primary source."

        return False
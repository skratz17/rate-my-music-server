"""Song ViewSet and Serializers"""
from django.db.models import Q, Avg
from django.db.models.expressions import Value
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.helpers import get_missing_keys, paginate
from rmmapi.models import Artist, Genre, Rater, Song, SongGenre, SongSource
from .rater import RaterSerializer

class SongGenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongGenre
        fields = ('id', 'genre')
        depth = 1

class SongSerializer(serializers.ModelSerializer):
    genres = SongGenresSerializer(many=True)
    creator = RaterSerializer()
    class Meta:
        model = Song
        fields = ('id', 'name', 'year', 'artist', 'genres', 'sources', 'created_at', 'avg_rating', 'creator')
        depth = 1

class SongViewSet(ViewSet):
    def create(self, request):
        """POST a new song"""
        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data['name']
        year = request.data['year']
        artist_id = request.data['artist_id']
        genre_ids = request.data['genre_ids']
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
                is_primary=source['is_primary']
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

        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        name = request.data['name']
        year = request.data['year']
        artist_id = request.data['artist_id']
        genre_ids = request.data['genre_ids']
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
                if source['is_primary'] != song_source.is_primary:
                    song_source.is_primary = source['is_primary']
                    song_source.save()

            except SongSource.DoesNotExist:
                song_source = SongSource(
                    song=song,
                    service=source['service'],
                    url=source['url'],
                    is_primary=source['is_primary']
                )

                try:
                    song_source.save()
                except ValidationError as ex:
                    return Response({ "message": ex.args[0] }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = SongSerializer(song)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        """DELETE a song by id"""
        song = get_object_or_404(Song, pk=pk)

        self.check_object_permissions(request, song.creator)

        song.delete()
        return Response({}, status.HTTP_204_NO_CONTENT)

    def list(self, request):
        """GET all songs with optional query string parameters:
            startYear - start year of songs to return results for
            endYear - end year of songs to return results for
            genres - comma-separated list of genre ids to return results for
            artist - id of artist to return results for
            q - search term to search song or artist names
            orderBy - field (one of: name, artist, year) to sort results by
            direction - direction to sort results in (one of: asc, desc)
        """
        songs = Song.objects.all()

        startYear = request.query_params.get('startYear', None)
        endYear = request.query_params.get('endYear', None)
        genres = request.query_params.get('genres', None)
        artist = request.query_params.get('artist', None)
        q = request.query_params.get('q', None)
        page = request.query_params.get('page', None)
        pageSize = request.query_params.get('pageSize', 10)

        if startYear is not None:
            try:
                startYear = int(startYear)
            except ValueError:
                startYear = 0
            songs = songs.filter(year__gte=startYear)
        
        if endYear is not None:
            try:
                endYear = int(endYear)
            except ValueError:
                endYear = 3000 
            songs = songs.filter(year__lte=endYear)
        
        if genres is not None:
            genres = genres.split(',')
            for genre in genres:
                songs = songs.filter(genres__genre_id=genre).distinct()

        if artist is not None:
            songs = songs.filter(artist_id=artist)

        if q is not None:
            songs = songs.filter(Q(artist__name__icontains=q) | Q(name__icontains=q))

        songs = self._sort_by_query_string_param(songs)

        count = len(songs)

        if page is not None:
            songs = paginate(songs, page, pageSize)

        serializer = SongSerializer(songs, many=True)
        return Response({
            "data": serializer.data,
            "count": count
        })
        
    def _validate(self):
        """Validate values sent in POST/PUT body - 
            ensure all required properties are present,
            ensure all IDs refer to existing objects,
            and that all sources are objects with all required properties
        Returns: error message string if error found, False otherwise.
        """
        REQUIRED_KEYS = [ 'name', 'year', 'artist_id', 'genre_ids', 'sources' ]

        missing_keys = get_missing_keys(self.request.data, REQUIRED_KEYS)
        if len(missing_keys) > 0:
                return f"Request body is missing the following required properties: {', '.join(missing_keys)}."

        artist_id = self.request.data['artist_id']

        try:
            Artist.objects.get(pk=artist_id)
        except Artist.DoesNotExist:
            return "`artistId` supplied does not match an existing artist." 

        genre_ids = self.request.data['genre_ids']
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
            if 'service' not in source or 'url' not in source or 'is_primary' not in source:
                return "All sources must contain `service`, `url`, and `is_primary` properties."

        primary_sources = [ source for source in sources if source['is_primary'] == True ]
        if len(primary_sources) != 1:
            return "There must be one and only one primary source."

        return False

    def _sort_by_query_string_param(self, songs):
        """Sort songs QuerySet by `orderBy` query string param"""
        orderable_fields_dict = {
            'name': Lower('name'),
            'artist': Lower('artist__name'),
            'avgRating': 'average_rating',
            'year': 'year'
        }

        order_by = self.request.query_params.get('orderBy', None)

        if order_by is not None and order_by in orderable_fields_dict:
            order_field = orderable_fields_dict[order_by]

            # sort in direction indicated by `direction` query string param
            # or ascending, by default
            direction = self.request.query_params.get('direction', 'asc')
            if direction == 'desc':
                if order_by == 'name' or order_by == 'artist':
                    order_field = order_field.desc()
                else:
                    order_field = '-' + order_field

            # add annotation for average_rating to sort by computed property
            if order_by == 'avgRating':
                songs = songs.annotate(
                    average_rating=Avg('ratings__rating')
                )

            songs = songs.order_by(order_field)

        return songs

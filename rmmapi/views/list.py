"""Genre ViewSet and Serializers"""
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.helpers import get_missing_keys
from rmmapi.models import List, Song

class ListViewSet(ViewSet):
    def create(self, request):
        """POST a new list"""
        error_message = self._validate()
        if error_message:
            return Response({'message': error_message}, status=status.HTTP_400_BAD_REQUEST)

        

    def _validate(self):
        """Validate values sent in POST/PUT body - 
            ensure all required properties are present,
            ensure all song objects include id and description keys,
            ensure all song IDs refer to existing objects
        Returns: error message string if error found, False otherwise.
        """
        REQUIRED_KEYS = [ 'name', 'songs' ]

        missing_keys = get_missing_keys(self.request.data, REQUIRED_KEYS)
        if len(missing_keys) > 0:
            return f"Request body is missing the following required properties: {', '.join(missing_keys)}."

        songs = self.request.data['songs']
        for song in songs:
            if 'id' not in song or 'description' not in song:
                return "All songs must contain `id` and `description` properties."
            song_id = song['id']
            try:
                Song.objects.get(pk=song_id)           
            except Song.DoesNotExist:
                return f"The song id {song_id} does not match an existing song."

        return False

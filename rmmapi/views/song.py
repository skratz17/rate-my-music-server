"""Artist ViewSet and Serializers"""
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework import status, serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response

class SongViewSet(ViewSet):
    def create(self, request):
        missing_keys = self._get_missing_keys()
        if len(missing_keys) > 0:
            return Response(
                { 'message': f"Request body is missing the following required properties: {', '.join(missing_keys)}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        

    def _get_missing_keys(self):
        """Given the request.data for a POST/PUT request, return a list containing the
        string values of all required keys that were not found in the request body"""
        REQUIRED_KEYS = [
            'name', 'artistId', 'genreIds', 'sources'
        ]

        return [ key for key in REQUIRED_KEYS if not key in self.request.data ]

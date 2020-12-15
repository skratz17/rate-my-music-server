"""Genre ViewSet and Serializers"""
from rest_framework import serializers, status
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.helpers import get_missing_keys
from rmmapi.models import List

REQUIRED_KEYS = [ 'name', 'songs' ]

class ListViewSet(ViewSet):
    def create(self, request):
        """POST a new list"""
        missing_keys = get_missing_keys(request.data, REQUIRED_KEYS)
        if len(missing_keys) > 0:
            return Response(
                { 'message': f"Request body is missing the following required properties: {', '.join(missing_keys)}."},
                status=status.HTTP_400_BAD_REQUEST
            )
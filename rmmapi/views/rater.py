"""Rater ViewSet and Serializers"""
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rmmapi.models import Rater

class UserSerializer(serializers.ModelSerializer):
    """JSON serializer for a user attached to a rater"""
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name')

class RaterSerializer(serializers.ModelSerializer):
    """JSON serializer for a rater"""
    user = UserSerializer()

    class Meta:
        model = Rater
        fields = ('id', 'bio', 'user')

class RaterViewSet(ViewSet):
    def list(self, request):
        """GET the logged-in rater"""
        rater = Rater.objects.get(user=request.auth.user)

        serializer = RaterSerializer(rater)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET a single rater"""
        rater = get_object_or_404(Rater, pk=pk)

        serializer = RaterSerializer(rater)
        return Response(serializer.data)

"""Rater ViewSet and Serializers"""
from django.contrib.auth import get_user_model
from rest_framework import serializers
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

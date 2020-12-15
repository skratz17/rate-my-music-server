"""server URL Configuration"""
from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from rmmapi.views import login_user, register_user
from rmmapi.views import ArtistViewSet, GenreViewSet, SongViewSet, ListViewSet, RatingViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'artists', ArtistViewSet, 'artist')
router.register(r'genres', GenreViewSet, 'genre')
router.register(r'songs', SongViewSet, 'song')
router.register(r'lists', ListViewSet, 'list')
router.register(r'ratings', RatingViewSet, 'rating')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user)
]

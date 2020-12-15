"""server URL Configuration"""
from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from rmmapi.views import login_user, register_user
from rmmapi.views import ArtistViewSet, GenreViewSet, SongViewSet
from rmmapi.views import ListViewSet, RatingViewSet, RaterViewSet, StatsViewSet

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'artists', ArtistViewSet, 'artist')
router.register(r'genres', GenreViewSet, 'genre')
router.register(r'songs', SongViewSet, 'song')
router.register(r'lists', ListViewSet, 'list')
router.register(r'ratings', RatingViewSet, 'rating')
router.register(r'raters', RaterViewSet, 'rater')
router.register(r'stats', StatsViewSet, 'stats')

urlpatterns = [
    path('', include(router.urls)),
    path('register', register_user),
    path('login', login_user)
]

"""Views Package"""
from .auth import login_user, register_user
from .artist import ArtistViewSet
from .genre import GenreViewSet
from .song import SongViewSet
from .list import ListViewSet
from .rating import RatingViewSet
from .rater import RaterViewSet

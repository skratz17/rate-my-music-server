from django.db import models
from .rater import get_deleted_rater_instance

class List(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    creator = models.ForeignKey("rmmapi.Rater", on_delete=models.SET(get_deleted_rater_instance))
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False)

    @property
    def fav_count(self):
        return self.favorites.count()

    @property
    def has_rater_favorited(self):
        return self.__has_rater_favorited

    @has_rater_favorited.setter
    def has_rater_favorited(self, rater):
        try:
            self.favorites.get(rater=rater)
            self.__has_rater_favorited = True
        except:
            self.__has_rater_favorited = False

from django.db import models
from statistics import StatisticsError, mean
from .rater import get_deleted_rater_instance

class Song(models.Model):
    creator = models.ForeignKey("rmmapi.Rater", on_delete=models.SET(get_deleted_rater_instance))
    artist = models.ForeignKey("rmmapi.Artist", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False)

    @property
    def avg_rating(self):
        ratings = self.ratings.all()

        try:
            return mean([ rating.rating for rating in ratings ])
        except StatisticsError:
            return None

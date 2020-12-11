from django.db import models
from .rater import get_deleted_rater_instance

class Artist(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=1000)
    founded_year = models.DateField(auto_now=False, auto_now_add=False)
    creator = models.ForeignKey("rmmapi.Rater", on_delete=models.SET(get_deleted_rater_instance))

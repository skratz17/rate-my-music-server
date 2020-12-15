from django.db import models
from .rater import get_deleted_rater_instance

class ListFavorite(models.Model):
    list = models.ForeignKey("rmmapi.List", on_delete=models.CASCADE, related_name="favorites")
    rater = models.ForeignKey("rmmapi.Rater", on_delete=models.SET(get_deleted_rater_instance))

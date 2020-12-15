from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .rater import get_deleted_rater_instance

class Rating(models.Model):
    rating = models.IntegerField(validators=[ MinValueValidator(1), MaxValueValidator(5) ])
    review = models.CharField(max_length=2000)
    song = models.ForeignKey("rmmapi.Song", on_delete=models.CASCADE, related_name="ratings")
    rater = models.ForeignKey("rmmapi.Rater", on_delete=models.SET(get_deleted_rater_instance))
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False)

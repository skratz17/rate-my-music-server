from django.db import models
from .rater import get_deleted_rater_instance

class List(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    creator = models.ForeignKey("rmmapi.Rater", on_delete=models.SET(get_deleted_rater_instance))
    created_at = models.DateTimeField(auto_now=False, auto_now_add=False)

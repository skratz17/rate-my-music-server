from django.db import models
from django.contrib.auth import get_user_model

class Rater(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    bio = models.CharField(max_length=500)

DELETED_RATER_ID = 1

def get_deleted_rater_instance():
    return Rater.objects.get(pk=DELETED_RATER_ID)

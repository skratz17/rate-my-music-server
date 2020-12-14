from django.db import models

class SongSource(models.Model):
    song = models.ForeignKey("rmmapi.Song", on_delete=models.CASCADE, related_name="sources")
    url = models.CharField(max_length=200)
    service = models.CharField(max_length=50)
    isPrimary = models.BooleanField()

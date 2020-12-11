from django.db import models

class ListSong(models.Model):
    list = models.ForeignKey("rmmapi.List", on_delete=models.CASCADE)
    song = models.ForeignKey("rmmapi.Song", on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)

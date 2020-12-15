from django.db import models

class ListSong(models.Model):
    list = models.ForeignKey("rmmapi.List", on_delete=models.CASCADE, related_name="songs")
    song = models.ForeignKey("rmmapi.Song", on_delete=models.CASCADE, related_name="lists")
    description = models.CharField(max_length=1000)

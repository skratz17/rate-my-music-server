from django.db import models

class SongGenre(models.Model):
    song = models.ForeignKey("rmmapi.Song", on_delete=models.CASCADE)
    genre = models.ForeignKey("rmmapi.Genre", on_delete=models.CASCADE)

#!/bin/bash

rm -rf rmmapi/migrations
rm db.sqlite3
python manage.py makemigrations rmmapi
python manage.py migrate
python manage.py loaddata users
python manage.py loaddata tokens
python manage.py loaddata raters
python manage.py loaddata artists
python manage.py loaddata songs
python manage.py loaddata genres
python manage.py loaddata lists
python manage.py loaddata ratings
python manage.py loaddata song_sources
python manage.py loaddata song_genres
python manage.py loaddata list_favorites
python manage.py loaddata list_songs

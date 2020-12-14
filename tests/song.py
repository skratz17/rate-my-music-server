import json
from rest_framework import status
from rest_framework.test import APITestCase
from rmmapi.models import Genre, Artist

class SongTests(APITestCase):
    def setUp(self):
        """Create an account, two genres, one artist"""
        data = {
            'username': 'jweckert17',
            'email': 'jweckert17@gmail.com',
            'password': 'test',
            'first_name': 'Jacob',
            'last_name': 'Eckert',
            'bio': 'I am just a cool boi.'
        }

        response = self.client.post('/register', data, format='json')
        json_response = json.loads(response.content)
        self.token = json_response['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        genre_1 = Genre(name="Indie Pop")
        genre_1.save()

        genre_2 = Genre(name="Indie Folk")
        genre_2.save()

        artist = Artist(
            name="The Magnetic Fields",
            description="A great band.",
            founded_year=1990,
            creator_id=1
        )

        artist.save()

    def test_create_song_missing_properties(self):
        # missing artistId
        data = {
            'name': 'Save a Secret for the Moon',
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A' }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], 'Request body is missing the following required properties: artistId.')

    def test_create_song_invalid_artist_id(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'artistId': 666,
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A' }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "`artistId` supplied does not match an existing artist.")

    def test_create_song_empty_genre_ids(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'artistId': 1,
            'genreIds': [ ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A' }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "You must specify at least one genre id in `genreIds` array.")

    def test_create_song_invalid_genre_id(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'artistId': 1,
            'genreIds': [ 1, 666 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A' }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "The genre id 666 does not match an existing genre.")

    def test_create_song_empty_sources(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ ]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "You must specify at least one source in `sources` array.")

    def test_create_song_invalid_source(self):
        # using `platform` key instead of `service` for source
        data = {
            'name': 'Save a Secret for the Moon',
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ { 'platform': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A' }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "All sources must contain `service` and `url` properties.")

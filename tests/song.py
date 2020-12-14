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
            'year': 1996,
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': True }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], 'Request body is missing the following required properties: artistId.')

    def test_create_song_invalid_artist_id(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artistId': 666,
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': True }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "`artistId` supplied does not match an existing artist.")

    def test_create_song_empty_genre_ids(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artistId': 1,
            'genreIds': [ ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': True }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "You must specify at least one genre id in `genreIds` array.")

    def test_create_song_invalid_genre_id(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artistId': 1,
            'genreIds': [ 1, 666 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': True }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "The genre id 666 does not match an existing genre.")

    def test_create_song_empty_sources(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
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
            'year': 1996,
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ { 'platform': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A' }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "All sources must contain `service`, `url`, and `isPrimary` properties.")

    def test_create_song_multiple_primary_sources(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ 
                { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': True }, 
                { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=8dNaXUwIeao', 'isPrimary': True }
            ]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "There must be one and only one primary source.")

    def test_create_valid_song(self):
        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': True }]
        }

        response = self.client.post('/songs', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        song = json.loads(response.content)
        self.assertEqual(song['id'], 1)
        self.assertEqual(song['name'], 'Save a Secret for the Moon')
        self.assertEqual(song['year'], 1996)
        self.assertEqual(song['artist']['name'], 'The Magnetic Fields')
        self.assertEqual(song['genres'][0]['genre']['name'], 'Indie Pop')
        self.assertEqual(song['sources'][0]['service'], 'YouTube')

    def test_get_song_invalid_id(self):
        response = self.client.get('/songs/1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_song(self):
        self.test_create_valid_song()

        response = self.client.get('/songs/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        song = json.loads(response.content)
        self.assertEqual(song['id'], 1)
        self.assertEqual(song['name'], 'Save a Secret for the Moon')
        self.assertEqual(song['year'], 1996)
        self.assertEqual(song['artist']['name'], 'The Magnetic Fields')
        self.assertEqual(song['genres'][0]['genre']['name'], 'Indie Pop')
        self.assertEqual(song['sources'][0]['service'], 'YouTube')

    def test_update_invalid_song_id(self):
        data = {
            'name': 'Strange Powers',
            'year': 1995,
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=8dNaXUwIeao', 'isPrimary': True }]
        }

        response = self.client.put('/songs/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_song_when_not_creator(self):
        # create song as Jacob
        self.test_create_valid_song()

        # create second user and use their credentials
        data = {
            'username': 'test',
            'email': 'test@gmail.com',
            'password': 'test',
            'first_name': 'Test',
            'last_name': 'NotEckert',
            'bio': 'I am just a test boi.'
        }

        response = self.client.post('/register', data, format='json')
        json_response = json.loads(response.content)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + json_response['token'])

        data = {
            'name': 'Strange Powers',
            'year': 1995,
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=8dNaXUwIeao', 'isPrimary': True }]
        }

        response = self.client.put('/songs/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_update_song(self):
        self.test_create_valid_song()

        data = {
            'name': 'Strange Powers',
            'year': 1995,
            'artistId': 1,
            'genreIds': [ 2 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=8dNaXUwIeao', 'isPrimary': True }]
        }

        response = self.client.put('/songs/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        song = json.loads(response.content)
        self.assertEqual(song['id'], 1)
        self.assertEqual(song['name'], 'Strange Powers')
        self.assertEqual(song['year'], 1995)
        self.assertEqual(song['artist']['name'], 'The Magnetic Fields')
        self.assertEqual(len(song['genres']), 1)
        self.assertEqual(song['genres'][0]['genre']['name'], 'Indie Folk')
        self.assertEqual(len(song['sources']), 1)
        self.assertEqual(song['sources'][0]['url'], 'https://www.youtube.com/watch?v=8dNaXUwIeao')

    def test_update_song_with_new_primary_source(self):
        self.test_create_valid_song()

        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ 
                { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': False },  
                { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=8dNaXUwIeao', 'isPrimary': True }
            ]
        }

        response = self.client.put('/songs/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        song = json.loads(response.content)
        self.assertEqual(len(song['sources']), 2)
        self.assertEqual(song['sources'][0]['url'], 'https://www.youtube.com/watch?v=4rk_9cYOp8A')
        self.assertEqual(song['sources'][0]['isPrimary'], False)
        self.assertEqual(song['sources'][1]['url'], 'https://www.youtube.com/watch?v=8dNaXUwIeao')
        self.assertEqual(song['sources'][1]['isPrimary'], True)

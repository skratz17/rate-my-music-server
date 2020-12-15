import json
from rest_framework import status
from rest_framework.test import APITestCase
from rmmapi.models import Genre, Artist

class RatingTests(APITestCase):
    def setUp(self):
        """Create an account, one genre, one artist, one song"""
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

        genre = Genre(name="Indie Pop")
        genre.save()

        artist = Artist(
            name="The Magnetic Fields",
            description="A great band.",
            founded_year=1990,
            creator_id=1
        )

        artist.save()

        song_data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artistId': 1,
            'genreIds': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'isPrimary': True }]
        }
        self.client.post('/songs', song_data, format='json')

    def test_create_rating_missing_key(self):
        # missing review key
        data = {
            "rating": 3,
            "songId": 1
        }

        response = self.client.post('/ratings', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], 'Request body is missing the following required properties: review.')

    def test_create_rating_invalid_song_id(self):
        data = {
            "rating": 3,
            "songId": 666,
            "review": "Devilishly good."
        }

        response = self.client.post('/ratings', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "The song id 666 does not match an existing song.")

    def test_create_duplicate_rating_for_song(self):
        data = {
            "rating": 3,
            "songId": 1,
            "review": "So good!"
        }

        self.client.post('/ratings', data, format='json')
        response = self.client.post('/ratings', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "User has already rated that song.")

    def test_create_valid_rating(self):
        data = {
            "rating": 3,
            "songId": 1,
            "review": "So good!"
        }

        response = self.client.post('/ratings', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        rating = json.loads(response.content)
        self.assertEqual(rating['id'], 1)
        self.assertEqual(rating['rating'], 3)
        self.assertEqual(rating['review'], 'So good!')
        self.assertEqual(rating['rater']['user']['username'], 'jweckert17')
        self.assertEqual(rating['song']['name'], 'Save a Secret for the Moon')

    def test_get_rating_by_invalid_id(self):
        response = self.client.get('/ratings/1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_valid_rating(self):
        self.test_create_valid_rating()

        response = self.client.get('/ratings/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rating = json.loads(response.content)
        self.assertEqual(rating['id'], 1)
        self.assertEqual(rating['rating'], 3)
        self.assertEqual(rating['review'], 'So good!')
        self.assertEqual(rating['rater']['user']['username'], 'jweckert17')
        self.assertEqual(rating['song']['name'], 'Save a Secret for the Moon')

    def test_update_rating_invalid_id(self):
        data = {
            "rating": 5,
            "songId": 1,
            "review": "Actually, perfect"
        }

        response = self.client.put('/ratings/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_rating_as_non_creator(self):
        # create rating as Jacob
        self.test_create_valid_rating()

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
            "rating": 5,
            "songId": 1,
            "review": "Actually, perfect"
        }

        response = self.client.put('/ratings/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_valid_rating(self):
        self.test_create_valid_rating()

        data = {
            "rating": 5,
            "songId": 1,
            "review": "Actually, perfect"
        }

        response = self.client.put('/ratings/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rating = json.loads(response.content)
        self.assertEqual(rating['id'], 1)
        self.assertEqual(rating['rating'], 5)
        self.assertEqual(rating['review'], 'Actually, perfect')

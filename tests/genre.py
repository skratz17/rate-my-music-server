import json
from rest_framework import status
from rest_framework.test import APITestCase
from rmmapi.models import Genre

class GenreTests(APITestCase):
    def setUp(self):
        """Create an account and set up auth header for future HTTP requests. Create two genres."""
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

    def test_get_all_genres(self):
        """Test getting all genres"""
        response = self.client.get('/genres')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        genres = json.loads(response.content)
        self.assertEqual(genres['count'], 2)

        self.assertEqual(genres['data'][0]['id'], 1)
        self.assertEqual(genres['data'][0]['name'], 'Indie Pop')

        self.assertEqual(genres['data'][1]['id'], 2)
        self.assertEqual(genres['data'][1]['name'], 'Indie Folk')

    def test_get_all_genres_by_search_term_with_one_match(self):
        """Test getting genres by search term only one matches"""
        response = self.client.get('/genres?q=folk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        genres = json.loads(response.content)
        self.assertEqual(genres['count'], 1)

        self.assertEqual(genres['data'][0]['id'], 2)
        self.assertEqual(genres['data'][0]['name'], 'Indie Folk')

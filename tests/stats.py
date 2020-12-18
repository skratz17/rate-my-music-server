import json
from rest_framework import status
from rest_framework.test import APITestCase
from rmmapi.models import Genre

class StatsTests(APITestCase):
    def setUp(self):
        """Create an account and a genre"""
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

    def test_get_empty_stats(self):
        response = self.client.get('/stats')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        stats = json.loads(response.content)
        self.assertEqual(stats['users'], 1) # will be at least 1 always cause of the setup user 
        self.assertEqual(stats['artists'], 0)
        self.assertEqual(stats['songs'], 0)
        self.assertEqual(stats['lists'], 0)

    def test_get_populated_stats(self):
        # create two artists
        data = {
            'name': 'The Magnetic Fields',
            'founded_year': 1990,
            'description': 'An amazing band.'
        }

        self.client.post('/artists', data, format='json')

        data = {
            'name': 'of Montreal',
            'founded_year': 1996,
            'description': 'Such a good band.'
        }

        self.client.post('/artists', data, format='json')

        # create one song
        data = {
            'name': 'Save a Secret for the Moon',
            'year': 1996,
            'artist_id': 1,
            'genre_ids': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'is_primary': True }]
        }
        self.client.post('/songs', data, format='json')

        # create three lists
        data = {
            "name": "My First List",
            "description": "Here is my list.",
            "songs": [
                { "id": 1, "description": "secret saving" }
            ]
        }
        self.client.post('/lists', data, format='json')

        data = {
            "name": "My Second List",
            "description": "Here is my list.",
            "songs": [
                { "id": 1, "description": "secret saving" }
            ]
        }
        self.client.post('/lists', data, format='json')

        data = {
            "name": "My Third List",
            "description": "Here is my list.",
            "songs": [
                { "id": 1, "description": "secret saving" }
            ]
        }
        self.client.post('/lists', data, format='json')

        response = self.client.get('/stats')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        stats = json.loads(response.content)
        self.assertEqual(stats['users'], 1) 
        self.assertEqual(stats['artists'], 2)
        self.assertEqual(stats['songs'], 1)
        self.assertEqual(stats['lists'], 3)
        
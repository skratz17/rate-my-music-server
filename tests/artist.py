import json
from rest_framework import status
from rest_framework.test import APITestCase

class ArtistTests(APITestCase):
    def setUp(self):
        """Create an account and set up auth header for future HTTP requests"""
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

    def test_create_artist(self):
        """Create a valid artist"""
        data = {
            'name': 'The Magnetic Fields',
            'founded_year': 1990,
            'description': 'An amazing band.'
        }

        response = self.client.post('/artists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_artist = json.loads(response.content)
        self.assertEqual(created_artist['id'], 1)
        self.assertEqual(created_artist['name'], 'The Magnetic Fields')
        self.assertEqual(created_artist['founded_year'], 1990)
        self.assertEqual(created_artist['description'], 'An amazing band.')

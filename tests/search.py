import json
from rest_framework import status
from rest_framework.test import APITestCase
from rmmapi.models import Genre

class SearchTests(APITestCase):
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

    def test_search_results_with_empty_db(self):
        response = self.client.get('/search?q=test')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = json.loads(response.content)

        self.assertIn('artists', results)
        self.assertIn('songs', results)
        self.assertIn('lists', results)

        self.assertEqual(len(results['artists']), 0)
        self.assertEqual(len(results['songs']), 0)
        self.assertEqual(len(results['lists']), 0)

    def test_search_results_matching_artists(self):
        self._create_artist('The Magnetic Fields')

        response = self.client.get('/search?q=mag')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = json.loads(response.content)

        self.assertEqual(len(results['artists']), 1)
        self.assertEqual(len(results['songs']), 0)
        self.assertEqual(len(results['lists']), 0)

        self.assertEqual(results['artists'][0]['name'], 'The Magnetic Fields')

    def test_search_results_matching_songs(self):
        self._create_artist('zzz')
        self._create_song('ABC', 1)
        self._create_song('CDE', 1)

        response = self.client.get('/search?q=c')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = json.loads(response.content)

        self.assertEqual(len(results['artists']), 0)
        self.assertEqual(len(results['songs']), 2)
        self.assertEqual(len(results['lists']), 0)

        self.assertEqual(results['songs'][0]['name'], 'ABC')
        self.assertEqual(results['songs'][1]['name'], 'CDE')

    def test_search_results_matching_lists(self):
        self._create_artist('ZZZ')
        self._create_song('ZZZ', 1)
        self._create_list('My List')

        response = self.client.get('/search?q=list')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = json.loads(response.content)

        self.assertEqual(len(results['artists']), 0)
        self.assertEqual(len(results['songs']), 0)
        self.assertEqual(len(results['lists']), 1)

        self.assertEqual(results['lists'][0]['name'], 'My List')

    def test_search_results_all_matches(self):
        self._create_artist('The Magnetic Fields')
        self._create_song('Famous', 1)
        self._create_list('Bangers')

        response = self.client.get('/search?q=a')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = json.loads(response.content)

        self.assertEqual(len(results['artists']), 1)
        self.assertEqual(len(results['songs']), 1)
        self.assertEqual(len(results['lists']), 1)

        self.assertEqual(results['artists'][0]['name'], 'The Magnetic Fields')
        self.assertEqual(results['songs'][0]['name'], 'Famous')
        self.assertEqual(results['lists'][0]['name'], 'Bangers')

    def _create_artist(self, name):
        data = {
            'name': name,
            'founded_year': 1990,
            'description': 'An amazing band.'
        }

        self.client.post('/artists', data, format='json')


    def _create_song(self, name, artist_id):
        data = {
            'name': name,
            'year': 1996,
            'artist_id': artist_id,
            'genre_ids': [ 1 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=4rk_9cYOp8A', 'is_primary': True }]
        }

        self.client.post('/songs', data, format='json')

    def _create_list(self, name):
        data = {
            "name": name,
            "description": "Here is my list.",
            "songs": [
                { "id": 1, "description": "secret saving" }
            ]
        }
        self.client.post('/lists', data, format='json')
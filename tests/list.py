import json
from rest_framework import status
from rest_framework.test import APITestCase
from rmmapi.models import Genre, Artist

class ListTests(APITestCase):
    def setUp(self):
        """Create an account, two genres, two artists, two songs"""
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

        artist = Artist(
            name="of Montreal",
            description="The best band.",
            founded_year=1996,
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

        song_data = {
            'name': 'Baby',
            'year': 1997,
            'artistId': 2,
            'genreIds': [ 1, 2 ],
            'sources': [ { 'service': 'YouTube', 'url': 'https://www.youtube.com/watch?v=pPBRwEmSESw', 'isPrimary': True }]
        }       
        self.client.post('/songs', song_data, format='json')

    def test_create_list_missing_keys(self):
        data = {
            "name": "My List",
            "songs": [
                { "id": 1, "description": "secret saving" },
                { "id": 2, "description": "baby song" }
            ]
        }
        response = self.client.post('/lists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], 'Request body is missing the following required properties: description.')

    def test_create_list_invalid_song_id(self):
        data = {
            "name": "My List",
            "description": "Here is my list.",
            "songs": [
                { "id": 1, "description": "secret saving" },
                { "id": 2, "description": "baby song" },
                { "id": 3, "description": "this song does not exist"}
            ]
        }
        response = self.client.post('/lists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "The song id 3 does not match an existing song.")

    def test_create_list_missing_song_key(self):
        data = {
            "name": "My List",
            "description": "Here is my list.",
            "songs": [
                { "id": 1 },
                { "id": 2, "description": "baby song" }
            ]
        }
        response = self.client.post('/lists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "All songs must contain `id` and `description` properties.")

    def test_create_list_duplicate_songs(self):
        data = {
            "name": "My List",
            "description": "Here is my list.",
            "songs": [
                { "id": 1, "description": "secret saving" },
                { "id": 1, "description": "secret saving again" }
            ]
        }
        response = self.client.post('/lists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], "List cannot contain any duplicate songs.")

    def test_create_valid_list(self):
        data = {
            "name": "My List",
            "description": "Here is my list.",
            "songs": [
                { "id": 1, "description": "secret saving" },
                { "id": 2, "description": "baby song" }
            ]
        }
        response = self.client.post('/lists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        list = json.loads(response.content)
        self.assertEqual(list['id'], 1)
        self.assertEqual(list['name'], 'My List')
        self.assertEqual(list['description'], 'Here is my list.')
        self.assertEqual(list['creator']['user']['username'], 'jweckert17')
        self.assertEqual(len(list['songs']), 2)
        self.assertEqual(list['songs'][0]['song']['name'], 'Save a Secret for the Moon')
        self.assertEqual(list['songs'][0]['song']['artist']['name'], 'The Magnetic Fields')
        self.assertEqual(len(list['songs'][0]['song']['sources']), 1)
        self.assertEqual(list['songs'][0]['description'], 'secret saving')
        self.assertEqual(list['songs'][1]['song']['name'], 'Baby')
        self.assertEqual(list['songs'][1]['song']['artist']['name'], 'of Montreal')
        self.assertEqual(len(list['songs'][1]['song']['sources']), 1)
        self.assertEqual(list['songs'][1]['description'], 'baby song')

    def test_get_by_invalid_id(self):
        response = self.client.get('/lists/1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_by_id(self):
        self.test_create_valid_list()

        response = self.client.get('/lists/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        list = json.loads(response.content)
        self.assertEqual(list['id'], 1)
        self.assertEqual(list['name'], 'My List')
        self.assertEqual(list['description'], 'Here is my list.')
        self.assertEqual(list['creator']['user']['username'], 'jweckert17')
        self.assertEqual(len(list['songs']), 2)
        self.assertEqual(list['songs'][0]['song']['name'], 'Save a Secret for the Moon')
        self.assertEqual(list['songs'][0]['song']['artist']['name'], 'The Magnetic Fields')
        self.assertEqual(len(list['songs'][0]['song']['sources']), 1)
        self.assertEqual(list['songs'][0]['description'], 'secret saving')
        self.assertEqual(list['songs'][1]['song']['name'], 'Baby')
        self.assertEqual(list['songs'][1]['song']['artist']['name'], 'of Montreal')
        self.assertEqual(len(list['songs'][1]['song']['sources']), 1)
        self.assertEqual(list['songs'][1]['description'], 'baby song')

    def test_update_by_invalid_id(self):
        data = {
            "name": "My UPDATED List",
            "description": "Here is my UPDATED list.",
            "songs": [
                { "id": 2, "description": "baby song" }
            ]
        }

        response = self.client.put('/lists/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_as_non_creator(self):
        # create list as Jacob
        self.test_create_valid_list()

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
            "name": "My UPDATED List",
            "description": "Here is my UPDATED list.",
            "songs": [
                { "id": 2, "description": "baby song" }
            ]
        }

        response = self.client.put('/lists/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_valid_list(self):
        self.test_create_valid_list()

        data = {
            "name": "My UPDATED List",
            "description": "Here is my UPDATED list.",
            "songs": [
                { "id": 2, "description": "UPDATED song" }
            ]
        }

        response = self.client.put('/lists/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        list = json.loads(response.content)
        self.assertEqual(list['id'], 1)
        self.assertEqual(list['name'], 'My UPDATED List')
        self.assertEqual(list['description'], 'Here is my UPDATED list.')
        self.assertEqual(list['creator']['user']['username'], 'jweckert17')
        self.assertEqual(len(list['songs']), 1)
        self.assertEqual(list['songs'][0]['song']['name'], 'Baby')
        self.assertEqual(list['songs'][0]['song']['artist']['name'], 'of Montreal')
        self.assertEqual(len(list['songs'][0]['song']['sources']), 1)
        self.assertEqual(list['songs'][0]['description'], 'UPDATED song')

    def test_delete_list_by_invalid_id(self):
        response = self.client.delete('/lists/1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_list_as_non_creator(self):
        # create list as Jacob
        self.test_create_valid_list()

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

        response = self.client.delete('/lists/1')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_valid_list(self):
        self.test_create_valid_list()

        response = self.client.delete('/lists/1')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_all_lists(self):
        self.test_create_valid_list()
        self._create_second_valid_list_as_second_user()

        response = self.client.get('/lists')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        lists = json.loads(response.content)
        self.assertEqual(len(lists), 2)
        self.assertEqual(lists[0]['name'], 'My List')
        self.assertEqual(lists[1]['name'], 'My Second List')

    def test_get_all_lists_by_song_id(self):
        self.test_create_valid_list()
        self._create_second_valid_list_as_second_user()

        response = self.client.get('/lists?songId=1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        lists = json.loads(response.content)
        self.assertEqual(len(lists), 1)
        self.assertEqual(lists[0]['name'], 'My List')

    def test_get_all_lists_by_user_id(self):
        self.test_create_valid_list()
        self._create_second_valid_list_as_second_user()

        response = self.client.get('/lists?userId=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        lists = json.loads(response.content)
        self.assertEqual(len(lists), 1)
        self.assertEqual(lists[0]['name'], 'My Second List')

    def test_favorite_list_by_invalid_id(self):
        response = self.client.post('/lists/1/favorite')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_favorite_list(self):
        self.test_create_valid_list()

        response = self.client.post('/lists/1/favorite')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_favorite_by_invalid_list_id(self):
        response = self.client.delete('/lists/1/favorite')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_favorite_that_does_not_exist(self):
        self.test_create_valid_list()

        response = self.client.delete('/lists/1/favorite')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], 'The user has not favorited that list.')

    def test_delete_favorite(self):
        self.test_favorite_list()

        response = self.client.delete('/lists/1/favorite')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def _create_second_valid_list_as_second_user(self):
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
            "name": "My Second List",
            "description": "Here is my second list.",
            "songs": [
                { "id": 2, "description": "baby song" }
            ]
        }

        response = self.client.post('/lists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

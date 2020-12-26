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

    def test_create_artist_missing_field(self):
        """Create an artist with missing required field"""
        # missing description field
        data = {
            'name': 'The Magnetic Fields',
            'founded_year': 1990
        }

        response = self.client.post('/artists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        error_message = json.loads(response.content)
        self.assertEqual(error_message['message'], 'Request body is missing the following required properties: description.')

    def test_create_artist_invalid_year(self):
        """Create an artist with an invalid year value"""
        data = {
            'name': 'The Magnetic Fields',
            'founded_year': 'aosidj',
            'description': 'Such a good band.'
        }

        response = self.client.post('/artists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_artist_invalid_name(self):
        """Create an artist with an overlong name value"""
        data = {
            'name': 'The Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic FieldsThe Magnetic Fields',
            'founded_year': 'aosidj',
            'description': 'Such a good band.'
        }

        response = self.client.post('/artists', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_artist(self):
        """Test getting a single valid artist by ID"""
        self.test_create_artist()

        response = self.client.get('/artists/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        artist = json.loads(response.content)
        self.assertEqual(artist['id'], 1)
        self.assertEqual(artist['name'], 'The Magnetic Fields')
        self.assertEqual(artist['founded_year'], 1990)
        self.assertEqual(artist['description'], 'An amazing band.')

    def test_get_artist_invalid_id(self):
        """Test getting a single artist by nonexistent ID"""
        response = self.client.get('/artists/1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_artist(self):
        """Test valid deletion of an artist"""
        self.test_create_artist()

        response = self.client.delete('/artists/1')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_artist_invalid_id(self):
        """Test deleting an artist by nonexistent ID"""
        response = self.client.delete('/artists/1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_artist_as_non_creator_user(self):
        """Test attempting to delete an artist as a user who is not that artist's creator"""
        # create artist as Jacob
        self.test_create_artist()

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
        response = self.client.delete('/artists/1')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_artist(self):
        """Test successfully updating an artist"""
        self.test_create_artist()

        data = {
            'name': 'of Montreal',
            'founded_year': 1996,
            'description': 'So good.'
        }

        response = self.client.put('/artists/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        updated_artist = json.loads(response.content)
        self.assertEqual(updated_artist['id'], 1)
        self.assertEqual(updated_artist['name'], 'of Montreal')
        self.assertEqual(updated_artist['founded_year'], 1996)
        self.assertEqual(updated_artist['description'], 'So good.')

    def test_update_artist_invalid_id(self):
        """Test attempting to update an artist by nonexistent id"""
        data = {
            'name': 'of Montreal',
            'founded_year': 1996,
            'description': 'So good.'
        }

        response = self.client.put('/artists/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_artist_missing_field(self):
        """Test attempting to update an artist with a missing field in request body"""
        self.test_create_artist()

        # missing description
        data = {
            'name': 'of Montreal',
            'founded_year': 1996,
        }

        response = self.client.put('/artists/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_artist_as_non_creator_user(self):
        """Test attempting to update an artist as a user who did not create the artist"""
        # create artist as Jacob
        self.test_create_artist()

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

        # attempt to put to the artist created by Jacob as second user
        data = {
            'name': 'of Montreal',
            'founded_year': 1996,
            'description': 'So good.'
        }

        response = self.client.put('/artists/1', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


    def test_get_all_artists(self):
        """Test getting all artists"""
        self.test_create_artist()

        response = self.client.get('/artists')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        artists = json.loads(response.content)
        self.assertEqual(artists['count'], 1)
        self.assertEqual(artists['data'][0]['id'], 1)
        self.assertEqual(artists['data'][0]['name'], 'The Magnetic Fields')
        self.assertEqual(artists['data'][0]['founded_year'], 1990)
        self.assertEqual(artists['data'][0]['description'], 'An amazing band.')

    def test_get_all_artists_by_matching_search_term(self):
        """Test getting all artists using the q query string parameter and a matching name"""
        self.test_create_artist()

        response = self.client.get('/artists?q=mag')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        artists = json.loads(response.content)
        self.assertEqual(artists['count'], 1)
        self.assertEqual(artists['data'][0]['id'], 1)
        self.assertEqual(artists['data'][0]['name'], 'The Magnetic Fields')
        self.assertEqual(artists['data'][0]['founded_year'], 1990)
        self.assertEqual(artists['data'][0]['description'], 'An amazing band.')

    def test_get_all_artists_by_non_matching_search_term(self):
        """Test getting all artists using the q query string parameter and a non-matching name"""
        self.test_create_artist()

        response = self.client.get('/artists?q=aosdifjoaisfj')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        artists = json.loads(response.content)
        self.assertEqual(artists['count'], 0)

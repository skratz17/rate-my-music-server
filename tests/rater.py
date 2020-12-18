import json
from rest_framework import status
from rest_framework.test import APITestCase

class RaterTests(APITestCase):
    def setUp(self):
        """Create an account"""
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

    def test_get_rater_invalid_id(self):
        response = self.client.get('/raters/666')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_valid_rater(self):
        response = self.client.get('/raters/1')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rater = json.loads(response.content)
        self.assertEqual(rater['id'], 1)
        self.assertEqual(rater['bio'], 'I am just a cool boi.')
        self.assertEqual(rater['user']['username'], 'jweckert17')

    def test_get_logged_in_rater(self):
        response = self.client.get('/raters')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        rater = json.loads(response.content)
        self.assertEqual(rater['id'], 1)
        self.assertEqual(rater['bio'], 'I am just a cool boi.')
        self.assertEqual(rater['user']['username'], 'jweckert17')

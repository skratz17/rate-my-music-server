import json
from rest_framework import status
from rest_framework.test import APITestCase

class AuthTests(APITestCase):
    def test_register_user(self):
        data = {
            'username': 'jweckert17',
            'email': 'jweckert17@gmail.com',
            'password': 'test',
            'first_name': 'Jacob',
            'last_name': 'Eckert',
            'bio': 'I am just a cool boi.'
        }

        response = self.client.post('/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_response = json.loads(response.content)
        self.assertIn('token', json_response)

    def test_register_user_bad_request(self):
        # missing password field
        data = {
            'username': 'jweckert17',
            'email': 'jweckert17@gmail.com',
            'first_name': 'Jacob',
            'last_name': 'Eckert',
            'bio': 'I am just a cool boi.'
        }

        response = self.client.post('/register', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        json_response = json.loads(response.content)
        self.assertEqual(json_response["message"], "Field `password` is required.")

    def test_login_user(self):
        self.test_register_user()

        data = {
            'username': 'jweckert17',
            'password': 'test'
        }

        response = self.client.post('/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], True)
        self.assertIn('token', json_response)

    def test_login_user_bad_request(self):
        # missing password field
        data = {
            'username': 'jweckert17'
        }

        response = self.client.post('/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        json_response = json.loads(response.content)
        self.assertEqual(json_response['message'], "Field `password` is required.")

    def test_login_user_invalid_password(self):
        self.test_register_user()

        data = {
            'username': 'jweckert17',
            'password': 'testt' # valid password is test
        }

        response = self.client.post('/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], False)

    def test_login_user_invalid_username(self):
        self.test_register_user()

        data = {
            'username': 'jweckert170', # valid username is jweckert17
            'password': 'test' 
        }

        response = self.client.post('/login', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        json_response = json.loads(response.content)
        self.assertEqual(json_response['valid'], False)

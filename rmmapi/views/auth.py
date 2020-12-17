"""Authentication Module"""
import json
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.contrib.auth import authenticate, get_user_model
from django.http.response import HttpResponseBadRequest, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rmmapi.models import Rater

User = get_user_model()

@csrf_exempt
def login_user(request):
    """Handle the authentication of a Rater
    Method arguments:
        request -- The full HTTP request object
    """

    req_body = json.loads(request.body.decode())

    if request.method == 'POST':

        # Verify all required values are present
        required_fields = [ 'username', 'password' ]
        for field in required_fields:
            if not field in req_body:
                return HttpResponseBadRequest(json.dumps({ "message": f"Field `{field}` is required." }))

        # verify using the builtin authenticate method
        username = req_body['username']
        password = req_body['password']
        authenticated_user = authenticate(username=username, password=password)

        # If authentication successful, respond with the token
        if authenticated_user is not None:
            token = Token.objects.get(user=authenticated_user)
            data = json.dumps({ "valid": True, "token": token.key })
            return HttpResponse(data, content_type='application/json')

        # Credentials did not match existing user, cannot log user in
        else:
            data = json.dumps({ "valid": False })
            return HttpResponseBadRequest(data, content_type='application/json')

@csrf_exempt
def register_user(request):
    """Handle registration of a new User - will create a User and a Rater
    Method arguments:
        request -- The full HTTP request object
    """

    if request.method == "POST":
        # Get the POST body
        req_body = json.loads(request.body.decode())

        # Verify all required values are present
        required_fields = [ 'username', 'email', 'password', 'first_name', 'last_name', 'bio' ]
        for field in required_fields:
            if not field in req_body:
                return HttpResponseBadRequest(json.dumps({ "message": f"Field `{field}` is required." }))

        try:
            User.objects.get(username=req_body['username'])
            return HttpResponseBadRequest(json.dumps({ "message": "A user with that username already exists." }))
        except:
            pass

        try:
            User.objects.get(email=req_body['email'])
            return HttpResponseBadRequest(json.dumps({ "message": "A user with that email already exists." }))
        except:
            pass

        # Create a new User via the create_user helper method from Django's User model
        try:
            new_user = User.objects.create_user(
                username=req_body['username'],
                email=req_body['email'],
                password=req_body['password'],
                first_name=req_body['first_name'],
                last_name=req_body['last_name']
            )
        except ValidationError as ex:
            return HttpResponseServerError()

        # Create a new Rater to pair with this User
        rater = Rater.objects.create(
            bio=req_body['bio'],
            user=new_user
        )
        rater.save()

        # Generate a new token for the new user using REST framework's token generator
        token = Token.objects.create(user=new_user)

        # Return the token to the client
        data = json.dumps({ "token": token.key })
        return HttpResponse(data, content_type="application/json")

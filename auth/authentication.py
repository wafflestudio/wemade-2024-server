from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
import requests

class GoogleTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # No token provided

        access_token = auth_header.split(' ')[1]
        user_info = self.validate_google_token(access_token)

        if not user_info:
            raise AuthenticationFailed("Invalid or expired token")

        # Get or create user based on email
        email = user_info.get('email')
        user, created = User.objects.get_or_create(username=email, defaults={
            'email': email,
            'first_name': user_info.get('given_name', ''),
            'last_name': user_info.get('family_name', ''),
        })

        return (user, None)

    def validate_google_token(self, access_token):
        token_info_url = "https://oauth2.googleapis.com/tokeninfo"
        response = requests.get(token_info_url, params={"access_token": access_token})
        if response.status_code == 200:
            return response.json()  # Valid token
        return None  # Invalid token

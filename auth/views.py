from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
import requests
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from urllib.parse import urljoin
from django.conf import settings
from django.shortcuts import render
from django.views import View
from rest_framework.permissions import IsAuthenticated, AllowAny


class GoogleLogin(SocialLoginView):
    permission_classes = [AllowAny]
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client

class GoogleLoginCallback(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")

        if not code:
            return Response({"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange authorization code for access token
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
            "grant_type": "authorization_code",
        }

        response = requests.post(token_url, data=payload)

        if response.status_code != 200:
            return Response({"error": "Failed to fetch access token", "details": response.json()}, status=response.status_code)

        return Response(response.json(), status=status.HTTP_200_OK)

class LoginPage(View):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "login.html",
            {
                "google_callback_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
                "google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            },
        )

class ProtectedView(APIView):
    def get(self, request):
        return Response({"message": f"Hello, {request.user.email}!"})
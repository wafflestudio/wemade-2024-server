from allauth.core.internal.http import redirect
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from django.conf import settings
from django.views import View
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenBlacklistView

from person.models import Person, PersonalInfo


class GoogleLogin(SocialLoginView):
    permission_classes = [AllowAny]
    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_OAUTH_CALLBACK_URL
    client_class = OAuth2Client

from django.conf import settings
from oauth.models import OauthInfo
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests

class GoogleLoginCallback(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")

        if not code:
            return Response({"error": "Authorization code not provided"}, status=status.HTTP_400_BAD_REQUEST)

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_OAUTH_CALLBACK_URL,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=payload)
        if token_response.status_code != 200:
            return Response(
                {"error": "Failed to fetch access token", "details": token_response.json()},
                status=token_response.status_code,
            )

        tokens = token_response.json()
        google_access_token = tokens.get("access_token")

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {google_access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            return Response(
                {"error": "Failed to fetch user info", "details": userinfo_response.json()},
                status=userinfo_response.status_code,
            )

        userinfo = userinfo_response.json()
        email = userinfo.get("email")
        sub = userinfo.get("id")

        email_domains = ["@wemade.com", "@wemadeconnect.com", "@gmail.com", "@snu.ac.kr"]
        if not email or not any(email.endswith(domain) for domain in email_domains):
            return Response({"error": "Email not provided by Corporation"}, status=status.HTTP_400_BAD_REQUEST)

        personal_info = PersonalInfo.objects.filter(emails__contains=[email]).first()
        if not personal_info:
            return Response({"error": "Personal info not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            person = Person.objects.get(personal_info=personal_info)
        except Person.DoesNotExist:
            person = Person.objects.create(personal_info=personal_info, name=personal_info.name)

        try:
            user = OauthInfo.objects.get(oauth_id=sub)
        except OauthInfo.DoesNotExist:
            OauthInfo.objects.filter(email=email).delete()
            user = OauthInfo.objects.create(person=person, oauth_id=sub, oauth_email=email, oauth_provider="google")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response(
            {
                "access_token": access_token,
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


class LoginPage(View):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?redirect_uri={settings.GOOGLE_OAUTH_CALLBACK_URL}&prompt=consent&response_type=code&client_id={settings.GOOGLE_OAUTH_CLIENT_ID}&scope=openid%20email%20profile&access_type=offline")

class TestPage(View):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        return Response({"message": "You are authenticated!"}, status=status.HTTP_200_OK)

class TokenRefresh(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        refresh = RefreshToken(request.data.get("refresh_token"))
        access_token = str(refresh.access_token)
        return Response(
            {
                "access_token": access_token,
                "refresh_token": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

class TokenBlacklist(TokenBlacklistView):
    permission_classes = [IsAuthenticated]
    pass
from allauth.core.internal.http import redirect
from django.views import View
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenBlacklistView

from person.models import Person, PersonalInfo
from company.serializers import ActiveRoleSerializer

from django.conf import settings
from oauth.models import OauthInfo, EmailDomain
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests


class GoogleLoginCallback(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        profile = request.GET.get("profile")

        if not code:
            return Response(
                {"error": "Authorization code not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            redirect_uri = settings.GOOGLE_OAUTH_CALLBACK_URLS[profile]
        except KeyError:
            redirect_uri = settings.GOOGLE_OAUTH_CALLBACK_URL_BACKEND

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=payload)
        if token_response.status_code != 200:
            return Response(
                {
                    "error": "Failed to fetch access token",
                    "details": token_response.json(),
                },
                status=token_response.status_code,
            )

        tokens = token_response.json()
        google_access_token = tokens.get("access_token")

        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        headers = {"Authorization": f"Bearer {google_access_token}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)

        if userinfo_response.status_code != 200:
            return Response(
                {
                    "error": "Failed to fetch user info",
                    "details": userinfo_response.json(),
                },
                status=userinfo_response.status_code,
            )

        userinfo = userinfo_response.json()
        email = userinfo.get("email")
        sub = userinfo.get("id")

        # @gmail.com and @snu.ac.kr are allowed for testing
        email_domains = ["@wemade.com", "@gmail.com", "@snu.ac.kr"] + list(
            EmailDomain.objects.values_list("domain", flat=True)
        )
        if not email or not any(email.endswith(domain) for domain in email_domains):
            return Response(
                {"error": "Email not provided by Corporation"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = OauthInfo.objects.get(username=sub)
            person = user.person
        except OauthInfo.DoesNotExist:
            personal_info = PersonalInfo.objects.filter(
                emails__contains=[email]
            ).first()
            if not personal_info:
                return Response(
                    {"error": "Personal info not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )
            try:
                person = Person.objects.get(personal_info=personal_info)
            except Person.DoesNotExist:
                person = Person.objects.create(
                    personal_info=personal_info,
                    name=personal_info.name,
                )
            OauthInfo.objects.filter(email=email).delete()
            user = OauthInfo.objects.create(
                person=person, username=sub, email=email, oauth_provider="google"
            )

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        roles_serialized = ActiveRoleSerializer(
            person.roles.filter(end_date__isnull=True), many=True
        ).data

        return Response(
            {
                "access_token": access_token,
                "refresh_token": str(refresh),
                "roles": roles_serialized,
                "p_id": person.p_id,
            },
            status=status.HTTP_200_OK,
        )


class TestPage(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "You are authenticated!: " + request.user.person.name},
            status=status.HTTP_200_OK,
        )


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


class LoginPage(View):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return redirect(
            f"https://accounts.google.com/o/oauth2/v2/auth?redirect_uri={settings.GOOGLE_OAUTH_CALLBACK_URL_BACKEND}&prompt=consent&response_type=code&client_id={settings.GOOGLE_OAUTH_CLIENT_ID}&scope=openid%20email%20profile&access_type=offline"
        )

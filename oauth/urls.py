from django.urls import include, path, re_path
from oauth.views import GoogleLoginCallback, TestPage, LoginPage

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    re_path("accounts/", include("allauth.urls")),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("google/callback/",GoogleLoginCallback.as_view(),name="google_login_callback"),
    path("test/", TestPage.as_view(), name="test"),
    path("loginpage", LoginPage.as_view(), name="login_page"),
]
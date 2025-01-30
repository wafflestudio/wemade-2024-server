from django.urls import include, path, re_path
from oauth.views import GoogleLogin, LoginPage, GoogleLoginCallback, TestPage

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    re_path("accounts/", include("allauth.urls")),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("google/callback/",GoogleLoginCallback.as_view(),name="google_login_callback"),
    path("test/", TestPage.as_view(), name="test"),
]
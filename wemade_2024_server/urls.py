"""
URL configuration for wemade_2024_server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os

from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Wemade 2024 API",
        default_version="v1",
        description="",
        terms_of_service="",
        contact=openapi.Contact(email="dlacksdud2@gmail.com"),
        license=openapi.License(name=""),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    url=os.getenv("DEPLOY_URL"),
)
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("oauth.urls")),
    path("api/v1/company/", include("company.urls")),
    path("api/v1/personCard/", include("personCard.urls")),
    path("api/v1/files/", include("files.urls")),
    path("api/v1/master/", include("master.urls")),
    path("api/v1/search/", include("search.urls")),
    # swagger 설정
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
]

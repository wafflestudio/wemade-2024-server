from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    # 쿼리로 team/corp/person 종류 및 검색어 받아 검색
    path('search/', SearchListAPIView.as_view(), name='search s'),
]

from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    # 쿼리로 team/corp/person 종류 및 검색어 받아 검색
    # path('search/', SearchListAPIView.as_view(), name='search'),

    # Person의 소속 법인/최하위 팀, 자격증으로 검색
    path('search/person/', PersonSearchAPIView.as_view(), name='search-person'),

    # Team 이름으로 Team 검색
    path('search/team/', TeamSearchAPIView.as_view(), name='search-team'),

    # Coporation 이름으로 Corp 검색
    path('search/corp/', CorpSearchAPIView.as_view(), name='search-corp'),

    # 법인/팀 검색 시, 하위 조직에 속한 사람들을 검색
    path('search/team-members/', TeamSubMembersSearchAPIView.as_view(), name='search-team-members'),
]

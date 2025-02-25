from django.urls import path
from .views import *

urlpatterns = [
    # Person의 소속 법인/최하위 팀, 자격증으로 검색
    path("person/", PersonSearchAPIView.as_view(), name="search-person"),
    # Team 이름으로 Team 검색
    path("team/", TeamSearchAPIView.as_view(), name="search-team"),
    # Coporation 이름으로 Corp 검색
    path("corp/", CorpSearchAPIView.as_view(), name="search-corp"),
]

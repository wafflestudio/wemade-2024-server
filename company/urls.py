from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    # Corporation
    # 새로운 Corporation 생성
    path('corp/create/', CorpCreateAPIView.as_view(), name='corp-create'),
    # 모든 Corporation List
    path('corp/list/', CorpListAPIView.as_view(), name='corp-list'),
    # Corporation 정보 업데이트 (Master)
    path('corp/<int:c_id>/update/', CorpUpdateDeleteAPIView.as_view(), name='corp-update'),
    # Corporation 정보 삭제 (Master)
    path('corp/<int:c_id>/delete/', CorpUpdateDeleteAPIView.as_view(), name='corp-delete'),
    # 특정 Corporation의 정보 조회
    path('corp/<int:c_id>/', CorpDetailAPIView.as_view(), name='corp-detail'),

    # Team
    # 새로운 Team 생성
    path('team/create/', TeamCreateAPIView.as_view(), name='team-create'),
    # 모든 Team List
    path('team/list/', TeamListAPIView.as_view(), name='team-list'),
    # Team 정보 업데이트 (Master/HR Team)
    path('team/<int:t_id>/update/', TeamUpdateDeleteAPIView.as_view(), name='team-update'),
    # Team 정보 삭제 (Master/HR Team)
    path('team/<int:t_id>/delete/', TeamUpdateDeleteAPIView.as_view(), name='team-delete'),
    # 특정 Team의 정보 조회
    path('team/<int:t_id>/', TeamDetailAPIView.as_view(), name='team-detail'),
]

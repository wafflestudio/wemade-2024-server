from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    # Edit mode
    path('edit/', EditListAPIView.as_view(), name='edit-list'),
    # Subteam들 정보 불러오기
    path('edit/team/<int:t_id>/'),
    # Corporation 정보 업데이트 - 조직 이동/비활성화 (Master)
    path('edit/corp/<int:c_id>/update/', CorpEditUpdateAPIView.as_view(), name='corp-update'),
    # Team 정보 업데이트 - 조직 이동/비활성화 (Master/HR Team)
    path('edit/team/<int:t_id>/update/', TeamEditUpdateAPIView.as_view(), name='team-update'),
    # Corporation 정보 삭제 (Master)
    # path('edit/corp/<int:c_id>/delete/', CorpDeleteAPIView.as_view(), name='corp-delete'),
    # Team 정보 삭제 (Master/HR Team)
    # path('edit/team/<int:t_id>/delete/', TeamDeleteAPIView.as_view(), name='team-delete'),

    # Corporation
    # 새로운 Corporation 생성
    path('corp/create/', CorpCreateAPIView.as_view(), name='corp-create'),
    # 모든 Corporation List
    path('corp/list/', CorpListAPIView.as_view(), name='corp-list'),
    # 특정 Corporation의 정보 조회
    path('corp/<int:c_id>/', CorpDetailAPIView.as_view(), name='corp-detail'),

    # Team
    # 새로운 Team 생성
    path('team/create/', TeamCreateAPIView.as_view(), name='team-create'),
    # 모든 Team List
    path('team/list/', TeamListAPIView.as_view(), name='team-list'),
    # 특정 Team의 정보 조회
    path('team/<int:t_id>/', TeamDetailAPIView.as_view(), name='team-detail'),
]

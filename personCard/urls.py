from django.contrib import admin
from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    # 검색 페이지 우측 특정한 사람 공개 정보 불러오기
    path('list/<int:p_id>/', PersonCardListDetailAPIView.as_view(), name='person-card-list-detail'),
    # 검색 페이지에서 모든 사람 정보 불러오기
    path('list/', PersonCardListAPIView.as_view(), name='person-card-list'),
    # 사람 이름을 query로 받아 검색하기
    path('search/',  PersonCardSearchListAPIView.as_view(), name='person-card-search'),

    # 개인정보 업데이트 (본인/Master/HR Team)
    path('<int:p_id>/info/update/', PersonalInfoUpdateAPIView.as_view(), name='personal-info-update'),
    # 직무 업데이트  + 직무 히스토리 생성 (Master/HR Team)
    path('<int:p_id/roles/update/>', PersonRolesUpdateAPIView.as_view(), name='person-roles-update'),
    # 인사카드 조회
    path('<int:p_id>/', PersonCardDetailAPIView.as_view(), name='person-card-detail'),

    # 직무 히스토리 정보 불러오기 (본인/팀장/Master/HR Team)
    path('<int:p_id>/history/list/', PersonalHistoryListAPIView.as_view(), name='personal-history-list'),
    # 직무 히스토리 내 직무 설명(job description) 수정하기 (본인/Master/HR Team)
    path('<int:p_id>/history/update/', PersonalHistoryUpdateAPIView.as_view(), name='personal-history-update'),

    # 직무 히스토리 삭제하기 (Master/HR Team)
    path('<int:p_id>/history/delete', PersonalHistoryDeleteAPIView.as_view(), name='personal-history-delete'),
]
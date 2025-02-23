from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from rest_condition import Or

from .models import Corporation, Team
from .serializers import *
from .paginations import *
from .permissions import *


# --------- 조직도 관련 Views ------------
class EditListAPIView(ListAPIView):
    serializer_class = CorpDetailSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    def get_queryset(self):
        user_person = self.request.user.person
        # 만약 요청 사용자가 MasterHRTeam이면 모든 법인을, 아니라면 자신이 HR팀 구성원인 법인 반환
        if IsMasterHRTeam().has_permission(self.request, self):
            qs = Corporation.objects.all().order_by('name')
        else:
            qs = Corporation.objects.filter(hr_team__members=user_person).order_by(('name'))
        return qs


# Edit mode Team List
class TeamEditListAPIView(ListAPIView):
    serializer_class = TeamEditListSerializer
    queryset = Team.objects.all().order_by('name')
    lookup_field = 't_id'
    lookup_url_kwarg = 't_id'
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# Corporation 정보 업데이트/삭제 (Master)
class CorpEditUpdateDeleteAPIView(RetrieveUpdateAPIView):
    serializer_class = CorpEditUpdateSerializer
    queryset = Corporation.objects.all()
    lookup_field = 'c_id'
    lookup_url_kwarg = 'c_id'
    permission_classes = [IsMasterHRTeam]


# Team 정보 업데이트/삭제 (Master/HR Team)
class TeamEditUpdateDeleteAPIView(RetrieveUpdateAPIView):
    serializer_class = TeamEditUpdateSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'
    lookup_url_kwarg = 't_id'
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# --------- 인사 이동 관련 Views ------------
#

# --------- 추가 기능 Views ------------

# --- Corporation Views ---
# 새로운 Corporation 생성
class CorpCreateAPIView(CreateAPIView):
    serializer_class = CorpCreateSerializer
    permission_class = [IsMasterHRTeam]


# 모든 Corporation List
class CorpListAPIView(ListAPIView):
    serializer_class = CorpListSerializer
    #pagination_class = CorpListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Corporation.objects.filter(name__icontains=name)
        return Corporation.objects.all()


# 특정 Corporation의 정보 조회
class CorpDetailAPIView(RetrieveAPIView):
    serializer_class = CorpDetailSerializer
    queryset = Corporation.objects.all()
    lookup_field = 'c_id'
    lookup_url_kwarg = 'c_id'
    permission_classes = [AllowAny]


# --- Team Views ---
# 새로운 Team 생성
class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# 모든 Team List
class TeamListAPIView(ListAPIView):
    serializer_class = TeamListSerializer
    #pagination_class = TeamListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Team.objects.filter(name__icontains=name)
        return Team.objects.all()

# 특정 Team의 정보 조회
class TeamDetailAPIView(RetrieveAPIView):
    serializer_class = TeamDetailSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'
    lookup_url_kwarg = 't_id'
    permission_classes = [AllowAny]

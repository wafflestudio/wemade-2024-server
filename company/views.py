from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models import Corporation, Team
from .serializers import *
from .paginations import *
from .permissions import *


# --- Corporation Views ---

# 새로운 Corporation 생성
class CorpCreateAPIView(CreateAPIView):
    serializer_class = CorpCreateSerializer
    permission_class = [IsMasterHRTeam]


# 모든 Corporation List
class CorpListAPIView(ListAPIView):
    serializer_class = CorpListSerializer
    pagination_class = CorpListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Corporation.objects.filter(name__icontains=name)
        return Corporation.objects.all()


# Corporation 정보 업데이트/삭제 (Master)
class CorpUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CorpUpdateDeleteSerializer
    queryset = Corporation.objects.all()
    lookup_field = 'c_id'
    lookup_url_kwarg = 'c_id'
    permission_classes = [IsMasterHRTeam]


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
    permission_classes = [OR(IsMasterHRTeam, IsHRTeam)]


# 모든 Team List
class TeamListAPIView(ListAPIView):
    serializer_class = TeamListSerializer
    pagination_class = TeamListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Team.objects.filter(name__icontains=name)
        return Team.objects.all()


# Team 정보 업데이트/삭제 (Master/HR Team)
class TeamUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamUpdateDeleteSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'
    lookup_url_kwarg = 't_id'
    permission_classes = [OR(IsMasterHRTeam, IsHRTeam)]

# 특정 Team의 정보 조회
class TeamDetailAPIView(RetrieveAPIView):
    serializer_class = TeamDetailSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'
    lookup_url_kwarg = 't_id'
    permission_classes = [AllowAny]

# views.py
from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView, CreateAPIView, RetrieveAPIView,
    RetrieveUpdateDestroyAPIView
)
from rest_framework.response import Response
from rest_framework import status
from .models import Corporation, Team
from .serializers import (
    CorpListSerializer, CorpDetailSerializer, CorpCreateSerializer,
    CorpUpdateDeleteSerializer, TeamListSerializer, TeamDetailSerializer,
    TeamCreateSerializer, TeamUpdateDeleteSerializer
)
from .paginations import CorpListPagination, TeamListPagination

# --- Corporation Views ---

class CorpListAPIView(ListAPIView):
    serializer_class = CorpListSerializer
    pagination_class = CorpListPagination

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Corporation.objects.filter(name__icontains=name)
        return Corporation.objects.all()


class CorpDetailAPIView(RetrieveAPIView):
    serializer_class = CorpDetailSerializer
    queryset = Corporation.objects.all()
    lookup_field = 'c_id'
    lookup_url_kwarg = 'c_id'


class CorpCreateAPIView(CreateAPIView):
    serializer_class = CorpCreateSerializer


class CorpUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CorpUpdateDeleteSerializer
    queryset = Corporation.objects.all()
    lookup_field = 'c_id'
    lookup_url_kwarg = 'c_id'


# --- Team Views ---

class TeamListAPIView(ListAPIView):
    serializer_class = TeamListSerializer
    pagination_class = TeamListPagination

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if name:
            return Team.objects.filter(name__icontains=name)
        return Team.objects.all()


class TeamDetailAPIView(RetrieveAPIView):
    serializer_class = TeamDetailSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'
    lookup_url_kwarg = 't_id'


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer


class TeamUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamUpdateDeleteSerializer
    queryset = Team.objects.all()
    lookup_field = 't_id'
    lookup_url_kwarg = 't_id'

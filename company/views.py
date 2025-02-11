from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, CreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from .serializers import *
from .paginations import *
from rest_framework import status


# Corporation
class CorpListAPIView(ListAPIView):
    serializer_class = CorpListSerializer
    pagination_class = CorpListPagination

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if not name:
            return Corporation.objects.all()
        return Corporation.objects.filter(name__icontains=name)


class CorpDetailAPIView(RetrieveAPIView):
    serializer_class = CorpDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        corporation = get_object_or_404(Corporation, c_id=kwargs.get('c_id'))  # ✅ `p_id` → `c_id`
        return Response(self.get_serializer(corporation).data, status=200)


class CorpCreateAPIView(CreateAPIView):
    serializer_class = CorpCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CorpUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = CorpUpdateDeleteSerializer

    def retrieve(self, request, *args, **kwargs):
        corporation = get_object_or_404(Corporation, p_id=kwargs.get('c_id'))
        return Response(self.get_serializer(corporation).data, status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


# Team
class TeamListAPIView(ListAPIView):
    serializer_class = TeamListSerializer
    pagination_class = TeamListPagination

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if not name:
            return Team.objects.all()
        return Team.objects.filter(name__icontains=name)


class TeamDetailAPIView(RetrieveAPIView):
    serializer_class = TeamDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        team = get_object_or_404(Team, t_id=kwargs.get('t_id'))
        return Response(self.get_serializer(team).data, status=200)


class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TeamUpdateDeleteAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TeamUpdateDeleteSerializer

    def retrieve(self, request, *args, **kwargs):
        team = get_object_or_404(Team, p_id=kwargs.get('t_id'))
        return Response(self.get_serializer(team).data, status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)

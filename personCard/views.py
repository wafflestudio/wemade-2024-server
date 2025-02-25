from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from rest_condition import Or

from person.models import Person, PersonalInfo
from company.models import Role
from .serializers import *
from .paginations import *
from .permissions import *


# 검색 페이지에서 모든 사람 정보 불러오기
class PersonCardListAPIView(ListAPIView):
    serializer_class = PersonCardListSerializer
    pagination_class = PersonCardListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if not name:
            return Person.objects.all()
        return Person.objects.filter(name__icontains=name)


# 검색 페이지 우측 특정한 사람 공개 정보 불러오기
class PersonCardListDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardListDetailSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get("p_id"))
        return Response(self.get_serializer(person).data, status=200)


# 인사카드 조회
class PersonCardDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardDetailSerializer
    permission_classes = [Or(IsMasterHRTeam, IsOwnerOrHRTeamOrTeamLeader)]

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get("p_id"))
        self.check_object_permissions(request, person)
        return Response(self.get_serializer(person).data, status=200)


# 개인정보 업데이트
class PersonalInfoUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoUpdateSerializer
    lookup_field = "person__p_id"
    lookup_url_kwarg = "p_id"
    permission_classes = [Or(IsMasterHRTeam, IsOwnerOrHRTeam)]


# 직무 히스토리 정보 불러오기
class RoleHistoryListAPIView(ListAPIView):
    serializer_class = RoleHistorySerializer
    permission_classes = [Or(IsMasterHRTeam, IsOwnerOrHRTeamOrTeamLeader)]

    def get_queryset(self):
        p_id = self.kwargs.get("p_id")
        person = get_object_or_404(Person, p_id=p_id)
        self.check_object_permissions(self.request, person)
        return Role.objects.filter(person=person).order_by("-start_date")


# 직무 히스토리 내 직무 설명(job description) 수정하기
class RoleHistoryUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = RoleHistoryUpdateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsOwnerOrHRTeam)]

    def get_object(self):
        p_id = self.kwargs.get("p_id")
        person = get_object_or_404(Person, p_id=p_id)
        self.check_object_permissions(self.request, person)

        # role_id는 요청 데이터나 쿼리 파라미터에서 전달
        role_id = self.request.data.get("role_id") or self.request.query_params.get(
            "role_id"
        )
        if not role_id:
            raise NotFound("role_id가 제공되지 않았습니다.")

        obj = get_object_or_404(Role, r_id=role_id, person=person)
        return obj

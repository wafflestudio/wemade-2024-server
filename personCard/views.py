from django.shortcuts import get_object_or_404
from company.permissions import *
from company.models import *
from django.core.exceptions import PermissionDenied

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

from company.permissions import IsMasterHRTeam
from person.models import PersonalInfo
from drf_yasg.utils import swagger_auto_schema
from .models import *
from .serializers import *
from .paginations import *
from .permissions import IsOwnerOrHRTeam, IsOwnerOrHRTeamOrTeamLeader


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
@swagger_auto_schema(
    operation_description="검색 페이지 우측 특정한 사람 공개 정보 불러오기"
)
class PersonCardListDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardListDetailSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get("p_id"))
        return Response(self.get_serializer(person).data, status=200)


# 인사카드 조회
@swagger_auto_schema(
    operation_description="인사카드 조회"
)
class PersonCardDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardDetailSerializer
    permission_classes = [Or(IsMasterHRTeam, IsOwnerOrHRTeamOrTeamLeader)]

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get("p_id"))
        self.check_object_permissions(request, person)
        return Response(self.get_serializer(person).data, status=200)


# 개인정보 업데이트
@swagger_auto_schema(
    operation_description="개인정보 업데이트"
)
class PersonalInfoUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoUpdateSerializer
    lookup_field = "person__p_id"
    lookup_url_kwarg = "p_id"
    permission_classes = [Or(IsMasterHRTeam, IsOwnerOrHRTeam)]


# 개인정보 수정 요청 list
@swagger_auto_schema(
    operation_description="개인정보 수정 요청 list"
)
class PersonCardChangeListAPIView(ListAPIView):
    serializer_class = PersonCardChangeListSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    def get_queryset(self):
        user_person = self.request.user.person
        c_id = self.kwargs.get("c_id")

        # MasterHRTeam은 모든 요청을 볼 수 있음
        if IsMasterHRTeam().has_permission(self.request, self):
            if c_id:
                return (
                    PersonCardChangeRequest.objects.filter(
                        person__member_of_teams__corporation__c_id=c_id
                    )
                    .distinct()
                    .order_by("requested_at")
                )
            return PersonCardChangeRequest.objects.all().order_by("requested_at")

        # HR팀원이라면 해당 법인의 HR팀에 속해야 함
        try:
            corp = Corporation.objects.get(c_id=c_id)
        except Corporation.DoesNotExist:
            raise PermissionDenied("해당 Corporation이 존재하지 않습니다.")

        if user_person not in corp.hr_team.members.all():
            raise PermissionDenied("해당 법인의 HR팀원만 접근할 수 있습니다.")

        return (
            PersonCardChangeRequest.objects.filter(
                person__member_of_teams__corporation=corp
            )
            .distinct()
            .order_by("requested_at")
        )


# 개인정보 수정 허가
@swagger_auto_schema(
    operation_description="개인정보 수정 허가"
)
class PersonCardChangeReviewAPIView(RetrieveUpdateAPIView):
    serializer_class = PersonCardChangeRequestReviewSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]
    lookup_field = "id"
    lookup_url_kwarg = "request_id"

    def get_queryset(self):
        qs = PersonCardChangeRequest.objects.filter(status="pending")
        user_person = self.request.user.person

        # 만약 사용자가 MasterHRTeam이 아니라면, 자신이 관리하는 직원들의 요청만 필터링
        if not IsMasterHRTeam().has_permission(self.request, self):
            # 사용자가 속한 HR팀에 해당하는 법인의 구성원만 조회
            qs = qs.filter(
                person__member_of_teams__corporation__hr_team__members=user_person
            )
        return qs.distinct().order_by("requested_at")


# 직무 히스토리 정보 불러오기
@swagger_auto_schema(
    operation_description="직무 히스토리 정보 불러오기"
)
class RoleHistoryListAPIView(ListAPIView):
    serializer_class = RoleHistorySerializer
    permission_classes = [Or(IsMasterHRTeam, IsOwnerOrHRTeamOrTeamLeader)]

    def get_queryset(self):
        p_id = self.kwargs.get("p_id")
        person = get_object_or_404(Person, p_id=p_id)
        self.check_object_permissions(self.request, person)
        return Role.objects.filter(person=person).order_by("-start_date")


# 직무 히스토리 내 직무 설명(job description) 수정하기
@swagger_auto_schema(
    operation_description="직무 히스토리 내 직무 설명(job description) 수정하기"
)
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


@swagger_auto_schema(
    operation_description="인사카드 컬럼 정보 불러오기"
)
class CardColumnsAPIView(ListAPIView):
    serializer_class = CardColumnSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return PersonCardColumns.objects.all()
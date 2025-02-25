from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import AllowAny

from rest_condition import Or
from rest_framework.response import Response

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
            qs = Corporation.objects.all().order_by("name")
        else:
            qs = Corporation.objects.filter(hr_team__members=user_person).order_by(
                ("name")
            )
        return qs


# Edit mode Team List
class TeamEditListAPIView(ListAPIView):
    serializer_class = TeamEditListSerializer
    queryset = Team.objects.all().order_by("name")
    lookup_field = "t_id"
    lookup_url_kwarg = "t_id"
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# Corporation 정보 업데이트/삭제 (Master)
class CorpEditUpdateDeleteAPIView(RetrieveUpdateAPIView):
    serializer_class = CorpEditUpdateSerializer
    queryset = Corporation.objects.all()
    lookup_field = "c_id"
    lookup_url_kwarg = "c_id"
    permission_classes = [IsMasterHRTeam]


# Team 정보 업데이트/삭제 (Master/HR Team)
class TeamEditUpdateDeleteAPIView(RetrieveUpdateAPIView):
    serializer_class = TeamEditUpdateSerializer
    queryset = Team.objects.all()
    lookup_field = "t_id"
    lookup_url_kwarg = "t_id"
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# --------- 인사 이동 관련 Views ------------
# 특정한 사람의 role 생성 (부서 이동/발령)
class RoleCreateAPIView(CreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleCreateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# 특정한 사람의 role 변경 (직급 변경)
class RoleUpdateAPIView(RetrieveUpdateAPIView):
    lookup_field = "r_id"
    lookup_url_kwarg = "r_id"
    queryset = Role.objects.all()
    serializer_class = RoleUpdateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

class RoleListDetailAPIView(ListAPIView):
    serializer_class = RoleDetailSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]
    lookup_field = 'person_id'
    lookup_url_kwarg = 'p_id'

    def get_queryset(self):
        person_id = self.kwargs.get(self.lookup_url_kwarg)
        return Role.objects.filter(person_id=person_id, end_date__isnull=True)

# # 직무 업데이트 (HR Team) + 직무 히스토리 생성
# class PersonRolesUpdateAPIView(RetrieveUpdateAPIView):
#     queryset = Person.objects.all()
#     serializer_class = PersonRolesUpdateSerializer
#     lookup_field = 'p_id'  # URL에서 p_id를 사용해 Person을 조회
#     permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# --------- 추가 기능 Views ------------


# --- Corporation Views ---
# 새로운 Corporation 생성
class CorpCreateAPIView(CreateAPIView):
    serializer_class = CorpCreateSerializer
    permission_classes = [IsMasterHRTeam]


# 모든 Corporation List
class CorpListAPIView(ListAPIView):
    serializer_class = CorpListSerializer
    # pagination_class = CorpListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if name:
            return Corporation.objects.filter(name__icontains=name)
        return Corporation.objects.all()


# 특정 Corporation의 정보 조회
class CorpDetailAPIView(RetrieveAPIView):
    serializer_class = CorpDetailSerializer
    queryset = Corporation.objects.all()
    lookup_field = "c_id"
    lookup_url_kwarg = "c_id"
    permission_classes = [AllowAny]


class CorpDeleteAPIView(RetrieveDestroyAPIView):
    serializer_class = CorpDetailSerializer
    queryset = Corporation.objects.all()
    lookup_field = "c_id"
    lookup_url_kwarg = "c_id"
    permission_classes = [IsMasterHRTeam]

    def perform_destroy(self, instance):
        """
        1) instance.is_active = False, deleted_at=now() → Corporation 소프트 딜리트
        2) 해당 Corporation에 속한 모든 Team(과 하위 조직)도 Deactivate
        3) 그 팀들에 연결된 Role 모두 end_date 처리
        """
        if instance.is_active:
            instance.is_active = False
            if not instance.deleted_at:
                instance.deleted_at = timezone.now()
            instance.save()

            # 2) 해당 법인에 속한 모든 팀(직접 + 하위 조직까지)을 찾아서 비활성화
            teams = instance.teams.all()
            for team in teams:
                self.deactivate_team_recursive(team)

        else:
            # 이미 비활성 상태라면 실제 삭제
            instance.delete()

    def deactivate_team_recursive(self, team_obj):
        """
        팀을 비활성화(is_active=False, deleted_at=now)하고,
        연결된 Role들도 end_date 처리, 그리고 재귀적으로 하위 팀들도 비활성화
        """
        if team_obj.is_active:
            team_obj.is_active = False
            if not team_obj.deleted_at:
                team_obj.deleted_at = timezone.now()
            team_obj.save()
            # 연결된 Role end_date 처리
            for role in team_obj.roles.filter(end_date__isnull=True):
                role.end_date = timezone.now()
                role.save()

        # team_obj 하위 조직(역참조 lower_teams)을 재귀적으로 비활성화
        for child_team in team_obj.lower_teams.all():
            if child_team.is_active:
                self.deactivate_team_recursive(child_team)


# --- Team Views ---
# 새로운 Team 생성
class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# 모든 Team List
class TeamListAPIView(ListAPIView):
    serializer_class = TeamListSerializer
    # pagination_class = TeamListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get("name")
        if name:
            return Team.objects.filter(name__icontains=name)
        return Team.objects.all()


# 특정 Team의 정보 조회
class TeamDetailAPIView(RetrieveAPIView):
    serializer_class = TeamDetailSerializer
    queryset = Team.objects.all()
    lookup_field = "t_id"
    lookup_url_kwarg = "t_id"
    permission_classes = [AllowAny]


class TeamDeleteAPIView(RetrieveDestroyAPIView):
    serializer_class = TeamDetailSerializer
    queryset = Team.objects.all()
    lookup_field = "t_id"
    lookup_url_kwarg = "t_id"
    permission_classes = [IsMasterHRTeam]

    def perform_destroy(self, instance):
        """
        1) instance.is_active = False, deleted_at=now() → Team 소프트 딜리트
        2) 해당 팀의 하위 조직도 비활성화
        3) 해당 팀의 Role들도 end_date 처리
        """
        if instance.is_active:
            instance.is_active = False
            if not instance.deleted_at:
                instance.deleted_at = timezone.now()
            instance.save()

            # 해당 팀에 연결된 진행중인 Role end_date 처리
            for role in instance.roles.filter(end_date__isnull=True):
                role.end_date = timezone.now()
                role.save()

            # 하위 팀도 재귀적으로 비활성화
            self.deactivate_subteams_recursive(instance)
        else:
            # 이미 비활성 상태라면 실제 삭제
            instance.delete()

    def deactivate_subteams_recursive(self, team_obj):
        """
        하위 팀들을 재귀적으로 비활성화 + 해당 Role end_date 처리
        """
        for child_team in team_obj.lower_teams.all():
            if child_team.is_active:
                child_team.is_active = False
                if not child_team.deleted_at:
                    child_team.deleted_at = timezone.now()
                child_team.save()
                # child_team.roles 진행중인 것 end_date 처리
                for role in child_team.roles.filter(end_date__isnull=True):
                    role.end_date = timezone.now()
                    role.save()
                # 재귀적으로 더 하위가 있으면 비활성화
                self.deactivate_subteams_recursive(child_team)


# ----- Role Views -----
class RoleDeleteAPIView(RetrieveDestroyAPIView):
    serializer_class = RoleDetailSerializer
    queryset = Role.objects.all()
    lookup_field = "r_id"
    lookup_url_kwarg = "r_id"
    permission_classes = [IsMasterHRTeam]

    def perform_destroy(self, instance):
        # 소프트 딜리트: is_active를 False로 변경하고, deleted_at을 기록
        if not instance.end_date:
            instance.end_date = timezone.now()
            instance.save()
        else:
            # 이미 delete 상태라면 실제 삭제?
            # instance.delete()
            # 실제 삭제는 안해야할듯
            pass
        print(instance.end_date)


# --- Commit Views ---

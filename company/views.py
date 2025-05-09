from copy import deepcopy

from django.db.models import OuterRef, Subquery
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models.aggregates import Max
from rest_framework import status
from django.db.models import Q
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    RetrieveDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import AllowAny

from rest_condition import Or
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Corporation, Team
from .serializers import *
from .paginations import *
from .permissions import *


# --------- 조직도 관련 Views ------------
class EditListAPIView(ListAPIView):
    serializer_class = CorpDetailSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    @swagger_auto_schema(
        operation_summary="Edit mode Corporation List",
        operation_description="List of Corporations for editing mode",
    )
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
@swagger_auto_schema(
    operation_summary="Edit mode Team List",
)
class TeamEditListAPIView(ListAPIView):
    serializer_class = TeamEditListSerializer
    queryset = Team.objects.all().order_by("name")
    lookup_field = "t_id"
    lookup_url_kwarg = "t_id"
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# 임시저장
@swagger_auto_schema(
    operation_summary="조직도 임시저장",
)
class EditDraftAPIView(ListCreateAPIView):
    serializer_class = EditDraftSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    def get_queryset(self):
        user_person = self.request.user.person
        return Draft.objects.filter(created_by=user_person).order_by("created_at")


# 임시저장 삭제
@swagger_auto_schema(
    operation_summary="조직도 임시저장 삭제",
)
class EditDraftDeleteAPIView(RetrieveDestroyAPIView):
    serializer_class = EditDraftSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]
    lookup_field = "id"
    lookup_url_kwarg = "d_id"

    def get_queryset(self):
        user_person = self.request.user.person
        return Draft.objects.filter(created_by=user_person).order_by("created_at")


# Corporation 정보 업데이트 (Master)
@swagger_auto_schema(
    operation_summary="Corporation 정보 업데이트 - 조직 이동/비활성화 (Master)",
)
class CorpUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = CorpEditUpdateSerializer
    queryset = Corporation.objects.all()
    lookup_field = "c_id"
    lookup_url_kwarg = "c_id"
    permission_classes = [IsMasterHRTeam]

    def perform_update(self, serializer):
        new_commit = self.request.data.get("new_commit", False)
        if new_commit:
            CompanyCommit.objects.create(created_by=self.request.user.person)
        else:
            commit = CompanyCommit.objects.latest("created_at")

        instance = serializer.save()
        if "name" in serializer.validated_data:
            CorporationNameHistoryInfo.objects.create(
                corporation=instance, name=instance.name, commit=commit
            )
            commit.actions.add(
                CompanyCommitAction.objects.create(
                    commit=commit,
                    target_type="CORPORATION",
                    action="UPDATE",
                    target_id=instance.c_id,
                    new_name=instance.name,
                )
            )


# Team 정보 업데이트 (Master/HR Team)
@swagger_auto_schema(
    operation_summary="Team 정보 업데이트(1) - 조직 이동/비활성화 (Master/HR Team)",
)
class TeamUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = TeamEditUpdateSerializer
    queryset = Team.objects.all()
    lookup_field = "t_id"
    lookup_url_kwarg = "t_id"
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_name = old_instance.name
        old_parent = old_instance.parent_teams.first()
        new_commit = self.request.data.get("new_commit", False)
        if new_commit:
            commit = CompanyCommit.objects.create(created_by=self.request.user.person)
        else:
            commit = CompanyCommit.objects.latest("created_at")

        instance = serializer.save()
        if "name" in serializer.validated_data:
            TeamNameHistoryInfo.objects.create(
                team=instance, name=instance.name, commit=commit
            )
            commit.actions.add(
                CompanyCommitAction.objects.create(
                    commit=commit,
                    target_type="TEAM",
                    action="UPDATE",
                    target_id=instance.t_id,
                    old_name=old_name,
                    new_name=instance.name,
                )
            )
        if "parent_teams" in serializer.validated_data:
            TeamParentHistoryInfo.objects.create(
                team=instance, parent_team=instance.parent_teams.first(), commit=commit
            )
            commit.actions.add(
                CompanyCommitAction.objects.create(
                    commit=commit,
                    target_type="TEAM",
                    action="UPDATE",
                    target_id=instance.t_id,
                    old_parent_id=old_parent.t_id if old_parent else None,
                    new_parent_id=instance.parent_teams.first().t_id
                    if instance.parent_teams.first()
                    else None,
                )
            )


# --------- 인사 이동 관련 Views ------------
# 특정한 사람의 role 생성 (부서 이동/발령)
@swagger_auto_schema(
    operation_summary="특정한 사람의 role 생성 (부서 이동/발령)",
)
class RoleCreateAPIView(CreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleCreateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


# 특정한 사람의 role 변경 (직급 변경)
@swagger_auto_schema(
    operation_summary="특정한 사람의 role 변경 (직급 변경)",
)
class RoleUpdateAPIView(RetrieveUpdateAPIView):
    lookup_field = "r_id"
    lookup_url_kwarg = "r_id"
    queryset = Role.objects.all()
    serializer_class = RoleUpdateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]


@swagger_auto_schema(
    operation_summary="특정한 사람의 role 조회 (supervisor 변경 포함)",
)
class RoleListDetailAPIView(ListAPIView):
    serializer_class = RoleDetailSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]
    lookup_field = "person_id"
    lookup_url_kwarg = "p_id"

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
@swagger_auto_schema(
    operation_summary="새로운 Corporation 생성",
)
class CorpCreateAPIView(CreateAPIView):
    serializer_class = CorpCreateSerializer
    permission_classes = [IsMasterHRTeam]

    def perform_create(self, serializer):
        new_commit = self.request.data.get("new_commit", False)
        if new_commit:
            commit = CompanyCommit.objects.create(created_by=self.request.user.person)
        else:
            commit = CompanyCommit.objects.latest("created_at")

        corporation = serializer.save()
        CorporationNameHistoryInfo.objects.create(
            corporation=corporation, name=corporation.name, commit=commit
        )
        commit.actions.add(
            CompanyCommitAction.objects.create(
                commit=commit,
                target_type="CORPORATION",
                action="CREATE",
                target_id=corporation.c_id,
                new_name=corporation.name,
            )
        )


# 모든 Corporation List
@swagger_auto_schema(
    operation_summary="모든 Corporation List",
)
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
@swagger_auto_schema(
    operation_summary="특정 Corporation의 정보 조회",
)
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

    @swagger_auto_schema(
        operation_summary="Corporation 삭제",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        """
        1) instance.is_active = False, deleted_at=now() → Corporation 소프트 딜리트
        2) 해당 Corporation에 속한 모든 Team(과 하위 조직)도 Deactivate
        3) 그 팀들에 연결된 Role 모두 end_date 처리
        """
        new_commit = self.request.data.get("new_commit", False)
        if new_commit:
            commit = CompanyCommit.objects.create(created_by=self.request.user.person)
        else:
            commit = CompanyCommit.objects.latest("created_at")

        CorporationNameHistoryInfo.objects.create(
            corporation=instance, name="", commit=commit
        )

        if instance.is_active:
            instance.is_active = False
            if not instance.deleted_at:
                instance.deleted_at = timezone.now()
            instance.save()
            teams = instance.teams.all()
            for team in teams:
                self.deactivate_team_recursive(team, commit)
            commit.actions.add(
                CompanyCommitAction.objects.create(
                    commit=commit,
                    target_type="CORPORATION",
                    action="DELETE",
                    target_id=instance.commit_id,
                )
            )
        else:
            # instance.delete()
            pass

    def deactivate_team_recursive(self, team_obj, commit):
        if team_obj.is_active:
            TeamNameHistoryInfo.objects.create(team=team_obj, name="", commit=commit)
            team_obj.is_active = False
            team_obj.deleted_at = timezone.now()
            team_obj.save()
            for child_team in team_obj.lower_teams.all():
                self.deactivate_team_recursive(child_team, commit)


# --- Team Views ---
# 새로운 Team 생성
@swagger_auto_schema(
    operation_summary="새로운 Team 생성",
)
class TeamCreateAPIView(CreateAPIView):
    serializer_class = TeamCreateSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    def perform_create(self, serializer):
        new_commit = self.request.data.get("new_commit", False)
        if new_commit:
            commit = CompanyCommit.objects.create(created_by=self.request.user.person)
        else:
            commit = CompanyCommit.objects.latest("created_at")

        team = serializer.save()
        TeamNameHistoryInfo.objects.create(team=team, name=team.name, commit=commit)
        if team.parent_teams:
            TeamParentHistoryInfo.objects.create(
                team=team, parent_team=team.parent_teams.first(), commit=commit
            )
        commit.actions.add(
            CompanyCommitAction.objects.create(
                commit=commit,
                target_type="TEAM",
                action="CREATE",
                target_id=team.t_id,
                new_name=team.name,
                new_parent_id=team.parent_teams.first().t_id
                if team.parent_teams.first()
                else None,
            )
        )


# 모든 Team List
@swagger_auto_schema(
    operation_summary="모든 Team List",
)
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
@swagger_auto_schema(
    operation_summary="특정 Team의 정보 조회",
)
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

    @swagger_auto_schema(
        operation_summary="Team 삭제",
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def perform_destroy(self, instance):
        new_commit = self.request.data.get("new_commit", False)
        if new_commit:
            commit = CompanyCommit.objects.create(created_by=self.request.user.person)
        else:
            commit = CompanyCommit.objects.latest("created_at")

        TeamNameHistoryInfo.objects.create(team=instance, name="", commit=commit)
        TeamParentHistoryInfo.objects.create(
            team=instance, parent_team=None, commit=commit
        )

        if instance.is_active:
            instance.is_active = False
            if not instance.deleted_at:
                instance.deleted_at = timezone.now()
            instance.save()
            for child_team in instance.sub_teams.all():
                self.deactivate_subteams_recursive(child_team, commit)
            commit.actions.add(
                CompanyCommitAction.objects.create(
                    commit=commit,
                    target_type="CORPORATION",
                    action="DELETE",
                    target_id=instance.commit_id,
                )
            )
        else:
            # instance.delete()
            # Do not delete permanently
            pass

    def deactivate_subteams_recursive(self, team_obj, commit):
        """
        하위 팀들을 재귀적으로 비활성화 + 해당 Role end_date 처리
        """
        if team_obj.is_active:
            TeamNameHistoryInfo.objects.create(team=team_obj, name="", commit=commit)
            TeamParentHistoryInfo.objects.create(
                team=team_obj, parent_team=None, commit=commit
            )
            team_obj.is_active = False
            team_obj.deleted_at = timezone.now()
            team_obj.save()
            for child_team in team_obj.sub_teams.all():
                self.deactivate_subteams_recursive(child_team, commit)


# ----- Role Views -----


class RoleDeleteAPIView(RetrieveDestroyAPIView):
    serializer_class = RoleDetailSerializer
    queryset = Role.objects.all()
    lookup_field = "r_id"
    lookup_url_kwarg = "r_id"
    permission_classes = [IsMasterHRTeam]

    @swagger_auto_schema(
        operation_summary="Role 삭제",
    )
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

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


class CorpRestoreView(RetrieveAPIView):
    serializer_class = CorpRestoreSerializer
    queryset = Corporation.objects.all()
    lookup_field = "c_id"
    lookup_url_kwarg = "c_id"

    @swagger_auto_schema(
        operation_summary="Commit Restore old status",
    )
    def get(self, request, commit_id, c_id):
        commit = get_object_or_404(CompanyCommit, commit_id=commit_id)
        corporation = get_object_or_404(Corporation, c_id=c_id)

        name_history = (
            CorporationNameHistoryInfo.objects.filter(
                corporation=corporation, commit__commit_id__lte=commit.commit_id
            )
            .order_by("-commit__commit_id")
            .first()
        )
        if name_history:
            corporation.name = name_history.name

        latest_commit_per_team = (
            TeamParentHistoryInfo.objects.filter(
                team=OuterRef("team"), commit__commit_id__lte=commit.commit_id
            )
            .values("team")
            .annotate(max_commit_id=Max("commit__commit_id"))
            .values("max_commit_id")
        )

        parent_history = TeamParentHistoryInfo.objects.filter(
            commit__commit_id=Subquery(latest_commit_per_team),
        ).distinct("team")

        sub_teams = []
        for h in parent_history.filter(parent_team=None).all():
            if h.team.corporation.c_id == corporation.c_id and h.parent_team is None:
                sub_teams.append(h.team.t_id)

        corporation_copy = deepcopy(corporation)
        corporation_copy.sub_teams.set(sub_teams)

        serializer = self.get_serializer(corporation_copy, commit=commit)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamRestoreView(RetrieveAPIView):
    serializer_class = TeamRestoreSerializer
    queryset = Team.objects.all()
    lookup_field = "t_id"
    lookup_url_kwarg = "t_id"

    @swagger_auto_schema(
        operation_summary="Commit Restore old status",
    )
    def get(self, request, commit_id, t_id):
        commit = get_object_or_404(CompanyCommit, commit_id=commit_id)
        team = get_object_or_404(Team, t_id=t_id)

        name_history = (
            TeamNameHistoryInfo.objects.filter(
                team=team, commit__created_at__lte=commit.created_at
            )
            .order_by("-commit__commit_id")
            .first()
        )
        if name_history:
            team.name = name_history.name

        latest_commit_per_team = (
            TeamParentHistoryInfo.objects.filter(
                team=OuterRef("team"), commit__commit_id__lte=commit.commit_id
            )
            .values("team")
            .annotate(max_commit_id=Max("commit__commit_id"))
            .values("max_commit_id")
        )

        parent_history = TeamParentHistoryInfo.objects.filter(
            commit__commit_id=Subquery(latest_commit_per_team),
        ).distinct("team")

        sub_teams = []
        for h in parent_history.filter(parent_team=team).all():
            if h.parent_team and h.parent_team.t_id == team.t_id:
                sub_teams.append(h.team.t_id)

        team_copy = deepcopy(team)
        team_copy.sub_teams.set(sub_teams)

        serializer = self.get_serializer(team_copy, commit=commit)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrentCommitView(APIView):
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    @swagger_auto_schema(
        operation_summary="Current Commit",
        manual_parameters=[
            openapi.Parameter(
                "c_id",
                openapi.IN_QUERY,
                description="Corporation ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def get(self, request):
        c_id = self.request.query_params.get("c_id")
        if not c_id:
            commit = CompanyCommit.objects.latest("created_at")
        else:
            commit = (
                CompanyCommit.objects.filter(
                    Q(
                        actions__target_type=CompanyCommitAction.TargetType.TEAM.name,
                        actions__target_id__in=Team.objects.filter(
                            corporation_id=c_id
                        ).values("t_id"),
                    )
                    | Q(
                        actions__target_type=CompanyCommitAction.TargetType.CORPORATION.name,
                        actions__target_id=c_id,
                    )
                )
                .distinct()
                .latest("created_at")
            )
        serializer = CompanyCommitSerializer(commit)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UnclassifiedListAPIView(ListAPIView):
    serializer_class = PersonCardListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (
            Person.objects.filter(Q(teams__isnull=True) | Q(teams__is_active=False))
            .distinct()
            .order_by("name")
        )


class CompanyCommitUpdateView(RetrieveUpdateAPIView):
    serializer_class = CompanyCommitSerializer
    queryset = CompanyCommit.objects.all()
    lookup_field = "commit_id"
    lookup_url_kwarg = "commit_id"
    permission_classes = [IsMasterHRTeam]


class CompanyCommitListView(ListAPIView):
    serializer_class = CompanyCommitSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    @swagger_auto_schema(
        operation_summary="Commit List",
        operation_description="List of all commits",
        manual_parameters=[
            openapi.Parameter(
                "c_id",
                openapi.IN_QUERY,
                description="Corporation ID",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
    )
    def get(self, request):
        return super().get(request)

    def get_queryset(self):
        c_id = self.request.query_params.get("c_id")
        if not c_id:
            return CompanyCommit.objects.all().order_by("-created_at")
        return (
            CompanyCommit.objects.filter(
                Q(
                    actions__target_type=CompanyCommitAction.TargetType.TEAM.name,
                    actions__target_id__in=Team.objects.filter(
                        corporation_id=c_id
                    ).values("t_id"),
                )
                | Q(
                    actions__target_type=CompanyCommitAction.TargetType.CORPORATION.name,
                    actions__target_id=c_id,
                )
            )
            .distinct()
            .order_by("-created_at")
        )


@swagger_auto_schema(
    operation_summary="Commit compare",
    manual_parameters=[
        openapi.Parameter(
            "c_id",
            openapi.IN_QUERY,
            description="Corporation ID",
            type=openapi.TYPE_INTEGER,
            required=False,
        ),
        openapi.Parameter(
            "starting_commit_id",
            openapi.IN_QUERY,
            description="Corporation ID",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
        openapi.Parameter(
            "ending_commit_id",
            openapi.IN_QUERY,
            description="Corporation ID",
            type=openapi.TYPE_INTEGER,
            required=True,
        ),
    ],
)
class CompanyCommitCompareListView(ListAPIView):
    serializer_class = CompanyCommitSerializer
    permission_classes = [Or(IsMasterHRTeam, IsHRTeam)]

    def get_queryset(self):
        c_id = self.request.query_params.get("c_id")
        starting_commit_id = self.request.query_params.get("starting_commit_id")
        ending_commit_id = self.request.query_params.get("ending_commit_id")

        queryset = CompanyCommit.objects.filter(
            commit_id__gte=starting_commit_id,
            commit_id__lte=ending_commit_id,
        ).order_by("-created_at")

        if c_id:
            team_ids = Team.objects.filter(corporation_id=c_id).values_list(
                "t_id", flat=True
            )
            queryset = queryset.filter(
                Q(
                    actions__target_type=CompanyCommitAction.TargetType.TEAM.name,
                    actions__target_id__in=team_ids,
                )
                | Q(
                    actions__target_type=CompanyCommitAction.TargetType.CORPORATION.name,
                    actions__target_id=c_id,
                )
            ).distinct()

        return queryset

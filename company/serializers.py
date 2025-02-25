from django.utils import timezone
from rest_framework import serializers
from .models import Corporation, Team, Role
from person.models import Person
from django.db import transaction
from personCard.serializers import RoleSupervisorHistorySerializer


# ----- Corporation Serializers -----
class CorpListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ["c_id", "name", "sub_teams", "is_active", "is_master"]


class CorpDetailSerializer(serializers.ModelSerializer):
    sub_teams = CorpListSerializer(
        many=True, read_only=True, source="corporation_sub_teams"
    )
    hr_team = CorpListSerializer(read_only=True, source="corporation_hr_team")

    class Meta:
        model = Corporation
        fields = ["c_id", "name", "sub_teams", "hr_team", "is_active"]


class CorpCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ["name", "sub_teams", "is_active", "is_master"]


class CorpEditUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ["name", "sub_teams", "is_active", "is_master", "hr_team"]

    def deactivate_corporation_recursive(self, corp_obj):
        from django.utils import timezone

        if corp_obj.is_active:
            corp_obj.is_active = False
            if not corp_obj.deleted_at:
                corp_obj.deleted_at = timezone.now()
            corp_obj.save()

            # 소속 팀들 비활성화
            for team in corp_obj.teams.all():
                if team.is_active:
                    TeamEditUpdateSerializer.deactivate_team_recursive(team)

    def update(self, instance, validated_data):
        sub_teams = validated_data.pop("sub_teams", None)
        old_is_active = instance.is_active

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # is_active가 False로 변경 시
        if old_is_active and not instance.is_active:
            self.deactivate_corporation_recursive(instance)

        if sub_teams is not None:
            instance.sub_teams.set(sub_teams)

        return instance


# ----- Team Serializers -----
class TeamListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["t_id", "name", "corporation", "sub_teams", "is_active"]


class TeamEditListSerializer(serializers.ModelSerializer):
    corporation = CorpDetailSerializer(read_only=True)
    # 하위 조직은 역참조인 lower_teams를 TeamListSerializer로 표시
    sub_teams = TeamListSerializer(many=True, read_only=True, source="lower_teams")

    class Meta:
        model = Team
        fields = ["t_id", "name", "corporation", "sub_teams", "is_active"]


class TeamDetailSerializer(serializers.ModelSerializer):
    corporation = CorpDetailSerializer(read_only=True)
    # 하위 조직은 역참조인 lower_teams를 TeamListSerializer로 표시
    sub_teams = TeamListSerializer(many=True, read_only=True, source="lower_teams")
    # 상위 조직은 커스텀 메서드로 부모 체인을 구성하여 상세 정보와 order 값을 함께 반환
    parent_teams = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Person.objects.all()
    )
    team_leader = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "t_id",
            "name",
            "corporation",
            "sub_teams",
            "parent_teams",
            "team_leader",
            "members",
            "member_count",
            "is_active",
            "created_at",
            "deleted_at",
        ]

    def get_parent_teams(self, obj):
        parent_chain = []
        current_team = obj
        order = 0
        # 현재 팀의 상위 체인을 모두 추적 (최상위까지)
        while current_team.parent_teams.exists():
            parent_team = current_team.parent_teams.first()
            # TeamListSerializer를 통해 상세 정보를 가져오고, order 값을 추가
            serialized = TeamListSerializer(parent_team, context=self.context).data
            serialized["order"] = order
            parent_chain.append(serialized)
            current_team = parent_team
            order += 1
        return parent_chain

    def get_member_count(self, obj):
        return obj.members.count()


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            "name",
            "corporation",
            "sub_teams",
            "parent_teams",
            "members",
            "team_leader",
            "is_active",
        ]

    def create(self, validated_data):
        # ManyToManyField 분리
        parent_teams = validated_data.pop("parent_teams", [])
        sub_teams = validated_data.pop("sub_teams", [])
        members = validated_data.pop("members", [])

        # # 같은 corporation에 속한 활성 팀 중 동일한 이름이 존재하는지 확인
        corporation = validated_data.get("corporation")
        # name = validated_data.get('name')
        # if corporation and Team.objects.filter(corporation=corporation, name=name, is_active=True).exists():
        #     raise serializers.ValidationError("같은 corporation 내에 활성 상태의 동일한 이름의 팀이 이미 존재합니다.")

        # 팀 생성일 자동 저장
        validated_data["created_at"] = timezone.now()

        # 팀 생성
        team = Team.objects.create(**validated_data)

        # ManyToMany 필드 설정
        team.parent_teams.set(parent_teams)
        team.sub_teams.set(sub_teams)
        team.members.set(members)

        # parent_teams가 빈 리스트이면, 자동으로 해당 팀을 corporation의 sub_teams에 추가
        if not parent_teams and corporation:
            corporation.sub_teams.add(team)

        return team


class TeamEditUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ["name", "corporation", "sub_teams", "parent_teams"]

    def deactivate_team_recursive(self, team_obj):
        """
        팀(team_obj)과 하위 조직을 재귀적으로 비활성화,
        그리고 진행 중인 Role(end_date가 null)을 모두 종료.
        """
        from django.utils import timezone

        if team_obj.is_active:
            team_obj.is_active = False
            if not team_obj.deleted_at:
                team_obj.deleted_at = timezone.now()
            team_obj.save()

            # 연관 Role 소프트 종료
            for role in team_obj.roles.filter(end_date__isnull=True):
                role.end_date = timezone.now()
                role.save()

        # 하위 팀(lower_teams)들도 동일하게 비활성화 처리
        for child in team_obj.lower_teams.all():
            if child.is_active:
                self.deactivate_team_recursive(child)

    def update(self, instance, validated_data):
        from django.utils import timezone

        # ManyToMany 필드 분리
        parent_teams_data = validated_data.pop("parent_teams", None)
        sub_teams = validated_data.pop("sub_teams", None)
        members = validated_data.pop("members", None)

        # 기존 is_active 값 기억
        old_is_active = instance.is_active

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # 만약 is_active가 False로 바뀌었을 때 (old_is_active=True & new_is_active=False)
        new_is_active = instance.is_active
        if old_is_active and not new_is_active:
            # 소프트 딜리트
            if not instance.deleted_at:
                instance.deleted_at = timezone.now()
            instance.save()

            # 하위 조직 비활성화 + Role 종료
            self.deactivate_team_recursive(instance)

        # parent_teams 업데이트
        if parent_teams_data is not None:
            if parent_teams_data and isinstance(parent_teams_data[0], dict):
                # [{'t_id': ..., 'order': ...}, ...] 형태라면
                filtered_parent_ids = [
                    d["t_id"] for d in parent_teams_data if d.get("order") == 0
                ]
            else:
                filtered_parent_ids = parent_teams_data
            instance.parent_teams.set(filtered_parent_ids)

            # parent_teams가 빈 리스트라면, 소속 corporation의 sub_teams에 추가
            if len(filtered_parent_ids) == 0 and instance.corporation:
                instance.corporation.sub_teams.add(instance)

        if sub_teams is not None:
            instance.sub_teams.set(sub_teams)
        if members is not None:
            instance.members.set(members)

        return instance


# class TeamUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Team
#         fields = [
#             'name', 'corporation', 'sub_teams',
#             'parent_teams', 'members', 'team_leader', 'is_active'
#         ]
#
#     def deactivate_team_recursive(self, team_obj):
#         """
#         팀(team_obj)과 하위 조직을 재귀적으로 비활성화,
#         그리고 진행 중인 Role(end_date가 null)을 모두 종료.
#         """
#         from django.utils import timezone
#
#         if team_obj.is_active:
#             team_obj.is_active = False
#             if not team_obj.deleted_at:
#                 team_obj.deleted_at = timezone.now()
#             team_obj.save()
#
#             # 연관 Role 소프트 종료
#             for role in team_obj.roles.filter(end_date__isnull=True):
#                 role.end_date = timezone.now()
#                 role.save()
#
#         # 하위 팀(lower_teams)들도 동일하게 비활성화 처리
#         for child in team_obj.lower_teams.all():
#             if child.is_active:
#                 deactivate_team_recursive(child)
#
#
#     def update(self, instance, validated_data):
#         from django.utils import timezone
#
#         # ManyToMany 필드 분리
#         parent_teams_data = validated_data.pop('parent_teams', None)
#         sub_teams = validated_data.pop('sub_teams', None)
#         members = validated_data.pop('members', None)
#
#         # 기존 is_active 값 기억
#         old_is_active = instance.is_active
#
#         # 일반 필드 업데이트
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         # 만약 is_active가 False로 바뀌었을 때 (old_is_active=True & new_is_active=False)
#         new_is_active = instance.is_active
#         if old_is_active and not new_is_active:
#             # 소프트 딜리트
#             if not instance.deleted_at:
#                 instance.deleted_at = timezone.now()
#             instance.save()
#
#             # 하위 조직 비활성화 + Role 종료
#             self.deactivate_team_recursive(instance)
#
#         # parent_teams 업데이트
#         if parent_teams_data is not None:
#             if parent_teams_data and isinstance(parent_teams_data[0], dict):
#                 # [{'t_id': ..., 'order': ...}, ...] 형태라면
#                 filtered_parent_ids = [d['t_id'] for d in parent_teams_data if d.get('order') == 0]
#             else:
#                 filtered_parent_ids = parent_teams_data
#             instance.parent_teams.set(filtered_parent_ids)
#
#             # parent_teams가 빈 리스트라면, 소속 corporation의 sub_teams에 추가
#             if len(filtered_parent_ids) == 0 and instance.corporation:
#                 instance.corporation.sub_teams.add(instance)
#
#         if sub_teams is not None:
#             instance.sub_teams.set(sub_teams)
#         if members is not None:
#             instance.members.set(members)
#
#         return instance


# ----- Role Serializers -----
class ActiveRoleSerializer(serializers.ModelSerializer):
    team = serializers.CharField(source="team.name", read_only=True)
    supervisor = serializers.CharField(source="supervisor.name", read_only=True)

    class Meta:
        model = Role
        fields = ["r_id", "team", "role_name", "supervisor", "isHR"]


# class PersonRolesUpdateSerializer(serializers.ModelSerializer):
#     # roles:  [{"t_id": 1, "role": "부서원"}, {"t_id": 2, "role": "팀장"}, ...]
#     roles = serializers.JSONField()
#
#     class Meta:
#         model = Person
#         fields = ['roles']
#
#     def update(self, instance, validated_data):
#         with transaction.atomic():
#             roles_data = validated_data.get('roles', [])
#             instance.roles = roles_data
#             instance.save()
#
#             # Step 1. ManyToMany Field (teams) 업데이트:
#             # roles_data에서 각 딕셔너리의 t_id 값을 추출하여, Person의 팀 관계를 설정합니다.
#             team_ids = [role_info.get('t_id') for role_info in roles_data if role_info.get('t_id')]
#             # ManyToMany 관계 업데이트: 해당 팀 목록으로 교체(set)
#             instance.teams.set(team_ids)
#
#             # Step 2. PersonalHistory 업데이트:
#             # 각 역할 정보를 기준으로 개인 이력(PersonalHistory)을 업데이트하거나 새 레코드를 생성합니다.
#             for role_info in roles_data:
#                 team_id = role_info.get('t_id')
#                 role_value = role_info.get('role')
#
#                 if not team_id:
#                     continue
#
#                 # 현재 진행 중(종료일(end_date)이 없는) 해당 팀의 이력이 있는지 확인
#                 history = instance.personal_histories.filter(t_id=team_id, end_date__isnull=True).first()
#                 team_instance = Team.objects.get(pk=team_id)  # team이 먼저 존재한다고 가정
#
#                 if history:
#                     if history.role != role_value:
#                         # 기존 이력이 있으나 역할이 달라졌다면, 새로운 이력 레코드를 생성
#                         history.end_date = timezone.now()
#                         history.save()
#                         PersonalHistory.objects.create(
#                             person=instance,
#                             start_date=timezone.now(),
#                             team=team_instance,
#                             role=role_value,
#                             supervisor=None  # supervisor 업데이트는 팀 로직에 따라 처리 (예: 팀 리더 정보 활용)
#                         )
#                     # 역할이 동일한 경우는 아무런 작업을 하지 않습니다.
#                 else:
#                     # 진행 중인 이력이 없으면 새 레코드를 생성합니다.
#                     PersonalHistory.objects.create(
#                         person=instance,
#                         start_date=timezone.now(),
#                         team=team_instance,
#                         role=role_value,
#                         supervisor=None
#                     )
#
#         return instance


class RoleCreateSerializer(serializers.ModelSerializer):
    """
    Role 생성용 Serializer.
    - 클라이언트는 person, team(t_id)만 전달하며, (선택적으로) old_role_id도 함께 전달한다고 가정.
    - old_role_id가 있으면 해당 Role을 종료(end_date 기록)한 후 새 Role을 생성.
    - 만약 role_name이 "부서장"이면:
         * 새 Role의 supervisor는 상위 팀의 team_leader(존재 시)로 설정.
         * 해당 팀의 team_leader를 새 Role의 person으로 업데이트.
         * 그 팀의 모든 구성원(팀 멤버)의 진행 중인 Role의 supervisor를 새 팀장으로 업데이트.
         * 기존 팀장의 진행 중인 Role이 있다면 종료 처리.
    """

    old_role_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = Role
        fields = [
            "person",
            "team",
            "supervisor",
            "role_name",
            "start_date",
            "end_date",
            "job_description",
            "is_HR",
            "old_role_id",
        ]
        read_only_fields = ["end_date"]

    def validate(self, attrs):
        old_role_id = attrs.get("old_role_id")
        if old_role_id:
            old_role = Role.objects.filter(r_id=old_role_id).first()
            if not old_role:
                raise serializers.ValidationError("old_role_id가 유효하지 않습니다.")
            if attrs.get("person") != old_role.person:
                raise serializers.ValidationError(
                    "old_role_id의 person과 생성할 person이 다릅니다."
                )
        return attrs

    def create(self, validated_data):
        old_role_id = validated_data.pop("old_role_id", None)
        person = validated_data.get("person")
        team_input = validated_data.get("team")

        # team_input이 인스턴스가 아니라 t_id라면 Team instance 조회
        if not isinstance(team_input, Team):
            try:
                team_instance = Team.objects.get(t_id=team_input)
            except Team.DoesNotExist:
                raise serializers.ValidationError(
                    "제공된 team t_id에 해당하는 팀이 존재하지 않습니다."
                )
        else:
            team_instance = team_input
        validated_data["team"] = team_instance

        # 기존 역할 종료 처리
        if old_role_id:
            old_role = Role.objects.get(r_id=old_role_id)
            if not old_role.end_date:
                old_role.end_date = timezone.now()
                old_role.save()

        # 기본값 처리: role_name, start_date
        if not validated_data.get("role_name"):
            validated_data["role_name"] = "부서원"
        role_name = validated_data.get("role_name")
        if not validated_data.get("start_date"):
            validated_data["start_date"] = timezone.now()

        # supervisor 기본값 처리:
        if not validated_data.get("supervisor"):
            if role_name == "부서장":
                # 상위 팀의 팀장이 있다면, 그 값을 supervisor로 설정, 없으면 None
                parent_team = team_instance.parent_teams.first()
                validated_data["supervisor"] = (
                    parent_team.team_leader if parent_team else None
                )
            else:
                validated_data["supervisor"] = team_instance.team_leader

        # is_HR 자동 설정: 해당 팀이 소속 법인의 hr_team과 동일하면 True, 아니면 False
        if (
            team_instance.corporation
            and team_instance.corporation.hr_team == team_instance
        ):
            validated_data["is_HR"] = True
        else:
            validated_data["is_HR"] = False

        # 새 Role 생성
        new_role = super().create(validated_data)

        # 추가 로직: 만약 새 Role의 role_name이 "부서장"이면
        if new_role.role_name == "부서장":
            # 1. 기존 팀의 팀 리더를 새 Role의 person으로 업데이트
            old_team_leader = team_instance.team_leader  # 기존 팀장
            team_instance.team_leader = new_role.person
            team_instance.save()

            # 2. 해당 팀의 모든 구성원들의 진행 중인 Role(supervisor)을 새 팀장으로 업데이트
            for member in team_instance.members.all():
                active_role = member.roles.filter(
                    team=team_instance, end_date__isnull=True
                ).first()
                if active_role:
                    active_role.update_supervisor(new_role.person)

            # 3. 만약 기존 팀장이 새 팀장과 다르다면, 해당 기존 팀장의 진행 중인 Role 종료 처리
            if old_team_leader and old_team_leader != new_role.person:
                old_leader_role = Role.objects.filter(
                    person=old_team_leader, team=team_instance, end_date__isnull=True
                ).first()
                if old_leader_role:
                    old_leader_role.end_date = timezone.now()
                    old_leader_role.save()

        return new_role


class RoleUpdateSerializer(serializers.ModelSerializer):
    """
    특정 Role의 role_name 변경 요청을 받아,
    기존 Role을 종료하고 새 Role 인스턴스를 생성하는 Serializer.

    추가 로직:
      - 이전 role이 "부서장"이고 새 role이 "부서장"이 아닐 경우,
        팀의 team_leader를 해제하고, 해당 팀 구성원들의 진행 중 Role의 supervisor를 상위 팀의 팀리더(존재 시)로 업데이트합니다.
      - 새 role의 supervisor는 새 role이 "부서장"이면 상위 팀의 팀리더로, 그렇지 않으면 기본적으로 팀의 team_leader로 설정합니다.
      - 새 role의 is_HR 여부는 팀이 속한 법인의 hr_team과 해당 팀이 일치하면 자동으로 True로 설정합니다.
    """

    class Meta:
        model = Role
        fields = ["role_name", "job_description", "is_HR"]
        # supervisor, start_date, end_date는 자동으로 처리됨

    def update(self, instance, validated_data):
        new_role_name = validated_data.get("role_name", instance.role_name)
        new_job_description = validated_data.get(
            "job_description", instance.job_description
        )
        # is_HR는 자동 판단
        team_instance = instance.team
        old_role_name = instance.role_name

        # 자동 is_HR 판단: 팀의 소속 법인의 hr_team과 현재 팀이 동일하면 True
        if (
            team_instance
            and team_instance.corporation
            and team_instance.corporation.hr_team == team_instance
        ):
            new_is_HR = True
        else:
            new_is_HR = False

        with transaction.atomic():
            # 1. 기존 Role 종료 (소프트 종료)
            instance.end_date = timezone.now()
            instance.save()

            # 2. 새 Role 데이터 준비 (person, team 등 동일)
            new_role_data = {
                "person": instance.person,
                "team": team_instance,
                "role_name": new_role_name,
                "job_description": new_job_description,
                "is_HR": new_is_HR,
                "start_date": timezone.now(),
            }

            # supervisor 기본 설정:
            if new_role_name == "부서장":
                parent_team = (
                    team_instance.parent_teams.first() if team_instance else None
                )
                new_role_data["supervisor"] = (
                    parent_team.team_leader if parent_team else None
                )
            else:
                new_role_data["supervisor"] = (
                    team_instance.team_leader if team_instance else None
                )

            new_role = Role.objects.create(**new_role_data)

            # 3. 추가 로직: 이전 role이 "부서장"이고 새 role이 "부서장"이 아닌 경우
            if old_role_name == "부서장" and new_role_name != "부서장":
                # (a) 팀의 team_leader 해제
                team_instance.team_leader = None
                team_instance.save()

                # (b) 해당 팀 구성원들의 진행 중 Role의 supervisor 업데이트
                for member in team_instance.members.all():
                    active_role = member.roles.filter(
                        team=team_instance, end_date__isnull=True
                    ).first()
                    if active_role and active_role.supervisor == instance.person:
                        parent_team = (
                            team_instance.parent_teams.first()
                            if team_instance
                            else None
                        )
                        new_sup = parent_team.team_leader if parent_team else None
                        active_role.update_supervisor(new_sup)

                # (c) 새 Role의 supervisor 업데이트: 상위 팀의 팀리더(존재 시)로
                parent_team = (
                    team_instance.parent_teams.first() if team_instance else None
                )
                new_role.supervisor = parent_team.team_leader if parent_team else None
                new_role.save()

        return new_role


# 직무 히스토리 정보 불러오기
class RoleDetailSerializer(serializers.ModelSerializer):
    # Nested: supervisor_history
    supervisor_history = RoleSupervisorHistorySerializer(
        many=True,
        read_only=True,
    )

    # team, supervisor 필드 등 추가
    t_id = serializers.IntegerField(source="team.t_id", read_only=True)
    team_name = serializers.CharField(source="team.name", read_only=True)
    supervisor_id = serializers.IntegerField(source="supervisor.p_id", read_only=True)
    supervisor_name = serializers.CharField(source="supervisor.name", read_only=True)

    class Meta:
        model = Role
        fields = [
            "r_id",
            "t_id",
            "team_name",
            "role_name",
            "supervisor_id",
            "supervisor_name",
            "start_date",
            "end_date",
            "job_description",
            "is_HR",
            "supervisor_history",
        ]

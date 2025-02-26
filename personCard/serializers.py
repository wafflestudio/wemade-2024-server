from rest_framework import serializers
from person.models import Person, PersonalInfo, PersonCardInfo
from company.models import Role, RoleSupervisorHistory
from .validators import PersonCardInfoValidator


class PersonCardListSerializer(serializers.ModelSerializer):
    emails = serializers.SerializerMethodField()
    phone_number = serializers.CharField(
        source="personal_info.main_phone_number", required=False, allow_null=True
    )
    corporations = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    def get_corporations(self, obj):
        return list(set(team.corporation.commit_id for team in obj.member_of_teams.all()))

    def get_teams(self, obj):
        return [team.t_id for team in obj.member_of_teams.all()]

    def get_roles(self, obj):
        return [
            {"t_id": role.team.t_id, "r_id": role.r_id, "role": role.role_name}
            for role in obj.roles.filter(end_date__isnull=True)
        ]

    class Meta:
        model = Person
        fields = [
            "p_id",
            "name",
            "emails",
            "phone_number",
            "corporations",
            "teams",
            "roles",
        ]

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []


class PersonCardListDetailSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        source="personal_info.main_phone_number", required=False, allow_null=True
    )
    info = serializers.JSONField(
        source="personal_info.p_info", required=False, allow_null=True
    )
    emails = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ["name", "phone_number", "info", "emails"]

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []


class PersonCardDetailSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        source="personal_info.main_phone_number", required=False, allow_null=True
    )
    info = serializers.JSONField(
        source="personal_info.p_info", required=False, allow_null=True
    )
    emails = serializers.SerializerMethodField()
    p_card_info = serializers.JSONField(
        source="personal_info.p_card_info.p_card_info", required=False, allow_null=True
    )

    class Meta:
        model = Person
        fields = ["name", "phone_number", "info", "emails", "p_card_info"]

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []


class PersonalInfoUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(
        source="main_phone_number", required=False, allow_null=True
    )
    emails = serializers.SerializerMethodField()

    validate_public_info = PersonCardInfoValidator(expected_public=True)
    validate_private_info = PersonCardInfoValidator(expected_public=False)

    # 공개 정보는 p_info JSON에 저장
    p_info = serializers.JSONField(
        required=False, allow_null=True, validators=[validate_public_info]
    )
    # 비공개 정보는 p_card_info JSON에 저장
    p_card_info = serializers.JSONField(
        source="p_card_info.p_card_info",
        required=False,
        allow_null=True,
        validators=[validate_private_info],
    )

    class Meta:
        model = PersonalInfo
        fields = ["name", "phone_number", "p_info", "emails", "p_card_info"]

    def get_emails(self, obj):
        if obj and isinstance(obj.emails, list):
            return obj.emails
        return []

    def update(self, instance, validated_data):
        p_card_info_data = validated_data.pop("p_card_info", None)
        instance = super().update(instance, validated_data)
        p_card_info = instance.p_card_info
        if not p_card_info:
            p_card_info = PersonCardInfo.objects.create()
            instance.p_card_info = p_card_info
            instance.save()
        if p_card_info_data:
            p_card_info.p_card_info = p_card_info_data
            p_card_info.save()
        return instance


class RoleSupervisorHistorySerializer(serializers.ModelSerializer):
    old_supervisor_id = serializers.IntegerField(
        source="old_supervisor.p_id", read_only=True
    )
    old_supervisor_name = serializers.CharField(
        source="old_supervisor.name", read_only=True
    )
    new_supervisor_id = serializers.IntegerField(
        source="new_supervisor.p_id", read_only=True
    )
    new_supervisor_name = serializers.CharField(
        source="new_supervisor.name", read_only=True
    )

    class Meta:
        model = RoleSupervisorHistory
        fields = [
            "id",  # RoleSupervisorHistory id
            "old_supervisor_id",
            "old_supervisor_name",
            "new_supervisor_id",
            "new_supervisor_name",
            "changed_at",
        ]


# 직무 히스토리 정보 불러오기
class RoleHistorySerializer(serializers.ModelSerializer):
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


# 직무 설명(job_description) 업데이트만을 위한 serializer
class RoleHistoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["job_description"]

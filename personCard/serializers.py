from rest_framework import serializers
from person.models import Person, PersonalInfo, PersonCardInfo
from company.models import Role, RoleSupervisorHistory
from .models import PersonCardChangeRequest, PersonCardColumns
from .validators import PersonCardInfoValidator


RESTRICTED_FIELDS = ["main_phone_number", "birthday", "name"]


class PersonCardListSerializer(serializers.ModelSerializer):
    emails = serializers.SerializerMethodField()
    phone_number = serializers.CharField(
        source="personal_info.main_phone_number", required=False, allow_null=True
    )
    corporations = serializers.SerializerMethodField()
    teams = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    def get_corporations(self, obj):
        return list(
            set(team.corporation.commit_id for team in obj.member_of_teams.all())
        )

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
    roles = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ["name", "phone_number", "info", "emails", "p_card_info", "roles"]

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []

    def get_roles(self, obj):
        return [
            {"t_id": role.team.t_id, "r_id": role.r_id, "role": role.role_name}
            for role in obj.roles.filter(end_date__isnull=True)
        ]


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
        # Pop out p_info and p_card_info data
        new_p_card_info_data = validated_data.pop("p_card_info", None)
        new_p_info_data = validated_data.pop("p_info", None)

        # Process RESTRICTED_FIELDS: don't update them immediately; create change requests instead.
        change_requests = []
        for field in RESTRICTED_FIELDS:
            if field in validated_data:
                new_value = validated_data.pop(field)
                old_value = getattr(instance, field, "")
                if old_value != new_value:
                    supporting_material = request_files.get(field)
                    # Create a change request (status is pending)
                    req = PersonCardChangeRequest.objects.create(
                        person=instance.person,
                        field_name=field,
                        old_value=old_value,
                        new_value=new_value,
                        status="pending",
                        supporting_material=supporting_material,
                    )
                    change_requests.append(req)

        # Update instance with remaining fields immediately
        instance = super().update(instance, validated_data)

        # Process p_info updates
        if new_p_info_data is not None:
            current_p_info = instance.p_info if instance.p_info else {}
            for key, new_value in new_p_info_data.items():
                column = PersonCardColumns.objects.filter(column_name=key).first()
                if column and column.permission_required:
                    old_value = current_p_info.get(key, "")
                    if old_value != new_value:
                        supporting_material = request_files.get(key)
                        PersonCardChangeRequest.objects.create(
                            person=instance.person,
                            column=column,
                            old_value=str(old_value),
                            new_value=str(new_value),
                            status="pending",
                            supporting_material=supporting_material,
                        )
                    # Do not immediately update
                else:
                    current_p_info[key] = new_value
            instance.p_info = current_p_info
            instance.save()

        # Process p_card_info updates similarly
        if new_p_card_info_data is not None:
            if instance.p_card_info and instance.p_card_info.p_card_info:
                current_p_card_info = instance.p_card_info.p_card_info
            else:
                current_p_card_info = {}
            for key, new_value in new_p_card_info_data.items():
                column = PersonCardColumns.objects.filter(column_name=key).first()
                if column and column.permission_required:
                    old_value = current_p_card_info.get(key, "")
                    if old_value != new_value:
                        supporting_material = request_files.get(key)
                        PersonCardChangeRequest.objects.create(
                            person=instance.person,
                            column=column,
                            old_value=str(old_value),
                            new_value=str(new_value),
                            status="pending",
                            supporting_material=supporting_material,
                        )
                else:
                    current_p_card_info[key] = new_value
            # Ensure p_card_info instance exists
            p_card_info_instance = instance.p_card_info
            if not p_card_info_instance:
                p_card_info_instance = PersonCardInfo.objects.create()
                instance.p_card_info = p_card_info_instance
                instance.save()
            if current_p_card_info:
                p_card_info_instance.p_card_info = current_p_card_info
                p_card_info_instance.save()

        return instance


class PersonCardChangeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonCardChangeRequest
        fields = [
            "id",
            "person",
            "column",
            "old_value",
            "new_value",
            "status",
            "requested_at",
            "reviewed_at",
            "reviewed_by",
            "supporting_material",
        ]


class PersonCardChangeRequestReviewSerializer(serializers.ModelSerializer):
    reviewed_by = serializers.PrimaryKeyRelatedField(read_only=True)
    reviewed_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = PersonCardChangeRequest
        fields = [
            "id",
            "person",
            "column",
            "old_value",
            "new_value",
            "status",
            "requested_at",
            "reviewed_at",
            "reviewed_by",
            "supporting_material",
        ]
        read_only_fields = [
            "id",
            "person",
            "column",
            "old_value",
            "new_value",
            "requested_at",
            "supporting_material",
        ]

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")
        if new_status not in ["approved", "rejected"]:
            raise serializers.ValidationError(
                "Status must be either 'approved' or 'rejected'."
            )
        instance.status = new_status
        instance.reviewed_at = timezone.now()
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            instance.reviewed_by = request.user.person
        instance.save()

        if new_status == "approved":
            # 실제 개인정보 업데이트: 승인된 경우에만 PersonalInfo에 반영
            personal_info = instance.person.personal_info
            if not personal_info:
                raise serializers.ValidationError(
                    "해당 직원의 PersonalInfo가 존재하지 않습니다."
                )

            column = instance.column  # PersonCardColumns instance
            new_value = instance.new_value

            # 만약 해당 칼럼이 top-level 필드(예: RESTRICTED_FIELDS)에 해당하면
            if column.column_name in RESTRICTED_FIELDS:
                setattr(personal_info, column.column_name, new_value)
                personal_info.save()
            else:
                # JSON 업데이트: 공개 정보와 비공개 정보 구분
                if column.is_public:
                    current_info = personal_info.p_info if personal_info.p_info else {}
                    current_info[column.column_name] = new_value
                    personal_info.p_info = current_info
                    personal_info.save()
                else:
                    p_card_info_instance = personal_info.p_card_info
                    if not p_card_info_instance:
                        p_card_info_instance = PersonCardInfo.objects.create()
                        personal_info.p_card_info = p_card_info_instance
                        personal_info.save()
                    current_p_card_info = (
                        p_card_info_instance.p_card_info
                        if p_card_info_instance.p_card_info
                        else {}
                    )
                    current_p_card_info[column.column_name] = new_value
                    p_card_info_instance.p_card_info = current_p_card_info
                    p_card_info_instance.save()
            # 승인되었으므로 최종 상태 변경
            instance.status = "applied"
            instance.save()
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

class CardColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonCardColumns
        fields = "__all__"
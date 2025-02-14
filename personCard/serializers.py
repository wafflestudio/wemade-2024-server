from rest_framework import serializers
from person.models import Person, PersonalInfo, PersonCardInfo, PersonalHistory
from django.utils import timezone


class PersonCardListSerializer(serializers.ModelSerializer):
    emails = serializers.SerializerMethodField()
    phone_number = serializers.CharField(source='personal_info.main_phone_number', required=False, allow_null=True)
    corporation = serializers.CharField(default="")
    team = serializers.CharField(default="")
    role = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Person
        fields = ['p_id', 'name', 'emails', 'phone_number', 'corporation', 'team', 'role']

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []


class PersonCardListDetailSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='personal_info.main_phone_number', required=False, allow_null=True)
    info = serializers.JSONField(source='personal_info.p_info', required=False, allow_null=True)
    emails = serializers.SerializerMethodField()

    class Meta:
        model = Person
        fields = ['name', 'phone_number', 'info', 'emails']

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []


class PersonCardDetailSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='personal_info.main_phone_number', required=False, allow_null=True)
    info = serializers.JSONField(source='personal_info.p_info', required=False, allow_null=True)
    emails = serializers.SerializerMethodField()
    p_card_info = serializers.JSONField(source='personal_info.p_card_info.p_card_info', required=False, allow_null=True)

    class Meta:
        model = Person
        fields = ['name', 'phone_number', 'info', 'emails', 'p_card_info']

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []



class PersonalInfoUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='main_phone_number', required=False, allow_null=True)
    emails = serializers.SerializerMethodField()

    validate_public_info = PersonCardInfoValidator(expected_public=True)
    validate_private_info = PersonCardInfoValidator(expected_public=False)

    # 공개 정보는 p_info JSON에 저장
    p_info = serializers.JSONField(
        source='p_info',
        required=False,
        allow_null=True,
        validators=[validate_public_info]
    )
    # 비공개 정보는 p_card_info JSON에 저장
    p_card_info = serializers.JSONField(
        source='p_card_info.p_card_info',
        required=False,
        allow_null=True,
        validators=[validate_private_info]
    )

    class Meta:
        model = PersonalInfo
        fields = ['name', 'phone_number', 'p_info', 'emails', 'p_card_info']

    def get_emails(self, obj):
        if obj and isinstance(obj.emails, list):
            return obj.emails
        return []

    def update(self, instance, validated_data):
        p_card_info_data = validated_data.pop('p_card_info', None)
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


class PersonRolesUpdateSerializer(serializers.ModelSerializer):
    # roles:  [{"t_id": 1, "role": "부서원"}, {"t_id": 2, "role": "팀장"}, ...]
    roles = serializers.JSONField()

    class Meta:
        model = Person
        fields = ['roles']

    def update(self, instance, validated_data):
        with transaction.atomic():
            roles_data = validated_data.get('roles', [])
            instance.roles = roles_data
            instance.save()

            # Step 1. ManyToMany Field (teams) 업데이트:
            # roles_data에서 각 딕셔너리의 t_id 값을 추출하여, Person의 팀 관계를 설정합니다.
            team_ids = [role_info.get('t_id') for role_info in roles_data if role_info.get('t_id')]
            # ManyToMany 관계 업데이트: 해당 팀 목록으로 교체(set)
            instance.teams.set(team_ids)

            # Step 2. PersonalHistory 업데이트:
            # 각 역할 정보를 기준으로 개인 이력(PersonalHistory)을 업데이트하거나 새 레코드를 생성합니다.
            for role_info in roles_data:
                team_id = role_info.get('t_id')
                role_value = role_info.get('role')

                if not team_id:
                    continue

                # 현재 진행 중(종료일(end_date)이 없는) 해당 팀의 이력이 있는지 확인
                history = instance.personal_histories.filter(t_id=team_id, end_date__isnull=True).first()
                team_instance = Team.objects.get(pk=team_id)  # team이 먼저 존재한다고 가정

                if history:
                    if history.role != role_value:
                        # 기존 이력이 있으나 역할이 달라졌다면, 새로운 이력 레코드를 생성
                        history.end_date = timezone.now()
                        history.save()
                        PersonalHistory.objects.create(
                            person=instance,
                            start_date=timezone.now(),
                            team=team_instance,
                            role=role_value,
                            supervisor=None  # supervisor 업데이트는 팀 로직에 따라 처리 (예: 팀 리더 정보 활용)
                        )
                    # 역할이 동일한 경우는 아무런 작업을 하지 않습니다.
                else:
                    # 진행 중인 이력이 없으면 새 레코드를 생성합니다.
                    PersonalHistory.objects.create(
                        person=instance,
                        start_date=timezone.now(),
                        team=team_instance,
                        role=role_value,
                        supervisor=None
                    )

        return instance


class PersonalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalHistory
        fields = ['id', 'start_date', 'end_date', 'team', 'role', 'supervisor', 'job_description']


# 직무 설명(job_description) 업데이트만을 위한 serializer
class PersonalHistoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalHistory
        fields = ['job_description']


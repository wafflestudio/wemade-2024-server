from rest_framework import serializers
from person.models import Person, PersonalInfo, PersonCardInfo


class PersonCardListSerializer(serializers.ModelSerializer):
    emails = serializers.SerializerMethodField()
    corporation = serializers.CharField(default="")
    team = serializers.CharField(default="")
    role = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Person
        fields = ['p_id', 'name', 'emails', 'corporation', 'team', 'role']

    def get_emails(self, obj):
        if obj.personal_info and isinstance(obj.personal_info.emails, list):
            return obj.personal_info.emails
        return []


class PersonCardListDetailSerializer(serializers.ModelSerializer):
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


class PersonCardUpdateSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='main_phone_number', required=False, allow_null=True)
    info = serializers.JSONField(source='p_info', required=False, allow_null=True)
    emails = serializers.SerializerMethodField()
    p_card_info = serializers.JSONField(source='p_card_info.p_card_info', required=False, allow_null=True)

    class Meta:
        model = PersonalInfo
        fields = ['name', 'phone_number', 'info', 'emails', 'p_card_info']

    def get_emails(self, obj):
        if obj and isinstance(obj.emails, list):
            return obj.emails
        return []

    def update(self, instance, validated_data):
        p_card_info_data = validated_data.pop('p_card_info', None)
        super().update(instance, validated_data)
        p_card_info = instance.p_card_info
        if not p_card_info:
            p_card_info = PersonCardInfo.objects.create()
            instance.p_card_info = p_card_info
            instance.save()
        if p_card_info_data:
            p_card_info.p_card_info = p_card_info_data
            p_card_info.save()
        return instance

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if 'p_card_info' in ret and isinstance(ret['p_card_info'], dict) and 'p_card_info' in ret['p_card_info']:
            ret['p_card_info'] = ret['p_card_info']['p_card_info']
        return ret
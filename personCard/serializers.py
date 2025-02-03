from rest_framework import serializers
from person.models import Person, PersonalInfo


class PersonCardListSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    corporation = serializers.CharField(default="")
    team = serializers.CharField(default="")
    role = serializers.CharField(default="")

    class Meta:
        model = Person
        fields = ['p_id', 'name', 'email', 'corporation', 'team', 'role']

    def get_email(self, obj):
        account = Account.objects.filter(p_id=obj).first()
        return account.email if account else None


class PersonCardListDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    phone_number = serializers.CharField(required=False, allow_null=True)
    info = serializers.ListField(child=serializers.JSONField(), required=False, allow_null=True)
    emails = serializers.ListField(child=serializers.EmailField(), required=False, allow_null=True)

    class Meta:
        model = Person
        fields = ['name', 'phone_number', 'info', 'emails']

    def get_emails(self, obj):
        account = Account.objects.filter(p_id=obj).first()
        return account.email if account else None


class PersonCardDetailSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    phone_number = serializers.CharField(required=False, allow_null=True)
    info = serializers.JSONField(required=False, allow_null=True)
    emails = serializers.ListField(child=serializers.EmailField(), required=False, allow_null=True)

    class Meta:
        model = Person
        fields = ['name', 'phone_number', 'info', 'emails']

    def get_emails(self, obj):
        account = Account.objects.filter(p_id=obj).first()
        return account.email if account else None


class PersonCardUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    phone_number = serializers.CharField(required=False, allow_null=True)
    info = serializers.JSONField(required=False, allow_null=True)
    emails = serializers.ListField(child=serializers.EmailField(), required=False, allow_null=True)

    class Meta:
        model = PersonalInfo
        fields = ['name', 'phone_number', 'info', 'emails']

    def get_emails(self, obj):
        account = Account.objects.filter(p_id=obj).first()
        return account.email if account else None
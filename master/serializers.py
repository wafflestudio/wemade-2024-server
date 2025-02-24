from rest_framework import serializers
from personCard.models import PersonCardColumns
from oauth.models import EmailDomain


class PersonCardColumnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonCardColumns
        fields = ['id', 'column_name', 'column_type', 'permission_required', 'is_multiple', 'is_supporting_material_required', 'is_public']


class EmailDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDomain
        fields = '__all__'

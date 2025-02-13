from rest_framework import serializers
from .models import PersonCardColumns, EmailDomain


class PersonCardColumnsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonCardColumns
        fields = ['id', 'column_name', 'column_type', 'is_multiple', 'is_supporting_material_required', 'is_public']


class EmailDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailDomain
        fields = '__all__'

from rest_framework import serializers
from .models import StorageFile


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageFile
        fields = "__all__"

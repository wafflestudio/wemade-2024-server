from django.views import View
from .models import StorageFile
from .serializers import FileSerializer

class FileUploadView(View):
    serializer_class = FileSerializer
    queryset = StorageFile.objects.all()
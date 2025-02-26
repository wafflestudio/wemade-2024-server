from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from .models import StorageFile


class FileUploadView(APIView):
    parser_classes = [FileUploadParser]

    def post(self, request, format=None):
        file_obj = request.data["file"]
        uploaded_file = StorageFile.objects.create(file=file_obj)
        return Response({"file_url": uploaded_file.file.url})

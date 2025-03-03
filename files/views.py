from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import FileUploadParser
from .models import StorageFile
from drf_yasg.utils import swagger_auto_schema

@swagger_auto_schema(operation_summary="upload file", request_body=FileUploadParser)
class FileUploadView(APIView):
    parser_classes = [FileUploadParser]

    def post(self, request, format=None):
        file_obj = request.data["file"]
        uploaded_file = StorageFile.objects.create(file=file_obj)
        return Response({"file_url": uploaded_file.file.url})

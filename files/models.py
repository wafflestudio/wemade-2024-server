from django.db import models

class StorageFile(models.Model):
    file = models.FileField(upload_to="files/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
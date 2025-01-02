from django.db import models

# Create your models here.

class User(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        db_table = 'user'
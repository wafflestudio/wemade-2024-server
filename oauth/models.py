from django.contrib.auth.models import AbstractUser
from django.db import models
from person.models import Person

class OauthInfo(AbstractUser):
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField()
    oauth_provider = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'oauth_info'
        
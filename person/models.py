from django.db import models

class PersonalInfo(models.Model):
    name = models.CharField(max_length=100, null=True)
    emails = models.JSONField()

    class Meta:
        db_table = 'personal_info'

class Person(models.Model):
    personal_info = models.OneToOneField(PersonalInfo, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'person'
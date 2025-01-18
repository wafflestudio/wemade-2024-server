from django.db import models

class PersonalInfo(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

    class Meta:
        db_table = 'personal_info'
        app_label = 'person'

class Person(models.Model):
    personal_info = models.ForeignKey(PersonalInfo, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        db_table = 'person'
        app_label = 'person'
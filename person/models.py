from django.db import models

class PersonalInfo(models.Model):
    p_id = models.ForeignKey('Person', on_delete=models.CASCADE)
    p_info = models.JSONField(null=True, blank=True)  # JSON 데이터를 저장할 필드

    class Meta:
        db_table = 'personal_info'
        app_label = 'person'


class Person(models.Model):
    p_id = models.IntegerField(null=False, unique=True)  # p_id를 고유값으로 설정
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'person'
        app_label = 'person'


class Account(models.Model):
    email = models.EmailField()
    p_id = models.ForeignKey('Person', null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = 'account'
        app_label = 'person'

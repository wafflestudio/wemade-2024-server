from django.db import models

class Person(models.Model):
    p_id = models.BigAutoField(primary_key=True) # p_id를 고유값으로 설정
    name = models.CharField(max_length=100)
    personal_info = models.OneToOneField(PersonalInfo, on_delete=models.SET_NULL, null=True)
    roles = models.JSONField(null=True)


    class Meta:
        db_table = 'person'
        app_label = 'person'


class PersonalInfo(models.Model):
    ## 가정: 생일 & 이름이 같은 사람은 없다
    main_phone_number = models.TextField(max_length=13)  # '010-0000-0000' 형태, 여러 개일 수 있음
    name = models.CharField(max_length=100, null=True)
    emails = models.JSONField()
    birthday = models.TextField(max_length=10) #2000-01-01 형태
    p_info = models.JSONField(null=True, blank=True)  # JSON 데이터를 저장할 필드


    class Meta:
        db_table = 'personal_info'

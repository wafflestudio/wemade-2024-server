from django.db import models
from person.models import *
#from company.models import * #company branch와 병합 후 주석 해제


# p_info: 공개정보(자격증 등), p_card_info(비공개/인사카드 정보)
class PersonCardInfo(models.Model):
    p_card_info = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'personCard_info'


class PersonalInfo(models.Model):
    main_phone_number = models.TextField(max_length=13, null=True)  # '010-0000-0000' 형태
    name = models.CharField(max_length=100, null=True)
    emails = models.JSONField()
    birthday = models.TextField(max_length=10, null=True) # 2000-01-01 형태
    p_info = models.JSONField(null=True, blank=True)  # 공개 정보
    p_card_info = models.OneToOneField(PersonCardInfo, on_delete=models.CASCADE, null=True) # 비공개 정보

    class Meta:
        db_table = 'personal_info'


class Person(models.Model):
    p_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    personal_info = models.OneToOneField(PersonalInfo, on_delete=models.SET_NULL, null=True)

    #corporations = models.ManyToManyField(Corporate, related_name="persons", blank=True)
    #teams = models.ManyToManyField(Team, related_name="persons", blank=True)

    roles = models.JSONField(null=True, blank=True)  # 역할 정보 (예: {"role": "developer", "level": "senior"})

    class Meta:
        db_table = "person"
        app_label = "person"


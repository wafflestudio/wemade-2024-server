from django.db import models


class PersonCardInfo(models.Model):
    p_card_info = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'personCard_info'


class PersonalInfo(models.Model):
    main_phone_number = models.TextField(max_length=13, null=True)
    name = models.CharField(max_length=100, null=True)
    emails = models.JSONField()
    birthday = models.TextField(max_length=10, null=True)
    p_info = models.JSONField(null=True, blank=True)
    p_card_info = models.OneToOneField(PersonCardInfo, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'personal_info'


class Person(models.Model):
    p_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    personal_info = models.OneToOneField(PersonalInfo, on_delete=models.SET_NULL, null=True)

    # 직접 import 없이 문자열 참조 사용
    corporations = models.ManyToManyField('company.Corporation', related_name="corporation_persons", blank=True)
    teams = models.ManyToManyField('company.Team', related_name="team_persons", blank=True)

    roles = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "person"
        app_label = "person"

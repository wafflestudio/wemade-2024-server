from company.models import *


# p_info: 공개정보(자격증 등), p_card_info(비공개/인사카드 정보)
class PersonCardInfo(models.Model):
    p_card_info = models.JSONField(null=True, blank=True, default=dict)

    class Meta:
        db_table = "personCard_info"


class PersonalInfo(models.Model):
    main_phone_number = models.TextField(
        max_length=13, null=True
    )  # '010-0000-0000' 형태
    name = models.CharField(max_length=100, null=True)
    emails = models.JSONField()
    birthday = models.TextField(max_length=10, null=True)  # 2000-01-01 형태
    p_info = models.JSONField(
        null=True, blank=True, default=dict
    )  # 공개 정보 : certificates 정보 있다고 생각
    p_card_info = models.OneToOneField(
        PersonCardInfo,
        on_delete=models.CASCADE,
        null=True,
        default=PersonCardInfo.objects.create,
    )  # 비공개 정보

    class Meta:
        db_table = "personal_info"


class Person(models.Model):
    p_id = models.BigAutoField(primary_key=True)
    employee_id = models.CharField(max_length=20)  # 사번 구조에 따라 변경 필요
    name = models.CharField(max_length=100)  # 이름
    personal_info = models.OneToOneField(
        PersonalInfo, on_delete=models.SET_NULL, null=True
    )  # 퇴사 시 삭제될 개인 정보

    corporations = models.ManyToManyField(
        "company.Corporation", related_name="corporation_persons", blank=True
    )
    teams = models.ManyToManyField(
        "company.Team", related_name="team_persons", blank=True
    )

    # roles = models.JSONField(null=True, blank=True) # 내부 구조: {{"t_id": "", "role": "부서원"}, {"t_id": "", "role":""},...}

    class Meta:
        db_table = "person"
        app_label = "person"


class PersonalHistory(models.Model):
    person = models.ForeignKey(
        "person.Person",
        on_delete=models.SET_NULL,
        null=True,
        related_name="personal_histories",
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True)
    team = models.ForeignKey("company.Team", on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=20)  # 한 팀에서는 role이 하나라고 가정
    supervisor = models.IntegerField()  # 해당 시기 team의 team_leader(p_id)
    job_description = models.TextField(null=True)

    class Meta:
        db_table = "personal_history"

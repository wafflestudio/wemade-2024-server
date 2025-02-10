from django.db import models
from person.models import Person


class Corporation(models.Model):
    c_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    sub_teams = models.ManyToManyField('Team', related_name='corporation_sub_teams', blank=True)  # 하위 팀들

    class Meta:
        db_table = 'corporation'


class Team(models.Model):
    t_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    # 소속된 법인
    corporation = models.ForeignKey(Corporation, related_name='teams', on_delete=models.CASCADE, null=True, blank=True)

    # 팀들 사이 관계
    sub_teams = models.ManyToManyField('self', related_name='super_teams', symmetrical=False, blank=True)  # 하위 팀들
    parent_teams = models.ManyToManyField('self', related_name='lower_teams', symmetrical=False, blank=True)  # 상위 조직들

    # 팀 정보
    members = models.ManyToManyField(Person, related_name='teams', blank=True)  # 팀원 목록
    team_leader = models.ForeignKey(Person, related_name='leading_teams', on_delete=models.SET_NULL, null=True, blank=True)  # 팀장 (1명)

    class Meta:
        db_table = 'team'

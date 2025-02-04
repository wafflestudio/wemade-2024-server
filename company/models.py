from django.db import models
from person.models import Person


class Corporate(models.Model):
    name = models.CharField(max_length=255)
    sub_teams = models.ManyToManyField('Team', related_name='corporate_sub_teams', blank=True)  # 하위 팀들

    class Meta:
        db_table = 'corporate'


class Team(models.Model):
    name = models.CharField(max_length=255)
    sub_teams = models.ManyToManyField('self', related_name='parent_teams', symmetrical=False, blank=True)  # 하위 팀들
    parent_teams = models.ManyToManyField('self', related_name='child_teams', symmetrical=False, blank=True)  # 상위 조직들
    members = models.ManyToManyField(Person, related_name='teams', blank=True)  # 팀원 목록
    team_leader = models.ForeignKey(Person, related_name='leading_teams', on_delete=models.SET_NULL, null=True, blank=True)  # 팀장 (1명)

    class Meta:
        db_table = 'team'

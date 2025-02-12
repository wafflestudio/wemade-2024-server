from django.db import models

class Corporation(models.Model):
    c_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    sub_teams = models.ManyToManyField('Team', related_name='corporation_sub_teams', blank=True)
    # 문자열 참조 사용: 'person.Person'
    hr_team_members = models.ManyToManyField('person.Person', related_name='hr_team_members', blank=True)

    class Meta:
        db_table = 'corporation'


class Team(models.Model):
    t_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)

    corporation = models.ForeignKey(Corporation, related_name='teams', on_delete=models.CASCADE, null=True, blank=True)

    sub_teams = models.ManyToManyField('self', related_name='super_teams', symmetrical=False, null=True,  blank=True)
    parent_teams = models.ManyToManyField('self', related_name='lower_teams', symmetrical=False, null=True, blank=True)

    # 문자열 참조 사용
    members = models.ManyToManyField('person.Person', related_name='member_of_teams', blank=True)
    team_leader = models.ForeignKey('person.Person', related_name='leading_teams', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'team'

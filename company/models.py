from django.db import models


class Corporation(models.Model):
    c_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # 현재 존재하는 법인 여부
    is_master = models.BooleanField(default=False)  # 본사 여부

    sub_teams = models.ManyToManyField('company.Team', related_name='corporation_sub_teams', blank=True)
    hr_team = models.ForeignKey('company.Team', related_name='corporation_hr_team', on_delete=models.SET_NULL, null=True)

    # 생성일과 삭제일 추가
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'corporation'


class Team(models.Model):
    t_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    corporation = models.ForeignKey(Corporation, related_name='teams', on_delete=models.CASCADE, null=True, blank=True)

    sub_teams = models.ManyToManyField('self', related_name='super_teams', symmetrical=False, null=True,  blank=True)
    parent_teams = models.ManyToManyField('self', related_name='lower_teams', symmetrical=False, null=True, blank=True)

    # 문자열 참조 사용
    members = models.ManyToManyField('person.Person', related_name='member_of_teams', blank=True)
    team_leader = models.ForeignKey('person.Person', related_name='leading_teams', on_delete=models.SET_NULL, null=True, blank=True)

    # 생성일과 삭제일 추가
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'team'

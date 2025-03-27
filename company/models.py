from django.db import models
from django.utils import timezone


class Corporation(models.Model):
    c_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)  # 현재 존재하는 법인 여부
    is_master = models.BooleanField(default=False)  # 본사 여부

    sub_teams = models.ManyToManyField(
        "company.Team", related_name="corporation_sub_teams", blank=True
    )
    hr_team = models.ForeignKey(
        "company.Team",
        related_name="corporation_hr_team",
        on_delete=models.SET_NULL,
        null=True,
    )

    # 생성일과 삭제일 추가
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    last_commit = models.ForeignKey(
        "company.CompanyCommit", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "corporation"


class Team(models.Model):
    t_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    corporation = models.ForeignKey(
        Corporation,
        related_name="teams",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    sub_teams = models.ManyToManyField(
        "self", related_name="super_teams", symmetrical=False, blank=True
    )
    parent_teams = models.ManyToManyField(
        "self", related_name="lower_teams", symmetrical=False, blank=True
    )

    # 문자열 참조 사용
    members = models.ManyToManyField(
        "person.Person", related_name="member_of_teams", blank=True
    )
    team_leader = models.ForeignKey(
        "person.Person",
        related_name="leading_teams",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # 생성일과 삭제일 추가
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    last_commit = models.ForeignKey(
        "company.CompanyCommit", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        db_table = "team"


class Role(models.Model):
    class RoleType(models.TextChoices):
        EMPLOYEE = "부서원"
        HEAD = "부서장"

    r_id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(
        "person.Person", on_delete=models.CASCADE, related_name="roles"
    )
    team = models.ForeignKey(
        "company.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roles",
    )
    supervisor = models.ForeignKey(
        "person.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="supervised_roles",
    )
    role_name = models.CharField(
        max_length=50, null=True, blank=True, choices=RoleType.choices
    )
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    is_HR = models.BooleanField(default=False)

    class Meta:
        db_table = "role"

    def __str__(self):
        return f"{self.person.name} - {self.role_name}"

    def update_supervisor(self, new_supervisor):
        # 만약 supervisor가 변경된다면, 히스토리 기록을 남깁니다.
        if self.supervisor != new_supervisor:
            RoleSupervisorHistory.objects.create(
                role=self,
                old_supervisor=self.supervisor,
                new_supervisor=new_supervisor,
                changed_at=timezone.now(),
            )
            self.supervisor = new_supervisor
            self.save()


class RoleSupervisorHistory(models.Model):
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name="supervisor_history"
    )
    old_supervisor = models.ForeignKey(
        "person.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="old_supervisor_roles",
    )
    new_supervisor = models.ForeignKey(
        "person.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="new_supervisor_roles",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "role_supervisor_history"

    def __str__(self):
        return f"Role {self.role.r_id}: {self.old_supervisor} -> {self.new_supervisor} at {self.changed_at}"


class CompanyCommit(models.Model):
    created_by = models.ForeignKey(
        "person.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commits_made",
    )
    commit_id = models.BigAutoField(primary_key=True)
    name = models.CharField(
        max_length=255,
        default="Change of " + timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company_commit"


class CompanyCommitAction(models.Model):
    class CommitType(models.TextChoices):
        CREATE = "CREATE"
        UPDATE = "UPDATE"
        DELETE = "DELETE"

    class TargetType(models.TextChoices):
        CORPORATION = "corporation"
        TEAM = "team"

    commit = models.ForeignKey(
        CompanyCommit, on_delete=models.CASCADE, related_name="actions"
    )
    action = models.CharField(
        max_length=50, choices=CommitType.choices, default=CommitType.CREATE
    )

    target_type = models.CharField(
        max_length=50, choices=TargetType.choices, default=TargetType.TEAM
    )
    new_parent_id = models.BigIntegerField(null=True, blank=True)
    target_id = models.BigIntegerField(null=True, blank=True)
    new_name = models.CharField(max_length=255, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "company_commit_action"


class CorporationNameHistoryInfo(models.Model):
    commit = models.ForeignKey(
        CompanyCommit,
        on_delete=models.CASCADE,
        related_name="corporation_name_histories",
    )
    name = models.CharField(max_length=255)
    corporation = models.ForeignKey(
        Corporation, on_delete=models.CASCADE, related_name="name_histories"
    )

    class Meta:
        db_table = "corp_name_history"


class TeamNameHistoryInfo(models.Model):
    commit = models.ForeignKey(
        CompanyCommit, on_delete=models.CASCADE, related_name="team_name_histories"
    )
    name = models.CharField(max_length=255)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="name_histories"
    )

    class Meta:
        db_table = "team_name_history"


class TeamParentHistoryInfo(models.Model):
    commit = models.ForeignKey(
        CompanyCommit, on_delete=models.CASCADE, related_name="team_parent_histories"
    )
    parent_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="subteam_histories", null=True
    )
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="parent_histories", null=True
    )

    class Meta:
        db_table = "team_parent_history"


class Draft(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        "person.Person",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="drafts",
    )
    changes = models.JSONField()

    class Meta:
        db_table = "draft"

    def __str__(self):
        return f"Draft by {self.created_by} at {self.created_at}"

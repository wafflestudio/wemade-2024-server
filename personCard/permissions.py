from rest_framework import permissions


class IsHRTeam(permissions.BasePermission):
    """
    대상 Person이 속한 팀의 소속 corporation의 hr_team 팀원인 경우
    """
    def has_object_permission(self, request, view, obj):
        # obj는 Person 또는 PersonalInfo 객체라고 가정
        user_person = getattr(request.user, 'person', None)
        if not user_person:
            return False

        # 대상 Person 결정
        target_person = obj if hasattr(obj, 'p_id') else getattr(obj, 'person', None)
        if not target_person:
            return False

        # 대상 Person이 속한 팀들 각각에 대해, 그 팀이 소속된 corporation의 hr_team에 요청 사용자가 속하는지 확인
        for team in target_person.member_of_teams.all():
            corp = team.corporation
            if corp and corp.hr_team:
                if user_person in corp.hr_team.members.all():
                    return True

        return False


class IsOwnerOrHRTeam(permissions.BasePermission):
    """
    본인 or 대상 Person이 속한 팀의 소속 corporation의 hr_team 팀원인 경우
    """
    def has_object_permission(self, request, view, obj):
        # obj는 Person 또는 PersonalInfo 객체라고 가정
        user_person = getattr(request.user, 'person', None)
        if not user_person:
            return False

        # 대상 Person 결정
        target_person = obj if hasattr(obj, 'p_id') else getattr(obj, 'person', None)
        if not target_person:
            return False

        # 본인인 경우 허용
        if user_person == target_person:
            return True

        # 대상 Person이 속한 팀들 각각에 대해, 그 팀이 소속된 corporation의 hr_team에 요청 사용자가 속하는지 확인
        for team in target_person.member_of_teams.all():
            corp = team.corporation
            if corp and corp.hr_team:
                if user_person in corp.hr_team.members.all():
                    return True

        return False


class IsOwnerOrHRTeamOrTeamLeader(permissions.BasePermission):
    """
    본인 or 대상 Person이 속한 팀의 팀의 리더 or 팀의 소속 corporation의 hr_team 팀원
    """
    def has_object_permission(self, request, view, obj):
        user_person = getattr(request.user, 'person', None)
        if not user_person:
            return False

        target_person = obj if hasattr(obj, 'p_id') else getattr(obj, 'person', None)
        if not target_person:
            return False

        # 본인인 경우
        if user_person == target_person:
            return True

        # 대상 Person의 각 팀에 대해 corporation의 hr_team에 사용자가 속하는지 확인
        for team in target_person.member_of_teams.all():
            corp = team.corporation
            if corp and corp.hr_team and user_person in corp.hr_team.members.all():
                return True

        # 대상 Person이 속한 팀에서 사용자가 팀 리더인 경우
        if target_person.member_of_teams.filter(team_leader=user_person).exists():
            return True

        return False

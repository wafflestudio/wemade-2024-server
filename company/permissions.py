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

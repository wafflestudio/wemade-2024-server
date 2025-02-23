from rest_framework import permissions


class IsMasterHRTeam(permissions.BasePermission):
    """
    본사(hr팀) 권한: 요청 사용자의 person이 소속된 팀 중,
    소속된 corporation이 is_master=True이고 해당 corporation의 hr_team에 속해 있다면 모든 권한을 허용.
    """
    def has_permission(self, request, view):
        user_person = getattr(request.user, 'person', None)
        if not user_person:
            return False
        # 사용자가 속한 팀들을 순회하며, 본사 hr_team 소속 여부 확인
        for team in user_person.member_of_teams.all():
            corp = team.corporation
            if corp and corp.is_master and corp.hr_team:
                if user_person in corp.hr_team.members.all():
                    return True
        return False

    def has_object_permission(self, request, view, obj):
        # object-level permission도 동일하게 체크
        return self.has_permission(request, view)


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

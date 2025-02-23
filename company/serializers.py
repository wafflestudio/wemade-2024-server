from rest_framework import serializers
from .models import Corporation, Team, Commit
from person.models import Person


# Corporation Serializers
class CorpListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ['c_id', 'name']


class CorpDetailSerializer(serializers.ModelSerializer):
    sub_teams = serializers.PrimaryKeyRelatedField(many=True, queryset=Team.objects.all())

    class Meta:
        model = Corporation
        fields = ['c_id', 'name', 'sub_teams']


class CorpCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ['name', 'sub_teams']


class CorpUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ['name', 'sub_teams']


# Team Serializers
class TeamListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['t_id', 'name', 'corporation', 'member_count']

    def get_member_count(self, obj):
        return obj.members.count()


class TeamDetailSerializer(serializers.ModelSerializer):
    corporation = CorpDetailSerializer()
    sub_teams = serializers.PrimaryKeyRelatedField(many=True, queryset=Team.objects.all(), source='lower_teams')
    parent_teams = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(many=True, queryset=Person.objects.all())
    team_leader = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['t_id', 'name', 'corporation', 'sub_teams', 'parent_teams', 'team_leader', 'members', 'member_count']

    def get_parent_teams(self, obj):
        parent_teams = []
        current_team = obj
        order = 0
        while current_team.parent_teams.exists():
            parent_team = current_team.parent_teams.first()
            parent_teams.append({'t_id': parent_team.t_id, 'name': parent_team.name, 'order': order})
            current_team = parent_team
            order += 1  # 상위조직일수록 order가 크게
        return parent_teams

    def get_member_count(self, obj):
        return obj.members.count()


class TeamCreateSerializer(serializers.ModelSerializer):
    parent_team_history = serializers.ListField(default=list)
    name_history = serializers.ListField(default=list)
    class Meta:
        model = Team
        fields = ['t_id', 'name', 'corporation', 'sub_teams', 'parent_teams', 'members', 'team_leader', 'parent_team_history', 'name_history', 'last_commit']
        read_only_fields = ['t_id']

class TeamUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['t_id', 'name', 'corporation', 'sub_teams', 'parent_teams', 'members', 'team_leader']
        read_only_fields = ['t_id']

class CommitListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commit
        fields = ['commit_id', 'commit_message', 'commit_date', 'commit_author', 'commit_content']
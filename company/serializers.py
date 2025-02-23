# serializers.py
from rest_framework import serializers
from .models import Corporation, Team
from person.models import Person

# Corporation Serializers
class CorpListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ['c_id', 'name', 'is_active']


class CorpDetailSerializer(serializers.ModelSerializer):
    sub_teams = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Team.objects.all()
    )

    class Meta:
        model = Corporation
        fields = ['c_id', 'name', 'sub_teams', 'is_active']


class CorpCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ['name', 'sub_teams', 'is_active']


class CorpUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ['name', 'sub_teams', 'is_active']


# Team Serializers
class TeamListSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ['t_id', 'name', 'corporation', 'member_count', 'is_active']

    def get_member_count(self, obj):
        return obj.members.count()


class TeamDetailSerializer(serializers.ModelSerializer):
    corporation = CorpDetailSerializer(read_only=True)
    # 하위 조직은 parent_teams의 역참조인 lower_teams를 사용하여 표현
    sub_teams = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Team.objects.all(),
        source='lower_teams'
    )
    parent_teams = serializers.SerializerMethodField()
    members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Person.objects.all()
    )
    team_leader = serializers.PrimaryKeyRelatedField(
        queryset=Person.objects.all()
    )
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            't_id', 'name', 'corporation', 'sub_teams',
            'parent_teams', 'team_leader', 'members', 'member_count', 'is_active'
        ]

    def get_parent_teams(self, obj):
        # 상위 조직 정보를 order와 함께 반환 (최상위까지)
        parent_teams = []
        current_team = obj
        order = 0
        while current_team.parent_teams.exists():
            parent_team = current_team.parent_teams.first()
            parent_teams.append({
                't_id': parent_team.t_id,
                'name': parent_team.name,
                'order': order
            })
            current_team = parent_team
            order += 1
        return parent_teams

    def get_member_count(self, obj):
        return obj.members.count()


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'name', 'corporation', 'sub_teams',
            'parent_teams', 'members', 'team_leader', 'is_active'
        ]

    def create(self, validated_data):
        # ManyToManyField 분리
        parent_teams = validated_data.pop('parent_teams', [])
        sub_teams = validated_data.pop('sub_teams', [])
        members = validated_data.pop('members', [])

        # 팀 생성
        team = Team.objects.create(**validated_data)

        # ManyToMany 필드 설정
        team.parent_teams.set(parent_teams)
        team.sub_teams.set(sub_teams)
        team.members.set(members)

        # parent_teams가 빈 리스트이면, 자동으로 해당 Team을 corporation의 sub_teams에 추가
        if not parent_teams:
            corporation = validated_data.get('corporation')
            if corporation:
                corporation.sub_teams.add(team)

        return team


class TeamUpdateDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = [
            'name', 'corporation', 'sub_teams',
            'parent_teams', 'members', 'team_leader', 'is_active'
        ]

    def update(self, instance, validated_data):
        # ManyToMany 필드 분리
        parent_teams = validated_data.pop('parent_teams', None)
        sub_teams = validated_data.pop('sub_teams', None)
        members = validated_data.pop('members', None)

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # ManyToMany 필드 업데이트: 값이 전달된 경우에만 처리
        if parent_teams is not None:
            instance.parent_teams.set(parent_teams)
            # parent_teams가 빈 리스트면 corporation의 sub_teams에 추가
            if len(parent_teams) == 0 and instance.corporation:
                instance.corporation.sub_teams.add(instance)
        if sub_teams is not None:
            instance.sub_teams.set(sub_teams)
        if members is not None:
            instance.members.set(members)

        return instance


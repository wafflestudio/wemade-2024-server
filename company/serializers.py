from django.utils import timezone
from rest_framework import serializers
from .models import Corporation, Team
from person.models import Person

# Corporation Serializers
class CorpListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Corporation
        fields = ['c_id', 'name', 'is_active']


class CorpDetailSerializer(serializers.ModelSerializer):
    sub_teams = TeamListSerializer(many=True, read_only=True, source='corporation_sub_teams')
    hr_team = TeamListSerializer(read_only=True, source='corporation_hr_team')

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

    def update(self, instance, validated_data):
        # ManyToMany 필드 분리
        sub_teams = validated_data.pop('sub_teams', None)

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # is_active가 False이고 deleted_at이 아직 설정되지 않았다면, 현재 시간으로 설정
        if 'is_active' in validated_data and not validated_data.get('is_active'):
            if not instance.deleted_at:
                instance.deleted_at = timezone.now()

        instance.save()

        # sub_teams 업데이트: 값이 전달된 경우에만 처리
        if sub_teams is not None:
            instance.sub_teams.set(sub_teams)

        return instance


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
    # 하위 조직은 역참조인 lower_teams를 TeamListSerializer로 표시
    sub_teams = TeamListSerializer(many=True, read_only=True, source='lower_teams')
    # 상위 조직은 커스텀 메서드로 부모 체인을 구성하여 상세 정보와 order 값을 함께 반환
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
            'parent_teams', 'team_leader', 'members', 'member_count', 'is_active', 'created_at', 'deleted_at'
        ]

    def get_parent_teams(self, obj):
        parent_chain = []
        current_team = obj
        order = 0
        # 현재 팀의 상위 체인을 모두 추적 (최상위까지)
        while current_team.parent_teams.exists():
            parent_team = current_team.parent_teams.first()
            # TeamListSerializer를 통해 상세 정보를 가져오고, order 값을 추가
            serialized = TeamListSerializer(parent_team, context=self.context).data
            serialized['order'] = order
            parent_chain.append(serialized)
            current_team = parent_team
            order += 1
        return parent_chain

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

        # 같은 corporation에 속한 활성 팀 중 동일한 이름이 존재하는지 확인
        corporation = validated_data.get('corporation')
        name = validated_data.get('name')
        if corporation and Team.objects.filter(corporation=corporation, name=name, is_active=True).exists():
            raise serializers.ValidationError("같은 corporation 내에 활성 상태의 동일한 이름의 팀이 이미 존재합니다.")

        # 팀 생성일 자동 저장 (Team 모델에 created_at 필드가 있다고 가정)
        validated_data['created_at'] = timezone.now()

        # 팀 생성
        team = Team.objects.create(**validated_data)

        # ManyToMany 필드 설정
        team.parent_teams.set(parent_teams)
        team.sub_teams.set(sub_teams)
        team.members.set(members)

        # parent_teams가 빈 리스트이면, 자동으로 해당 팀을 corporation의 sub_teams에 추가
        if not parent_teams and corporation:
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
        # ManyToMany 필드 분리: parent_teams, sub_teams, members
        parent_teams_data = validated_data.pop('parent_teams', None)
        sub_teams = validated_data.pop('sub_teams', None)
        members = validated_data.pop('members', None)

        # 일반 필드 업데이트
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # deleted_at 필드 업데이트
        if 'is_active' in validated_data and not validated_data.get('is_active'):
            if not instance.deleted_at:
                instance.deleted_at = timezone.now()
            instance.is_active = False

        instance.save()

        # parent_teams 업데이트
        if parent_teams_data is not None:
            # 전달된 값이 [{'t_id': ..., 'name': ..., 'order': ...}, ...] 형태
            if parent_teams_data and isinstance(parent_teams_data[0], dict):
                filtered_parent_ids = [d['t_id'] for d in parent_teams_data if d.get('order') == 0]
            else:
                filtered_parent_ids = parent_teams_data

            instance.parent_teams.set(filtered_parent_ids)

            # parent_teams가 빈 리스트이면 corporation의 sub_teams에 추가
            if len(filtered_parent_ids) == 0 and instance.corporation:
                instance.corporation.sub_teams.add(instance)

        if sub_teams is not None:
            instance.sub_teams.set(sub_teams)
        if members is not None:
            instance.members.set(members)

        return instance



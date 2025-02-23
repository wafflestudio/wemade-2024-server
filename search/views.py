from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from person.models import Person
from company.models import Team, Corporation
from personCard.serializers import PersonCardListSerializer
from company.serializers import CorpListSerializer, TeamListSerializer

from django.db.models import F, Value, Func, CharField


class RemoveSpaces(Func):
    function = 'REPLACE'
    template = "%(function)s(%(expressions)s, ' ', '')"
    output_field = CharField()


# Person의 소속 법인/팀, 자격증으로 검색
class PersonSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        # 검색 기준: 'name' 또는 'certificate' (기본은 'name')
        search_by = request.query_params.get('search_by', 'name').lower()
        query = request.query_params.get('q', '')
        filter_corp = request.query_params.get('corp_id')
        filter_team = request.query_params.get('team_id')

        persons = Person.objects.all()

        # 특정 팀 또는 법인 조건이 들어온 경우 해당 팀(및 하위 조직) 산하 사람들로 범위 한정
        team_ids = None
        if filter_team:
            try:
                team = Team.objects.get(t_id=filter_team)
            except Team.DoesNotExist:
                return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
            team_ids = self.get_lower_team_ids(team)
        elif filter_corp:
            try:
                corp = Corporation.objects.get(c_id=filter_corp)
            except Corporation.DoesNotExist:
                return Response({"detail": "Corporation not found."}, status=status.HTTP_404_NOT_FOUND)
            team_ids = set()
            for team in corp.teams.all():
                team_ids.update(self.get_lower_team_ids(team))
        if team_ids:
            persons = persons.filter(member_of_teams__t_id__in=team_ids)

        # 검색 조건 적용
        if search_by == 'name':
            if query:
                query_clean = query.replace(' ', '')
                persons = persons.annotate(
                    clean_name=RemoveSpaces(F('name'))
                ).filter(clean_name__icontains=query_clean)
        elif search_by == 'certificate':
            # certificate 검색 시에도 q 파라미터 사용
            if query:
                query_clean = query.replace(' ', '')
                persons = persons.annotate(
                    clean_cert=RemoveSpaces(F('personal_info__p_info__certificates'))
                ).filter(clean_cert__icontains=query_clean)
        else:
            # 기본은 name 검색
            if query:
                query_clean = query.replace(' ', '')
                persons = persons.annotate(
                    clean_name=RemoveSpaces(F('name'))
                ).filter(clean_name__icontains=query_clean)

        persons = persons.distinct().order_by('name')
        serializer = PersonCardListSerializer(persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_lower_team_ids(self, team_obj):
        ids = {team_obj.t_id}
        for child in team_obj.lower_teams.all():
            ids.update(self.get_lower_team_ids(child))
        return ids




# Team 이름으로 Team 검색
class TeamSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        teams = Team.objects.all().order_by('name')
        if query:
            query_clean = query.replace(' ', '')
            teams = teams.annotate(clean_name=RemoveSpaces(F('name'))).filter(clean_name__icontains=query_clean)
        serializer = TeamListSerializer(teams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Coporation 이름으로 Corp 검색
class CorpSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        corps = Corporation.objects.all().order_by('name')
        if query:
            query_clean = query.replace(' ', '')
            corps = corps.annotate(clean_name=RemoveSpaces(F('name'))).filter(clean_name__icontains=query_clean)
        serializer = CorpListSerializer(corps, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


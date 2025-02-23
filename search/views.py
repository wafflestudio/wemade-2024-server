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



# class SearchListAPIView(APIView):
#     """
#     쿼리 파라미터로 type(검색 대상: person, team, corp)와 q(검색어)를 받아서 해당 모델을 검색한 결과를 반환.
#     Type 파라미터가 없는 경우, 기본적으로 person 모델을 대상으로 검색
#     """
#     permission_classes = [AllowAny]
#
#     def get(self, request, *args, **kwargs):
#         search_type = request.query_params.get('type', 'person').lower()
#         query = request.query_params.get('q')
#
#         if not query:
#             queryset = Person.objects.all()
#             serializer = PersonCardListSerializer(queryset, many=True)
#         elif search_type == "person":
#             queryset = Person.objects.filter(name__icontains=query)
#             serializer = PersonCardListSerializer(queryset, many=True)
#         elif search_type == "team":
#             queryset = Team.objects.filter(name__icontains=query)
#             serializer = TeamListSerializer(queryset, many=True)
#         elif search_type in ["corp", "corporation"]:
#             queryset = Corporation.objects.filter(name__icontains=query)
#             serializer = CorpListSerializer(queryset, many=True)
#         else:
#             return Response(
#                 {"detail": "Invalid type. Allowed types: person, team, corp"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         return Response(serializer.data, status=status.HTTP_200_OK)



# Person의 소속 법인/팀, 자격증으로 검색
class PersonSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '')
        certificate = request.query_params.get('certificate')
        filter_corp = request.query_params.get('corp_id')
        filter_team = request.query_params.get('team_id')

        persons = Person.objects.all().order_by('name')

        if query:
            # 입력된 검색어의 띄어쓰기를 제거
            query_clean = query.replace(' ', '')
            # name 필드에서 띄어쓰기를 제거한 값을 clean_name으로 주석 처리 후 필터링
            persons = persons.annotate(
                clean_name=RemoveSpaces(F('name'))
            ).filter(clean_name__icontains=query_clean)
        if certificate:
            cert_clean = certificate.replace(' ', '')
            persons = persons.annotate(
                cert_no_space=RemoveSpaces(F('personal_info__p_info__certificates'))
            ).filter(cert_no_space__icontains=cert_clean)
        if filter_corp:
            persons = persons.filter(member_of_teams__corporation__c_id=filter_corp)
        if filter_team:
            persons = persons.filter(member_of_teams__t_id=filter_team)
        persons = persons.distinct()
        serializer = PersonCardListSerializer(persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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


# 특정 법인/팀의 하위 조직원들 모두 검색
class TeamSubMembersSearchAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        team_id = request.query_params.get('team_id')
        corp_id = request.query_params.get('corp_id')

        if team_id:
            try:
                team = Team.objects.get(t_id=team_id)
            except Team.DoesNotExist:
                return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
            team_ids = self.get_lower_team_ids(team)
        elif corp_id:
            try:
                corp = Corporation.objects.get(c_id=corp_id)
            except Corporation.DoesNotExist:
                return Response({"detail": "Corporation not found."}, status=status.HTTP_404_NOT_FOUND)
            team_ids = set()
            # corp.teams related_name로 해당 법인에 속한 모든 팀을 가져온 후, 하위 조직까지 재귀적으로 포함
            for team in corp.teams.all():
                team_ids.update(self.get_lower_team_ids(team))
        else:
            return Response(
                {"detail": "Either team_id or corp_id parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        persons = Person.objects.filter(member_of_teams__t_id__in=team_ids).distinct().order_by('name')
        serializer = PersonCardListSerializer(persons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_lower_team_ids(self, team_obj):
        ids = {team_obj.t_id}
        for child in team_obj.lower_teams.all():
            ids.update(self.get_lower_team_ids(child))
        return ids


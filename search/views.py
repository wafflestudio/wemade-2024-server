from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from person.models import Person
from company.models import Team, Corporation
from personCard.serializers import PersonCardListSerializer
from company.serializers import CorpListSerializer, TeamListSerializer


class SearchListAPIView(APIView):
    """
    쿼리 파라미터로 type(검색 대상: person, team, corp)와 q(검색어)를 받아서 해당 모델을 검색한 결과를 반환.
    Type 파라미터가 없는 경우, 기본적으로 person 모델을 대상으로 검색
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        search_type = request.query_params.get('type', 'person').lower()
        query = request.query_params.get('q')

        if not query:
            queryset = Person.objects.all()
            serializer = PersonCardListSerializer(queryset, many=True)
        elif search_type == "person":
            queryset = Person.objects.filter(name__icontains=query)
            serializer = PersonCardListSerializer(queryset, many=True)
        elif search_type == "team":
            queryset = Team.objects.filter(name__icontains=query)
            serializer = TeamListSerializer(queryset, many=True)
        elif search_type in ["corp", "corporation"]:
            queryset = Corporation.objects.filter(name__icontains=query)
            serializer = CorpListSerializer(queryset, many=True)
        else:
            return Response(
                {"detail": "Invalid type. Allowed types: person, team, corp"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(serializer.data, status=status.HTTP_200_OK)

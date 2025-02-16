from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny

from person.models import Person, PersonalInfo, PersonalHistory
from .serializers import *
from .paginations import *
from .permissions import *


# 검색 페이지에서 모든 사람 정보 불러오기
class PersonCardListAPIView(ListCreateAPIView):
    serializer_class = PersonCardListSerializer
    pagination_class = PersonCardListPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Person.objects.all()


# 사람 이름을 query로 받아 검색하기
class PersonCardSearchListAPIView(ListAPIView):
    serializer_class = PersonCardListSerializer
    pagination_class = PersonCardListPagination
    permission_classes =  [AllowAny]

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if not name:
            return Person.objects.all()
        return Person.objects.filter(name__icontains=name)


# 검색 페이지 우측 특정한 사람 공개 정보 불러오기
class PersonCardListDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardListDetailSerializer
    permission_classes =  [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get('p_id'))
        return Response(self.get_serializer(person).data, status=200)


# 개인정보 업데이트
class PersonalInfoUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoUpdateSerializer
    lookup_field = 'person__p_id'
    lookup_url_kwarg = 'p_id'
    permission_classes = [IsOwnerOrHRTeam]


# 직무 업데이트 (HR Team) + 직무 히스토리 생성
class PersonRolesUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonRolesUpdateSerializer
    lookup_field = 'p_id'  # URL에서 p_id를 사용해 Person을 조회
    permission_classes = [IsHRTeam]


# 인사카드 조회
class PersonCardDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardDetailSerializer
    permission_classes = [IsOwnerOrHRTeamOrTeamLeader]

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get('p_id'))
        self.check_object_permissions(request, person)
        return Response(self.get_serializer(person).data, status=200)


# 직무 히스토리 정보 불러오기
class PersonalHistoryListAPIView(ListAPIView):
    serializer_class = PersonalHistorySerializer
    permission_classes = [IsOwnerOrHRTeamOrTeamLeader]

    def get_queryset(self):
        p_id = self.kwargs.get('p_id')
        self.check_object_permissions(request, person)
        return PersonalHistory.objects.filter(person__p_id=p_id)


# 직무 히스토리 내 직무 설명(job description) 수정하기
class PersonalHistoryUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = PersonalHistoryUpdateSerializer
    permission_classes = [IsOwnerOrHRTeam]

    def get_object(self):
        p_id = self.kwargs.get('p_id')
        person = get_object_or_404(Person, p_id=p_id)
        self.check_object_permissions(self.request, person)

        # history_id는 요청 데이터나 쿼리 파라미터에서 전달받음
        history_id = self.request.data.get('history_id') or self.request.query_params.get('history_id')
        if not history_id:
            raise NotFound("history_id가 제공되지 않았습니다.")

        qs = person.personal_histories.all()
        obj = get_object_or_404(qs, id=history_id)

        return obj


 # 직무 히스토리 삭제하기 (HR Team)
class PersonalHistoryDeleteAPIView(DestroyAPIView):
    serializer_class = PersonalHistorySerializer
    permission_classes = [IsHRTeam]

    def get_object(self):
        p_id = self.kwargs.get('p_id')
        person = get_object_or_404(Person, p_id=p_id)
        self.check_object_permissions(self.request, person)

        # history_id는 요청 데이터나 쿼리 파라미터에서 전달받음
        history_id = self.request.data.get('history_id') or self.request.query_params.get('history_id')
        if not history_id:
            raise NotFound("history_id가 제공되지 않았습니다.")

        qs = person.personal_histories.all()
        obj = get_object_or_404(qs, id=history_id)

        return obj


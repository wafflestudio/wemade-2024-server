from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from person.models import Person, PersonalInfo, PersonalHistory
from .serializers import *
from .paginations import *


class PersonCardListAPIView(ListCreateAPIView):
    serializer_class = PersonCardListSerializer
    pagination_class = PersonCardListPagination

    def get_queryset(self):
        return Person.objects.all()


class PersonCardSearchListAPIView(ListAPIView):
    serializer_class = PersonCardListSerializer
    pagination_class = PersonCardListPagination

    def get_queryset(self):
        name = self.request.query_params.get('name')
        if not name:
            return Person.objects.all()
        return Person.objects.filter(name__icontains=name)


class PersonCardListDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardListDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get('p_id'))
        return Response(self.get_serializer(person).data, status=200)


class PersonCardDetailAPIView(RetrieveAPIView):
    serializer_class = PersonCardDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get('p_id'))
        return Response(self.get_serializer(person).data, status=200)


class PersonalInfoUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PersonalInfo.objects.all()
    serializer_class = PersonalInfoUpdateSerializer
    lookup_field = 'person__p_id'
    lookup_url_kwarg = 'p_id'


class PersonRolesUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonRolesUpdateSerializer
    lookup_field = 'p_id'  # URL에서 p_id를 사용해 Person을 조회


class PersonalHistoryListAPIView(ListAPIView):
    serializer_class = PersonalHistorySerializer

    def get_queryset(self):
        p_id = self.kwargs.get('p_id')
        return PersonalHistory.objects.filter(person__p_id=p_id)


class PersonalHistoryUpdateAPIView(RetrieveUpdateAPIView):
    serializer_class = PersonalHistoryUpdateSerializer

    def get_object(self):
        p_id = self.kwargs.get('p_id')
        history_id = self.request.data.get('history_id') or self.request.query_params.get('history_id')
        if not history_id:
            raise NotFound("history_id가 제공되지 않았습니다.")
        person = get_object_or_404(Person, p_id=p_id)
        qs = person.personal_histories.all()
        obj = get_object_or_404(qs, id=history_id)
        return obj


class PersonalHistoryDeleteAPIView(DestroyAPIView):
    serializer_class = PersonalHistorySerializer

    def get_object(self):
        p_id = self.kwargs.get('p_id')
        # history_id는 요청 데이터나 쿼리 파라미터에서 전달받음
        history_id = self.request.data.get('history_id') or self.request.query_params.get('history_id')
        if not history_id:
            raise NotFound("history_id가 제공되지 않았습니다.")
        person = get_object_or_404(Person, p_id=p_id)
        qs = person.personal_histories.all()
        obj = get_object_or_404(qs, id=history_id)
        return obj


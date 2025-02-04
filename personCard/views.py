from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from person.models import Person, PersonalInfo
from .serializers import *
from .paginations import *


class PersonCardListAPI(ListCreateAPIView):
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


class PersonCardListDetailAPI(RetrieveAPIView):
    serializer_class = PersonCardListDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get('p_id'))
        return Response(self.get_serializer(person).data, status=200)


class PersonCardDetailAPI(RetrieveAPIView):
    serializer_class = PersonCardDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        person = get_object_or_404(Person, p_id=kwargs.get('p_id'))
        return Response(self.get_serializer(person).data, status=200)


class PersonCardUpdateAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = PersonCardUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        personal_info = get_object_or_404(PersonalInfo, p_id=kwargs.get('p_id'))
        return Response(self.get_serializer(personal_info).data, status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)

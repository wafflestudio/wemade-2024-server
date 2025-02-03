from django.shortcuts import render
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response

from person.models import Person, PersonalInfo
from .serializers import *
from .paginations import *

class PersonCardListAPI(ListCreateAPIView):
    serializer_class = PersonCardListSerializer
    pagination_class = PersonCardListPagination
    #authentication_classes = []

    def get_queryset(self):
        # Fetch all Person objects along with their associated Account emails
        return Person.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        # 일단은 email 정보만 return. 이후 role 만들면 role도 return할 예정.
        # Prepare data with names and associated email addresses
        data = [
            {
                "p_id": person.p_id,
                "name": person.name,
                "email": Account.objects.filter(p_id=person).values_list('email', flat=True).first(),
                "corporation": "",
                "team": "",
                "role": "",
            }
            for person in page
        ]

        return self.get_paginated_response(data)


class PersonCardSearchListAPIView(ListAPIView):
    serializer_class = PersonCardListSerializer
    pagination_class = PersonCardListPagination

    # 현재 => 이름으로 검색. 추후 corporation/team/role 단위 검색 만들 예정
    def get_queryset(self):
        name = self.request.query_params.get('name')

        if not name:
            # name 파라미터가 없을 경우, 모든 Person 반환
            return Person.objects.all()

        # 이름이 부분 일치하는 Person 객체 반환
        return Person.objects.filter(name__icontains=name)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        # Prepare data with names and associated email addresses
        data = [
            {
                "p_id": person.p_id,
                "name": person.name,
                "email": Account.objects.filter(p_id=person).values_list('email', flat=True).first(),
                "corporation": "",
                "team": "",
                "role": "",
            }
            for person in page
        ]

        return self.get_paginated_response(data)


class PersonCardListDetailAPI(RetrieveAPIView):
    serializer_class = PersonCardListDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get p_id from the request data
        p_id = kwargs.get('p_id')

        if not p_id:
            return Response({"error": "p_id is required"}, status=400)

        try:
            # Fetch the Person object
            person = Person.objects.get(p_id=p_id)
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=404)

        # Fetch related PersonalInfo and Account data
        personal_info = PersonalInfo.objects.filter(p_id=person).first()
        accounts = Account.objects.filter(p_id=person)

        # Filter p_info for type == 'certificate'
        filtered_p_info = []
        if personal_info and personal_info.p_info:
            filtered_p_info = [
                item for item in personal_info.p_info
                if item.get("type") == "certificate"
            ]

        # Prepare response data
        response_data = {
            "name": person.name,
            "phone_number": personal_info.main_phone_number if personal_info else None,
            "info": filtered_p_info,
            "emails": [account.email for account in accounts]
        }

        return Response(response_data, status=200)


class PersonCardDetailAPI(RetrieveAPIView):
    serializer_class = PersonCardDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get p_id from the request data
        p_id = kwargs.get('p_id')

        if not p_id:
            return Response({"error": "p_id is required"}, status=400)

        try:
            # Fetch the Person object
            person = Person.objects.get(p_id=p_id)
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=404)

        # Fetch related PersonalInfo and Account data
        personal_info = PersonalInfo.objects.filter(p_id=person.p_id).first()
        accounts = Account.objects.filter(p_id=person.p_id)

        # Prepare response data
        response_data = {
            "name": person.name,
            "phone_number": personal_info.phone_number if personal_info else None,
            "info": personal_info.p_info if personal_info else None,
            "emails": [account.email for account in accounts]
        }

        return Response(response_data, status=200)


class PersonCardUpdateAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = PersonCardUpdateSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get p_id from the URL kwargs
        p_id = kwargs.get('p_id')

        if not p_id:
            return Response({"error": "p_id is required"}, status=400)

        try:
            # Fetch the Person object
            person = Person.objects.get(p_id=p_id)
        except Person.DoesNotExist:
            return Response({"error": "Person not found"}, status=404)

        try:
            # Fetch the related PersonalInfo object
            personal_info = PersonalInfo.objects.get(p_id=person.p_id)
        except PersonalInfo.DoesNotExist:
            return Response({"error": "PersonalInfo not found"}, status=404)

        # Fetch related Account data
        accounts = Account.objects.filter(p_id=person.p_id)

        # Prepare response data
        response_data = {
            "name": person.name,
            "phone_number": personal_info.phone_number if personal_info else None,
            "info": personal_info.p_info if personal_info else None,
            "emails": [account.email for account in accounts],
        }

        return Response(response_data, status=200)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # def destroy(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     self.perform_destroy(instance)
    #     return Response(status=status.HTTP_204_NO_CONTENT)
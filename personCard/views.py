from django.shortcuts import render
from person import Person, PersonInfo
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView

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
                "email": Account.objects.filter(p_id=person).values_list('email', flat=True).first()
                "corporation": "",
                "team": "",
                "role": "",
            }
            for person in page
        ]

        return self.get_paginated_response(data)


# class  PersonCardSearchListAPIView(ListAPIView):
#     serializer_class = PersonCardListSerializer
#     pagination_class = PersonCardListPagination
#
#     def get_queryset(self):
#         #corporation - team 구조 가정 (조직 밑에 조직 밑에 조직 구조 고려 필요)
#         corporation = self.request.query_params.get('corporation')
#         team = self.request.query_params.get('team')
#
#         return Person.objects.filter()

class PersonCardListDetailAPI(RetrieveAPIView):
    serializer_class = PersonCardListDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get p_id from the request data
        p_id = request.data.get('p_id')

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
            "phone_number": personal_info.phone_number if personal_info else None,
            "info": filtered_p_info,
            "emails": [account.email for account in accounts]
        }

        return Response(response_data, status=200)


class PersonCardDetailAPI(RetrieveAPIView):
    serializer_class = PersonCardDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        # Get p_id from the request data
        p_id = request.data.get('p_id')

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

        # Prepare response data
        response_data = {
            "name": person.name,
            "phone_number": personal_info.phone_number if personal_info else None,
            "info": personal_info.p_info if personal_info else None,
            "emails": [account.email for account in accounts]
        }

        return Response(response_data, status=200)


class PersonCardUpdateDestroyAPI(RetrieveUpdateDestroyAPIView):
    serializer_class = PersonCardUpdateSerializer

    def get_object(self):
        # Get p_id from the request data
        p_id = self.request.data.get('p_id')

        if not p_id:
            raise ValueError("p_id is required")

        try:
            # Fetch the related PersonalInfo object
            person = Person.objects.get(p_id=p_id)
            personal_info = PersonalInfo.objects.get(p_id=person)
        except (Person.DoesNotExist, PersonalInfo.DoesNotExist):
            raise ValueError("PersonalInfo not found")

        return personal_info

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAdminUser
from .models import PersonCardColumns, EmailDomain
from .serializers import PersonCardColumnsSerializer, EmailDomainSerializer


# PersonCardColumns 관련 뷰
class PersonCardColumnsCreateAPIView(CreateAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    #permission_classes = [IsAdminUser]


class PersonCardColumnsListAPIView(ListAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    #permission_classes = [IsAdminUser]


class PersonCardColumnsUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    #permission_classes = [IsAdminUser]
    lookup_field = 'pk'  # 기본 primary key 사용


# EmailDomain 관련 뷰
class EmailDomainCreateAPIView(CreateAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    #permission_classes = [IsAdminUser]


class EmailDomainListAPIView(ListAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    #permission_classes = [IsAdminUser]


class EmailDomainUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    #permission_classes = [IsAdminUser]
    lookup_field = 'pk'

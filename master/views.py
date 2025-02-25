from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from personCard.models import PersonCardColumns
from oauth.models import EmailDomain
from .serializers import PersonCardColumnsSerializer, EmailDomainSerializer
from company.permissions import IsMasterHRTeam


# PersonCardColumns 관련 뷰
class PersonCardColumnsCreateAPIView(CreateAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    permission_classes = [IsMasterHRTeam]


class PersonCardColumnsListAPIView(ListAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    permission_classes = [IsMasterHRTeam]


class PersonCardColumnsUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    permission_classes = [IsMasterHRTeam]
    lookup_field = 'pk'  # 기본 primary key 사용


# EmailDomain 관련 뷰
class EmailDomainCreateAPIView(CreateAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    permission_classes = [IsMasterHRTeam]


class EmailDomainListAPIView(ListAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    permission_classes = [IsMasterHRTeam]


class EmailDomainUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    permission_classes = [IsMasterHRTeam]
    lookup_field = 'pk'

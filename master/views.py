from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveUpdateDestroyAPIView,
)
from personCard.models import PersonCardColumns
from oauth.models import EmailDomain
from .serializers import PersonCardColumnsSerializer, EmailDomainSerializer
from company.permissions import IsMasterHRTeam
from drf_yasg.utils import swagger_auto_schema


# PersonCardColumns 관련 뷰
@swagger_auto_schema(
    operation_summary="인사카드 Column 생성",
)
class PersonCardColumnsCreateAPIView(CreateAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    permission_classes = [IsMasterHRTeam]

@swagger_auto_schema(
    operation_summary="인사카드 Column 리스트",
)
class PersonCardColumnsListAPIView(ListAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    permission_classes = [IsMasterHRTeam]

@swagger_auto_schema(
    operation_summary="인사카드 Column 수정",
)
class PersonCardColumnsUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = PersonCardColumns.objects.all()
    serializer_class = PersonCardColumnsSerializer
    permission_classes = [IsMasterHRTeam]
    lookup_field = "pk"  # 기본 primary key 사용


# EmailDomain 관련 뷰
@swagger_auto_schema(
    operation_summary="Email Domain 생성",
)
class EmailDomainCreateAPIView(CreateAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    permission_classes = [IsMasterHRTeam]

@swagger_auto_schema(
    operation_summary="Email Domain 리스트",
)
class EmailDomainListAPIView(ListAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    permission_classes = [IsMasterHRTeam]

@swagger_auto_schema(
    operation_summary="Email Domain 수정",
)
class EmailDomainUpdateAPIView(RetrieveUpdateDestroyAPIView):
    queryset = EmailDomain.objects.all()
    serializer_class = EmailDomainSerializer
    permission_classes = [IsMasterHRTeam]
    lookup_field = "pk"

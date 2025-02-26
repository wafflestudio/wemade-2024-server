from django.urls import path
from .views import *

urlpatterns = [
    # 인사카드 Column 관련 Endpoint
    path(
        "create/personCard/columns/",
        PersonCardColumnsCreateAPIView.as_view(),
        name="personcard-columns-create",
    ),
    path(
        "list/personCard/columns/",
        PersonCardColumnsListAPIView.as_view(),
        name="personcard-columns-list",
    ),
    path(
        "update/personCard/columns/<int:pk>/",
        PersonCardColumnsUpdateAPIView.as_view(),
        name="personcard-columns-update",
    ),
    # Email Domain 관련 Endpoint
    path(
        "create/email/", EmailDomainCreateAPIView.as_view(), name="email-domain-create"
    ),
    path("list/email/", EmailDomainListAPIView.as_view(), name="email-domain-list"),
    path(
        "update/email/<int:pk>/",
        EmailDomainUpdateAPIView.as_view(),
        name="email-domain-update",
    ),
]

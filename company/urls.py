from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    # Corporation
    path('corp/list/', CorpListAPIView.as_view(), name='corp-list'),  # list all corporations
    path('corp/<int:c_id>/update/', CorpUpdateDeleteAPIView.as_view(), name='corp-update'),  # update corporation info
    path('corp/<int:c_id>/delete/', CorpUpdateDeleteAPIView.as_view(), name='corp-delete'),  # delete corporation info
    path('corp/<int:c_id>/', CorpDetailAPIView.as_view(), name='corp-detail'),  # get specific corporation info
    path('corp/create/', CorpCreateAPIView.as_view(), name='corp-create'),  # create new corporation

    # Team
    path('team/list/', TeamListAPIView.as_view(), name='team-list'),  # list all teams
    path('team/<int:t_id>/update/', TeamUpdateDeleteAPIView.as_view(), name='team-update'),  # update team info
    path('team/<int:t_id>/delete/', TeamUpdateDeleteAPIView.as_view(), name='team-delete'),  # delete team info
    path('team/<int:t_id>/', TeamDetailAPIView.as_view(), name='team-detail'),  # get specific team info
    path('team/create/', TeamCreateAPIView.as_view(), name='team-create'),  # create new team
]

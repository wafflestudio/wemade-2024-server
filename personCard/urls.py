from django.contrib import admin
from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    path('list/<int:p_id>/', PersonCardListDetailAPIView.as_view(), name='person-card-list-detail'),
    path('list/', PersonCardListAPIView.as_view(), name='person-card-list'),
    path('search/',  PersonCardSearchListAPIView.as_view(), name='person-card-search'), #query로 받도록
    path('<int:p_id>/update/', PersonCardUpdateAPIView.as_view(), name='person-card-update'),
    path('<int:p_id>/', PersonCardDetailAPIView.as_view(), name='person-card-detail'),
]
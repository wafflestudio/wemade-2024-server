from django.contrib import admin
from django.urls import path, include
from rest_framework import urls
from .views import *

urlpatterns = [
    path('list/', PersonCardListAPI.as_view(), name='person-card-list'),
    path('list/<int:p_id>', name='person-card-list-detail'),
    #path('search/',  PersonCardSearchListAPIView.as_view(), name='person-card-search'), #query로 받도록
    path('<int:p_id>/', PersonCardDetailAPI.as_view(), name='person-card-detail'),
    path('<int:p_id>/update/', PersonCardUpdateDestroyAPI.as_view(), name='person-card-update'),
]
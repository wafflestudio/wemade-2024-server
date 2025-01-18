from django.shortcuts import render
from person import Person, PersonInfo
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView

class PersonCardListAPI(ListCreateAPIView):


class PersonCardDetailAPI(RetrieveAPIView):


class PersonCardUpdateDestroyAPI(RetrieveUpdateDestroyAPIView):

# Create your views here.

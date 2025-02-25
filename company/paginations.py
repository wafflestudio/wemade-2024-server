from rest_framework.pagination import CursorPagination
from .models import *


class CorpListPagination(CursorPagination):
    page_size = 10
    ordering = 'c_id'


class TeamListPagination(CursorPagination):
    page_size = 10
    ordering = 't_id'

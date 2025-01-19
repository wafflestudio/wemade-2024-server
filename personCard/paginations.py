from rest_framework.pagination import CursorPagination
from person import Person, PersonInfo


class PersonCardListPagination(CursorPagination):
    page_size = 10
    ordering = 'p_id'
    
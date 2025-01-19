from rest_framework.pagination import CursorPagination
from person.models import Person, PersonalInfo


class PersonCardListPagination(CursorPagination):
    page_size = 10
    ordering = 'p_id'

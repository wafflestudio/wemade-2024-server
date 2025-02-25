from rest_framework.pagination import CursorPagination


class PersonCardListPagination(CursorPagination):
    page_size = 10
    ordering = "p_id"

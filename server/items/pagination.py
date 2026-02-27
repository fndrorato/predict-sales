from rest_framework.pagination import CursorPagination


class SingleItemCursorPagination(CursorPagination):
    page_size = 1
    ordering = 'code'

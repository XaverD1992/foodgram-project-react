from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class CustomizedPaginator(PageNumberPagination):
    """Пагинатор с возможностью устанавливать кол-во объектов на страницу"""
    page_size_query_param = 'limit'
    page_size = settings.PAGE_SIZE

from rest_framework.pagination import PageNumberPagination

class PerfumePagination(PageNumberPagination):
    page_size = 8  # number of perfumes per page
    page_size_query_param = 'page_size'  # allow client to change page size via query param
    max_page_size = 50  # maximum page size

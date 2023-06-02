from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PageNumberWithPageSizePagination(PageNumberPagination):
    page_size_query_param = "size"

    def get_paginated_response(self, data: list[dict[str, Any]]) -> Response:
        return Response({"count": self.page.paginator.count, "results": data})

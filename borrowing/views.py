
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer
)


def params_to_ints(qs):
    return [int(str_id) for str_id in qs.split(",")]


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset

        if self.request.user.is_staff:
            users = self.request.query_params.get("users")
            if users:
                user_ids = params_to_ints(users)
                queryset = queryset.filter(user_id__in=user_ids)
        else:
            queryset = queryset.filter(user_id=self.request.user.id)

        queryset = queryset.filter(actual_return_date=None)

        return queryset

from rest_framework.viewsets import ModelViewSet

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer
)


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        if not self.request.user.is_staff:
            return queryset.filter(user_id=self.request.user.id)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        """Adds user to borrow instance and decreasing book inventory by 1"""
        book = Book.objects.get(id=self.request.data["book_id"])
        book.inventory -= 1
        book.save()
        serializer.save(user_id=self.request.user)

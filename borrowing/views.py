from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from book.models import Book
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer, BorrowingReturnSerializer
)


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        queryset = Borrowing.objects.all()
        if not self.request.user.is_staff:
            return queryset.filter(user_id=self.request.user.id)
        return queryset

    @action(
        methods=["PATCH"],
        detail=True,
        url_path="return-book",
        permission_classes=[IsAuthenticated],)
    def return_book(self, request, pk=None):
        borrowing = Borrowing.objects.get(id=pk)
        book = Book.objects.get(id=borrowing.book_id.id)
        if borrowing.actual_return_date:
            raise ValidationError(f"You already return the {book.title}")
        book.inventory += 1
        book.save()
        borrowing.actual_return_date = timezone.datetime.now().date()
        serializer = self.get_serializer(borrowing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        """Adds user to borrow instance and decreasing book inventory by 1"""
        book = Book.objects.get(id=self.request.data["book_id"])
        book.inventory -= 1
        book.save()
        serializer.save(user_id=self.request.user)

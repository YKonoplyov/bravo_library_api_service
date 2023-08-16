from django.db.models import Q
from django.shortcuts import redirect
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import ModelViewSet

from book.models import Book
from borrowing.models import Borrowing
from borrowing.permissions import TGBotActivated
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer
)
from borrowing.signals import borrowing_created


def params_to_ints(qs):
    return [int(str_id) for str_id in qs.split(",")]


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated, TGBotActivated]

    def get_queryset(self):
        """Return queryset of borrowings of non-staff user.
        For admins returns all borrowings. Allows to filter
        borrowings by user id and it status active(?is_active=1)
        and not active(?is_active=0)"""
        queryset = self.queryset
        users = self.request.query_params.get("users")

        if not self.request.user.is_staff:
            queryset = queryset.filter(user_id=self.request.user)

        if users:
            queryset = queryset.filter(user_id__in=users)

        is_active = self.request.query_params.get("is_active")
        if is_active:
            is_active = bool(int(is_active))
            if is_active:
                queryset = queryset.filter(actual_return_date=None)

            else:
                queryset = queryset.filter(~Q(actual_return_date=None))

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return redirect(reverse("payment:session-create"), status=status.HTTP_307_TEMPORARY_REDIRECT, headers=headers)

    def perform_create(self, serializer):
        """Adds user to borrow instance and decreasing book inventory by 1"""
        book = Book.objects.get(id=self.request.data["book_id"])
        book.inventory -= 1
        book.save()
        serializer.save(user_id=self.request.user)

        borrowing_created.send(sender=Borrowing, instance=self.queryset)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "users",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by users id (ex. ?users=2,5)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

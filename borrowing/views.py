from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer
)


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingDetailSerializer

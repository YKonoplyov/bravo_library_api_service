from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from borrowing.models import Borrowing
from borrowing.permissions import TGBotActivated
from borrowing.serializers import BorrowingSerializer, BorrowingDetailSerializer


class BorrowingViewSet(ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated, TGBotActivated]

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

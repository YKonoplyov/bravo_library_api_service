from django.views import View
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from borrowing.models import Borrowing

OVERDUE_CONST = 2


class PaymentView(View):
    def get(self, request, borrowing_id):
        borrowing = get_object_or_404(Borrowing, id=borrowing_id)
        return JsonResponse(
            {"money_to_pay": self.calculate_money_to_pay(borrowing)}
        )

    @staticmethod
    def calculate_money_to_pay(borrowing):
        if not borrowing.actual_return_date:
            return 0

        if borrowing.actual_return_date <= borrowing.expected_return_date:
            actual_return_date = (
                borrowing.expected_return_date - borrowing.actual_return_date
            ).days
            days_in_usage = borrowing.actual_return_date - actual_return_date
            book_daily_fee = borrowing.book_id.daily_fee
            total_price = book_daily_fee * days_in_usage
            return total_price

        days_late = (
            borrowing.actual_return_date - borrowing.expected_return_date
        ).days
        book_daily_fee = borrowing.book_id.daily_fee
        total_price = (book_daily_fee * OVERDUE_CONST * days_late) + (
            borrowing.expected_return_date - borrowing.borrow_date
        ) * book_daily_fee
        return total_price

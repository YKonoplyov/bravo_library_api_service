from rest_framework import serializers

from book.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = "__all__"
        read_only_fields = ("id", "image")


class BookImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = ("id", "image")

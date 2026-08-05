from rest_framework import serializers
from .models import Store, Product, Review


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = [
            "id",
            "name",
            "description",
        ]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "store",
            "name",
            "description",
            "price",
            "stock",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "product",
            "buyer",
            "rating",
            "comment",
            "verified",
            "created_at",
        ]

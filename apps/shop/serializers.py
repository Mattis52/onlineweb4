# -*- coding: utf-8 -*-

from apps.authentication.models import OnlineUser as User
from apps.gallery.serializers import ResponsiveImageSerializer
from apps.payment.models import PaymentTransaction
from apps.inventory.models import Item
from apps.shop.models import Order, OrderLine

from rest_framework import serializers


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'object_id', 'quantity',
        )


class OrderLineSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True)

    def create(self, validated_data):
        order_list = validated_data.pop("orders")
        order_line = OrderLine.objects.create(**validated_data)
        while len(order_list) > 0:
            order_data = order_list.pop()
            order = Order(order_line=order_line, **order_data)
            item = Item.objects.get(pk=order.object_id)
            order.content_object = item
            order.price = item.price
            order.save()

        order_line.pay()

        return order_line

    class Meta:
        model = OrderLine
        fields = (
            'user', 'orders',
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'pk', 'first_name', 'last_name', 'saldo',
        )


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = (
            'user', 'amount',
        )


class ItemSerializer(serializers.ModelSerializer):
    image = ResponsiveImageSerializer()

    class Meta:
        model = Item
        fields = (
            'pk', 'name', 'price', 'description', 'image',
        )

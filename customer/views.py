from django.shortcuts import render, redirect
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from userauths.models import User
from store.models import Product, Category, Cart, Tax, CartOrder, CartOrderItem, Coupon, Notification, Review, Wishlist
from store.serializer import ProductSerializer, CategorySerializer, CartSerializer, CartOrderSerializer, CartOrderItemSerializer, CouponSerializer, ReviewSerializer, WishlistSerializer

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.response import Response
from decimal import Decimal

import stripe
import requests


class OrdersAPIView(generics.ListAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)

        orders = CartOrder.objects.filter(buyer=user, payment_status="paid")
        return orders


class OrdersDetailAPIView(generics.RetrieveAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        user_id = self.kwargs['user_id']
        order_oid = self.kwargs['order_oid']

        user = User.objects.get(id=user_id)

        order = CartOrder.objects.get(
            buyer=user, payment_status="paid", oid=order_oid)
        return order


class WishlistCreateAPIView(generics.CreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        payload = request.data

        product_id = payload['product_id']
        user_id = payload['user_id']

        product = Product.objects.get(id=product_id)
        user = User.objects.get(id=user_id)

        wishlist = Wishlist.objects.filter(product=product, user=user)
        if wishlist:
            wishlist.delete()
            return Response({"message": "Removed From Wishlist"}, status=status.HTTP_200_OK)
        else:
            wishlist = Wishlist.objects.create(
                product=product,
                user=user,
            )
            return Response({"message": "Added To Wishlist"}, status=status.HTTP_201_CREATED)


class WishlistAPIView(generics.ListAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        user = User.objects.get(id=user_id)
        wishlist = Wishlist.objects.filter(user=user)
        return wishlist

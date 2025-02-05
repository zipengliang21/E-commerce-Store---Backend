from django.shortcuts import render

from store.models import Product, Category
from store.serializer import ProductSerializer, CategorySerializer

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

class CategoryListAPIView(generics.ListAPIView):
  queryset = Category.objects.all()
  serializer_class = CategorySerializer
  permission_classes = [AllowAny]

class ProductListAPIView(generics.ListAPIView):
  queryset = Product.objects.all()
  serializer_class = ProductSerializer
  permission_classes = [AllowAny]
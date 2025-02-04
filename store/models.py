from django.db import models

from django.utils.text import slugify
from userauths.models import User, Profile
from vendor.models import Vendor

from shortuuid.django_fields import ShortUUIDField

class Category(models.Model):
  title = models.CharField(max_length=100)
  image = models.FileField(upload_to='category', null=True, blank=True, default='category.jpg')
  active = models.BooleanField(default=True)
  slug = models.SlugField(unique=True)

  def __str__(self):
    return str(self.title)
  
  class Meta:
    verbose_name_plural = "Category"
    ordering = ['title']

class Product(models.Model):

  STATUS = (
      ("draft", "Draft"),
      ("disabled", "Disabled"),
      ("rejected", "Rejected"),
      ("in_review", "In Review"),
      ("published", "Published"),
  )
  title = models.CharField(max_length=100)
  image = models.FileField(upload_to='product', null=True, blank=True, default='product.jpg')
  description = models.TextField(null=True, blank=True)
  category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
  price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
  old_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
  shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
  stock_qty = models.PositiveIntegerField(default=1)
  in_stock = models.BooleanField(default=True)
  status = models.CharField(max_length=100, choices=STATUS, default="published")
  featured = models.BooleanField(default=False)
  views = models.PositiveIntegerField(default=0, null=True, blank=True)
  rating = models.IntegerField(default=0, null=True, blank=True)
  vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name="vendor")
  pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefghijklmnopqrstuvxyz")
  slug = models.SlugField(null=True, blank=True)
  date = models.DateTimeField(auto_now_add=True)

  def save(self, *args, **kwargs):
    if self.slug == "" or self.slug is None:
      self.slug = slugify(self.name)

    super(Product, self).save(*args, **kwargs)

  def __str__(self):
    return self.title
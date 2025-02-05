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
  
class Gallery(models.Model): 
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  image = models.FileField(upload_to="products", default="product.jpg")
  active = models.BooleanField(default=True)
  gid = ShortUUIDField(unique=True, length=10, alphabet="abcdefghijklmnopqrstuvxyz")

  def __str__(self):
    return self.product.title
  
  class Meta:
    verbose_name_plural = "Product Images"
  
class Specification(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  title = models.CharField(max_length=1000)
  content = models.CharField(max_length=1000)

  def __str__(self):
    return self.title

class Size(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  name = models.CharField(max_length=1000)
  price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00)

  def __str__(self):
    return self.name
  
class Color(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  name = models.CharField(max_length=1000)
  color_code = models.CharField(max_length=1000)

  def __str__(self):
    return self.name

class Cart(models.Model):
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
  qty = models.PositiveIntegerField(default=0, null=True, blank=True)
  price = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
  sub_total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
  shipping_amount = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
  service_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
  tax_fee = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
  total = models.DecimalField(decimal_places=2, max_digits=12, default=0.00, null=True, blank=True)
  country = models.CharField(max_length=100, null=True, blank=True)
  size = models.CharField(max_length=100, null=True, blank=True)
  color = models.CharField(max_length=100, null=True, blank=True)
  cart_id = models.CharField(max_length=1000, null=True, blank=True)
  date = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f'{self.cart_id} - {self.product.title}'
  
class CartOrder(models.Model):
    PAYMENT_STATUS = (
        ("paid", "Paid"),
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("cancelled", "Cancelled"),
    )

    ORDER_STATUS = (
        ("pending", "Pending"),
        ("fulfilled", "Fulfilled"),
        ("cancelled", "Cancelled"),
    )

    vendor = models.ManyToManyField(Vendor, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    sub_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    shipping_amount = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    tax_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)

    payment_status = models.CharField(choices=PAYMENT_STATUS, max_length=100, default="pending")
    order_status = models.CharField(max_length=100, choices=ORDER_STATUS, default="pending")

    # Discounts
    initial_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2, help_text="The original total before discounts")
    saved = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, null=True, blank=True, help_text="Amount saved by customer")

    # Personal Informations
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    email = models.CharField(max_length=1000, null=True, blank=True)
    mobile = models.CharField(max_length=1000, null=True, blank=True)

    # Shipping Address
    address = models.CharField(max_length=1000, null=True, blank=True)
    city = models.CharField(max_length=1000, null=True, blank=True)
    state = models.CharField(max_length=1000, null=True, blank=True)
    country = models.CharField(max_length=1000, null=True, blank=True)

    oid = ShortUUIDField(unique=True, length=10, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return self.oid
    
class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    qty = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    sub_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    shipping_amount = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    tax_fee = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    country = models.CharField(max_length=100, null=True, blank=True)

    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)

    # Coupons
    initial_total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    saved = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    oid = ShortUUIDField(unique=True, length=10, alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return self.oid
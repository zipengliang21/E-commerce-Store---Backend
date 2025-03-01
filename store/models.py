from django.db import models

from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save

from userauths.models import User, Profile
from vendor.models import Vendor

from shortuuid.django_fields import ShortUUIDField

RATING = (
    (1, "★☆☆☆☆"),
    (2, "★★☆☆☆"),
    (3, "★★★☆☆"),
    (4, "★★★★☆"),
    (5, "★★★★★"),
)


class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.FileField(
        upload_to='category',
        null=True,
        blank=True,
        default='category.jpg')
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
    image = models.FileField(
        upload_to='product',
        null=True,
        blank=True,
        default='product.jpg')
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    old_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    shipping_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)
    stock_qty = models.PositiveIntegerField(default=1)
    in_stock = models.BooleanField(default=True)
    status = models.CharField(
        max_length=100,
        choices=STATUS,
        default="published")
    featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0, null=True, blank=True)
    rating = models.IntegerField(default=0, null=True, blank=True)
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vendor")
    pid = ShortUUIDField(
        unique=True,
        length=10,
        max_length=20,
        alphabet="abcdefghijklmnopqrstuvxyz")
    slug = models.SlugField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.slug == "" or self.slug is None:
            self.slug = slugify(self.name)

        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    def product_rating(self):
        product_rating = Review.objects.filter(
            product=self).aggregate(
            avg_rating=models.Avg("rating"))
        return product_rating["avg_rating"]

    def rating_count(self):
        return Review.objects.filter(product=self).count()

    def save(self, *args, **kwargs):
        self.rating = self.product_rating()
        super(Product, self).save(*args, **kwargs)

    # Returns the gallery images linked to this product
    def gallery(self):
        gallery = Gallery.objects.filter(product=self)
        return gallery

    def specification(self):
        return Specification.objects.filter(product=self)

    def color(self):
        return Color.objects.filter(product=self)

    def order_count(self):
        return CartOrderItem.objects.filter(product=self).count()

    def size(self):
        return Size.objects.filter(product=self)


class Gallery(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.FileField(upload_to="products", default="product.jpg")
    active = models.BooleanField(default=True)
    gid = ShortUUIDField(
        unique=True,
        length=10,
        alphabet="abcdefghijklmnopqrstuvxyz")

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
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    qty = models.PositiveIntegerField(default=0, null=True, blank=True)
    price = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=0.00,
        null=True,
        blank=True)
    sub_total = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=0.00,
        null=True,
        blank=True)
    shipping_amount = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=0.00,
        null=True,
        blank=True)
    service_fee = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=0.00,
        null=True,
        blank=True)
    tax_fee = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=0.00,
        null=True,
        blank=True)
    total = models.DecimalField(
        decimal_places=2,
        max_digits=12,
        default=0.00,
        null=True,
        blank=True)
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
        ("Pending", "Pending"),
        ("Fulfilled", "Fulfilled"),
        ("Cancelled", "Cancelled"),
    )

    vendor = models.ManyToManyField(Vendor, blank=True)
    buyer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)

    sub_total = models.DecimalField(
        default=0.00, max_digits=12, decimal_places=2)
    shipping_amount = models.DecimalField(
        default=0.00, max_digits=12, decimal_places=2)
    tax_fee = models.DecimalField(
        default=0.00,
        max_digits=12,
        decimal_places=2)
    service_fee = models.DecimalField(
        default=0.00, max_digits=12, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)

    payment_status = models.CharField(
        choices=PAYMENT_STATUS,
        max_length=100,
        default="pending")
    order_status = models.CharField(
        max_length=100,
        choices=ORDER_STATUS,
        default="pending")

    # Discounts
    initial_total = models.DecimalField(
        default=0.00,
        max_digits=12,
        decimal_places=2,
        help_text="The original total before discounts")
    saved = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        null=True,
        blank=True,
        help_text="Amount saved by customer")

    # Personal Informations
    full_name = models.CharField(max_length=1000, null=True, blank=True)
    email = models.CharField(max_length=1000, null=True, blank=True)
    mobile = models.CharField(max_length=1000, null=True, blank=True)

    # Shipping Address
    address = models.CharField(max_length=1000, null=True, blank=True)
    city = models.CharField(max_length=1000, null=True, blank=True)
    state = models.CharField(max_length=1000, null=True, blank=True)
    country = models.CharField(max_length=1000, null=True, blank=True)

    stripe_session_id = models.CharField(
        max_length=1000, null=True, blank=True)

    oid = ShortUUIDField(
        unique=True,
        length=10,
        alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.oid

    def orderitem(self):
        return CartOrderItem.objects.filter(order=self)


class CartOrderItem(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    qty = models.PositiveIntegerField(default=0)
    price = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    sub_total = models.DecimalField(
        default=0.00, max_digits=12, decimal_places=2)
    shipping_amount = models.DecimalField(
        default=0.00, max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(
        default=0.00, max_digits=12, decimal_places=2)
    tax_fee = models.DecimalField(
        default=0.00,
        max_digits=12,
        decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    country = models.CharField(max_length=100, null=True, blank=True)

    size = models.CharField(max_length=100, null=True, blank=True)
    color = models.CharField(max_length=100, null=True, blank=True)

    # Coupons
    coupon = models.ManyToManyField("store.Coupon", blank=True)
    initial_total = models.DecimalField(
        default=0.00, max_digits=12, decimal_places=2)
    saved = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    oid = ShortUUIDField(
        unique=True,
        length=10,
        alphabet="abcdefghijklmnopqrstuvxyz")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.oid


class ProductFaq(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    question = models.CharField(max_length=1000)
    answer = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name_plural = "Product FAQs"

# Define a model for Reviews


class Review(models.Model):
    # A foreign key relationship to the User model with SET_NULL option,
    # allowing null and blank values
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True)

    # A foreign key relationship to the Product model with SET_NULL option,
    # allowing null and blank values, and specifying a related name
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="reviews")

    # Text field for the review content
    review = models.TextField()

    # Field for a reply with max length 1000, allowing null and blank values
    reply = models.CharField(null=True, blank=True, max_length=1000)

    # Integer field for rating with predefined choices
    rating = models.IntegerField(choices=RATING, default=None)

    # Boolean field for the active status
    active = models.BooleanField(default=False)

    # Many-to-many relationships with User model for helpful and not helpful
    # actions
    helpful = models.ManyToManyField(User, blank=True, related_name="helpful")
    not_helpful = models.ManyToManyField(
        User, blank=True, related_name="not_helpful")

    # Date and time field
    date = models.DateTimeField(auto_now_add=True)

    # Method to return a string representation of the object
    def __str__(self):
        if self.product:
            return self.product.title
        else:
            return "Review"

    class Meta:
        verbose_name_plural = "Reviews & Rating"
        ordering = ["-date"]

    # Method to get the rating value
    def get_rating(self):
        return self.rating

    def profile(self):
        return Profile.objects.get(user=self.user)

# Signal handler to update the product rating when a review is saved


@receiver(post_save, sender=Review)
def update_product_rating(sender, instance, **kwargs):
    if instance.product:
        instance.product.save()

# Define a model for Wishlist


class Wishlist(models.Model):
    # A foreign key relationship to the User model with CASCADE deletion
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    # A foreign key relationship to the Product model with CASCADE deletion,
    # specifying a related name
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlist")
    # Date and time field
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Wishlist"

    # Method to return a string representation of the object
    def __str__(self):
        if self.product.title:
            return self.product.title
        else:
            return "Wishlist"

# Define a model for Notification


class Notification(models.Model):
    # A foreign key relationship to the User model with CASCADE deletion
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    # A foreign key relationship to the Vendor model with CASCADE deletion
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    # A foreign key relationship to the CartOrder model with CASCADE deletion,
    # specifying a related name
    order = models.ForeignKey(
        CartOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    # A foreign key relationship to the CartOrderItem model with CASCADE
    # deletion, specifying a related name
    order_item = models.ForeignKey(
        CartOrderItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    # Is read Boolean Field
    seen = models.BooleanField(default=False)
    # Date and time field
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Notification"

    # Method to return a string representation of the object
    def __str__(self):
        if self.order:
            return self.order.oid
        else:
            return "Notification"

# Define a model for Coupon


class Coupon(models.Model):
    # A foreign key relationship to the Vendor model with SET_NULL option,
    # allowing null values, and specifying a related name
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.SET_NULL,
        null=True,
        related_name="coupon_vendor")
    # Many-to-many relationship with User model for users who used the coupon
    used_by = models.ManyToManyField(User, blank=True)
    # Fields for code, type, discount, redemption, date, and more
    code = models.CharField(max_length=1000)
    # type = models.CharField(max_length=100, choices=DISCOUNT_TYPE, default="Percentage")
    discount = models.IntegerField(default=1)
    # redemption = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    # Method to return a string representation of the object
    def __str__(self):
        return self.code


class Tax(models.Model):
    country = models.CharField(max_length=100)
    rate = models.IntegerField(
        default=5,
        help_text="Numbers added here are in percentage e.g. 5%")
    active = models.BooleanField(default=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.country

    class Meta:
        verbose_name_plural = "Taxes"
        ordering = ["country"]

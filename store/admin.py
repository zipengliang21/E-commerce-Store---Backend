from django.contrib import admin
from store.models import Product, Category, Gallery, Specification, Size, Color, Cart, CartOrder, CartOrderItem, Review, Notification, Coupon

class GalleryInline(admin.TabularInline):
  model = Gallery
  extra = 0

class SpecificationInline(admin.TabularInline):
  model = Specification
  extra = 0

class SizeInline(admin.TabularInline):
  model = Size
  extra = 0

class ColorInline(admin.TabularInline):
  model = Color
  extra = 0

class ProductAdmin(admin.ModelAdmin):
  list_display = ["title", "price", "category","shipping_amount", "stock_qty", "in_stock", "vendor", "featured"]
  list_editable = ["featured"]
  list_filter = ["date"]
  search_fields = ["title"]
  inlines = [GalleryInline, SpecificationInline, SizeInline, ColorInline]

class ProductReviewAdmin(admin.ModelAdmin):
  list_editable = ['active']
  list_editable = ['active']
  list_display = ['user', 'product', 'review', 'reply' ,'rating', 'active']

class NotificationAdmin(admin.ModelAdmin):
  list_editable = ['seen']
  list_display = ['order', 'seen', 'user', 'vendor', 'date']

class CouponAdmin(admin.ModelAdmin):
  list_editable = ['code', 'active', ]
  list_display = ['vendor' ,'code', 'discount', 'active', 'date']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)

admin.site.register(Cart)
admin.site.register(CartOrder)
admin.site.register(CartOrderItem)

admin.site.register(Review, ProductReviewAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Coupon, CouponAdmin)


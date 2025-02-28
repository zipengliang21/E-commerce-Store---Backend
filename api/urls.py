from django.urls import path

from userauths import views as userauths_views
from store import views as store_views
from customer import views as customer_views
from vendor import views as vendor_views

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user/token/', userauths_views.MyTokenObtainPairView.as_view()),
    path('user/token/refresh/', TokenRefreshView.as_view()),
    path('user/register/', userauths_views.RegisterView.as_view()),
    path('user/password-reset/<email>/',
         userauths_views.PasswordResetEmailVerifyView.as_view()),
    path('user/password-change/', userauths_views.PasswordChangeView.as_view()),
    path('user/profile/<user_id>/', userauths_views.ProfileView.as_view()),

    # Store Endpoints
    path('category/', store_views.CategoryListAPIView.as_view()),
    path('products/', store_views.ProductListAPIView.as_view()),
    path('products/<slug>/', store_views.ProductDetailAPIView.as_view()),
    path('cart-view/', store_views.CartAPIView.as_view()),
    path('cart-list/<str:cart_id>/<int:user_id>/',
         store_views.CartListView.as_view()),
    path('cart-list/<str:cart_id>/', store_views.CartListView.as_view()),
    path('cart-detail/<str:cart_id>/', store_views.CartDetailView.as_view()),
    path('cart-detail/<str:cart_id>/<int:user_id>/',
         store_views.CartDetailView.as_view()),
    path('cart-delete/<str:cart_id>/<int:item_id>/<int:user_id>/',
         store_views.CartItemDeleteView.as_view()),
    path('cart-delete/<str:cart_id>/<int:item_id>/',
         store_views.CartItemDeleteView.as_view()),
    path('create-order/', store_views.CreateOrderView.as_view()),
    path('checkout/<order_oid>/', store_views.CheckoutView.as_view()),
    path('coupon/', store_views.CouponAPIView.as_view()),
    path('reviews/<product_id>/', store_views.ReviewListAPIView.as_view()),
    path('create-review/', store_views.ReviewRatingAPIView.as_view()),
    path('search/', store_views.SearchProductsAPIView.as_view()),

    # Payment Endpoints
    path('stripe-checkout/<order_oid>/',
         store_views.StripeCheckoutView.as_view()),
    path('payment-success/<order_oid>/',
         store_views.PaymentSuccessView.as_view()),

    # Customer Endpoints
    path('customer/orders/<int:user_id>/',
         customer_views.OrdersAPIView.as_view()),
    path('customer/order/<int:user_id>/<order_oid>/',
         customer_views.OrdersDetailAPIView.as_view()),
    path('customer/wishlist/create/',
         customer_views.WishlistCreateAPIView.as_view()),
    path('customer/wishlist/<user_id>/',
         customer_views.WishlistAPIView.as_view()),
    path('customer/notification/<user_id>/',
         customer_views.CustomerNotificationView.as_view()),
    path('customer/notification/<user_id>/<noti_id>/',
         customer_views.MarkNotificationAsSeen.as_view()),
    path('customer/setting/<user_id>/',
         customer_views.CustomerUpdateView.as_view()),

    # Vendor Dashboard
    path('vendor/stats/<vendor_id>/',
         vendor_views.DashboardStatsAPIView.as_view()),
    path('vendor-orders-chart/<vendor_id>/',
         vendor_views.MonthlyOrderChartAPIView),
    path('vendor-product-chart/<vendor_id>/',
         vendor_views.MonthlyProductsChartAPIView),
    path('vendor/products/<vendor_id>/', vendor_views.ProductsAPIView.as_view()),
    path('vendor/orders/<vendor_id>/', vendor_views.OrdersAPIView.as_view()),
    path('vendor/order/<vendor_id>/<order_oid>/',
         vendor_views.OrderDetailAPIView.as_view()),
    path('vendor/revenue/<vendor_id>/<order_oid>/',
         vendor_views.RevenueAPIView.as_view()),
]

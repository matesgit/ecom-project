from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('', home, name='home'),
    path('api/brands/', BrandListView.as_view(), name='brand-list'),
    path('api/perfumes/', PerfumeListView.as_view(), name='perfume-list'),
    path('api/register/', RegisterView.as_view()),
    path('api/login/', LoginView.as_view()),
    path('api/whoami/', WhoAmIView.as_view()),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/guest-session/',GuestSessionView.as_view(),name='guest-session'),
    path("api/cart/", CartView.as_view(), name="cart"),
    path("api/cart/add/<int:perfume_id>/", AddToCartView.as_view(), name="add_to_cart"),
    path("api/cart/update/<int:item_id>/", UpdateCartItemQuantity.as_view(), name="cart-update"),
    path("api/cart/remove/<int:item_id>/", RemoveCartItemView.as_view(), name="cart-remove"),
    path('cart-page/', cart_page, name='cart_page'),
    path("cart-page/api/checkout/", checkout_page, name="checkout"),
    path("api/checkout/", CheckoutView.as_view(), name="checkout"),
    path("api/order/place/", PlaceOrderView.as_view(), name="place-order"),
    path("api/orders/", OrderHistoryView.as_view(), name="order_history"),
    path("orders/",order_history_page,name='order_page')
]



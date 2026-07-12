from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate,login
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from rest_framework.permissions import AllowAny 
from .paginations import PerfumePagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
import uuid
from .serializers import *
from .models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page



@cache_page(60 * 10)
def home(request):
    return render(request, "home.html")

@method_decorator(cache_page(60 * 5), name='get')
class BrandListView(generics.ListAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        print("🔥 BRAND VIEW HIT DATABASE")
        return super().get(request, *args, **kwargs)
    
@method_decorator(cache_page(60 * 5), name='get')
class PerfumeListView(generics.ListAPIView):
    queryset = Perfume.objects.select_related("brand").all()
    serializer_class = PerfumeSerializer
    permission_classes = [AllowAny]
    pagination_class = PerfumePagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['perfume_type', 'brand']

    def get(self, request, *args, **kwargs):
        print("🔥 PERFUME VIEW HIT DATABASE")
        return super().get(request, *args, **kwargs)
    
    

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response({
            "message": "User created successfully",
            "user": RegisterSerializer(user).data
        }, status=201)


class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)

        if user is None:
            return Response({"detail": "Invalid credentials"}, status=401)

        # DELETE guest cart on login
        guest_id = request.COOKIES.get("guest_id")
        if guest_id:
            Cart.objects.filter(guest_id=guest_id).delete()

        refresh = RefreshToken.for_user(user)

        response = Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        })

        # Remove old guest cookie
        response.delete_cookie("guest_id")

        return response


class WhoAmIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user

        if user.is_authenticated:
            return Response({
                "authenticated": True,
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name
            })

        
        return Response({
            "authenticated": False
        })

        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()  # blacklist the token

            return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)
        except TokenError as e:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)
    
class GuestSessionView(APIView):
    """
    Creates or returns a unique anonymous session ID for guest users.
    This ID is stored in a cookie and lasts until browser closes or expires.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        # Check if guest_id already exists in cookie
        guest_id = request.COOKIES.get("guest_id")

        if not guest_id:
            # Generate a unique temporary ID (UUID)
            guest_id = str(uuid.uuid4())

        response = Response({"guest_id": guest_id})
        # Set cookie so frontend can use it
        response.set_cookie(
            "guest_id",
            guest_id,
            max_age=60 * 60 * 24 * 7,  # 7 days
            httponly=False,
            secure=False,
            samesite="Lax"
        )
        return response
        

def get_or_create_cart(request):
    """Returns (cart, guest_id) for authenticated or guest users."""

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart, None

    guest_id = request.COOKIES.get("guest_id")

    if not guest_id:
        guest_id = str(uuid.uuid4())

    cart, _ = Cart.objects.get_or_create(guest_id=guest_id)

    return cart, guest_id


# ------------------------------------
# GET CART (authenticated or guest)
# ------------------------------------
class CartView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart, guest_id = get_or_create_cart(request)

        response = Response(CartSerializer(cart).data, status=200)

        # If guest, set cookie
        if guest_id:
            response.set_cookie(
            "guest_id",
            guest_id,
            httponly=False,
            secure=False,
            samesite="Lax"
        )

        return response


# ------------------------------------
# ADD ITEM TO CART
# ------------------------------------
class AddToCartView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, perfume_id):
        cart, guest_id = get_or_create_cart(request)

        try:
            perfume = Perfume.objects.get(id=perfume_id)
        except Perfume.DoesNotExist:
            return Response({"error": "Perfume not found"}, status=404)

        item, created = CartItem.objects.get_or_create(cart=cart, perfume=perfume)

        if not created:
            item.quantity += 1
        item.save()

        response = Response(CartSerializer(cart).data, status=200)

        if guest_id:
            response.set_cookie("guest_id", guest_id, max_age=7*24*3600)

        return response


# ------------------------------------
# UPDATE QUANTITY
# ------------------------------------
class UpdateCartItemQuantity(APIView):
    permission_classes = [AllowAny]

    def post(self, request, item_id):
        quantity = request.data.get("quantity")

        if not quantity or int(quantity) <= 0:
            return Response({"error": "Quantity must be >= 1"}, status=400)

        cart, guest_id = get_or_create_cart(request)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.quantity = int(quantity)
        item.save()

        response = Response(CartSerializer(cart).data, status=200)

        if guest_id:
            response.set_cookie("guest_id", guest_id, max_age=7 * 24 * 3600)

        return response


# ------------------------------------
# REMOVE ITEM
# ------------------------------------
class RemoveCartItemView(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, item_id):
        cart, guest_id = get_or_create_cart(request)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        item.delete()

        response = Response(CartSerializer(cart).data, status=200)

        if guest_id:
            response.set_cookie("guest_id", guest_id, max_age=7 * 24 * 3600)

        return response        

def cart_page(request):
    cart, guest_id = get_or_create_cart(request)
    items = cart.items.all() if cart else []
    total = sum([item.subtotal for item in items])
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total': total})


class CheckoutView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cart, guest_id = get_or_create_cart(request)

        if not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        user = request.user if request.user.is_authenticated else None

        return Response({
            "items": CartSerializer(cart).data["items"],
            "total": cart.total_price,
            "user": {
                "full_name": user.get_full_name() if user else "",
                "email": user.email if user else "",
            },
            "guest_id": guest_id
        })


class PlaceOrderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        cart, guest_id = get_or_create_cart(request)

        if cart.items.count() == 0:
            return Response({"error": "Cart is empty"}, status=400)

        data = request.data

        full_name = data.get("full_name")
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address")

        if not all([full_name, email, phone, address]):
            return Response({"error": "All fields are required"}, status=400)

        user = request.user if request.user.is_authenticated else None

        order = Order.objects.create(
            user=user,
            guest_id=None if user else guest_id,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            total=cart.total_price,
            is_completed=False
        )

        # Create order items
        for item in cart.items.all():
            perfume = item.perfume

            # 🔒 Check stock
            if perfume.quantity < item.quantity:
                return Response({
                    "error": f"Not enough stock for {perfume.name}. "
                            f"Available quantity: {perfume.quantity}"
                }, status=400)

            # ✅ Reduce stock
            perfume.quantity -= item.quantity
            perfume.save()

            # ✅ Create order item
            OrderItem.objects.create(
                order=order,
                perfume=perfume,
                quantity=item.quantity,
                subtotal=item.subtotal
            )


        # Clear cart
        cart.items.all().delete()

        return Response({
            "message": "Order placed successfully",
            "order_id": order.id,
            "total": order.total
        }, status=201)

def checkout_page(request):
    cart, guest_id = get_or_create_cart(request)

    if not cart.items.exists():
        return render(request, "checkout.html", {
            "items": [],
            "total": 0,
            "error": "Your cart is empty."
        })

    user = request.user if request.user.is_authenticated else None

    context = {
        "items": cart.items.all(),
        "total": cart.total_price,
        "user_full_name": user.get_full_name() if user else "",
        "user_email": user.email if user else "",
        "guest_id": guest_id,
    }

    return render(request, "checkout.html", context)


class OrderHistoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        orders = Order.objects.filter(user=user).order_by('-created_at')

        orders_data = []
        for order in orders:
            items = [{
                "perfume_name": item.perfume.name,
                "quantity": item.quantity,
                "subtotal": item.subtotal,
                "image": item.perfume.image.url if item.perfume.image else None
            } for item in order.items.all()]

            orders_data.append({
                "id": order.id,
                "total": order.total,
                "completed": order.is_completed,
                "items": items,
                "created_at": order.created_at
            })

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            },
            "orders": orders_data
        })


def order_history_page(request):
    """
    Just renders the HTML template.
    Actual orders are fetched via JS from /api/orders/
    """
    return render(request, 'order_history.html')    



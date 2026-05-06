from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.db.models import Sum
from .permissions import IsAdminOrReadOnly, IsAdmin
from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Course, Offer, Order,Category
from .serializers import (
    CourseSerializer,
    OfferSerializer,
    OrderSerializer,
    LoginSerializer,
    CategorySerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Course.objects.select_related('category').all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def filter(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAdmin]



class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]

    @action(detail=False, methods=['get'])
    def by_course(self, request):
        course_id = request.query_params.get('course_id')

        if not course_id:
            return Response(
                {"error": "course_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        orders = self.queryset.filter(course_id=course_id)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


@extend_schema(request=LoginSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = authenticate(
        username=serializer.validated_data['username'],
        password=serializer.validated_data['password']
    )

    if user is not None:
   
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "username": user.username,
            "is_staff": user.is_staff,
            "role": getattr(user, 'role', 'user'),
        }, status=status.HTTP_200_OK)

    return Response(
        {"error": "Invalid credentials"},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAdmin])
def dashboard_view(request):
    User = get_user_model()
    totals = Order.objects.aggregate(total_payment=Sum('total_price'))
    total_payment = totals['total_payment'] or 0

    return Response({
        "total_payment": total_payment,
        "refund_amount": 0,
        "buy_request": Order.objects.count(),
        "delivery": Order.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "inactive_users": User.objects.filter(is_active=False).count(),
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_course_view(request):
    course_id = request.data.get('Course_id') or request.data.get('course') or request.data.get('course_id')

    try:
        quantity = int(request.data.get('quantity') or 1)
    except (TypeError, ValueError):
        return Response({"error": "Quantity must be a number"}, status=status.HTTP_400_BAD_REQUEST)

    if quantity < 1:
        return Response({"error": "Quantity must be at least 1"}, status=status.HTTP_400_BAD_REQUEST)

    if not course_id:
        return Response({"error": "Course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        course = Course.objects.get(id=course_id, available=True)
    except Course.DoesNotExist:
        return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

    order = Order.objects.create(user=request.user, course=course, quantity=quantity)
    saved = (course.mrp * quantity) - order.total_price

    return Response({
        "order_id": order.id,
        "Final Price": order.total_price,
        "You Saved": saved,
    }, status=status.HTTP_201_CREATED)
    

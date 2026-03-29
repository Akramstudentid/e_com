from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, CourseViewSet, OfferViewSet, OrderViewSet
from django.urls import path
from .views import login_view


router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'offers', OfferViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = router.urls
urlpatterns += [
    path('login/', login_view, name='login'),
    path('Category/', CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name='category-list'),
]
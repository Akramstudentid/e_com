from django.urls import path
from .views import userListCreateView, userDetailView
urlpatterns = [
    path('users/', userListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', userDetailView.as_view(), name='user-detail'),
]
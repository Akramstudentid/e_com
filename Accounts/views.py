from django.shortcuts import render

from rest_framework import generics
from .models import user
from .serializers import userSerializer

class userListCreateView(generics.ListCreateAPIView):
    queryset = user.objects.all()
    serializer_class = userSerializer
    
class userDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = user.objects.all()
    serializer_class = userSerializer
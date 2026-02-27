from django.contrib.auth.models import Group, Permission
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from groups.serializers import GroupSerializer, PermissionSerializer
from app.permissions import GlobalDefaultPermission


class GroupListCreateView(generics.ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated, GlobalDefaultPermission,]


class GroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]


class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]

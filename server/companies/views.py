from companies.models import Company, CompanySettings
from companies.serializers import CompanySerializer, CompanySettingsSerializer, GroupSerializer
from django.contrib.auth.models import Group
from rest_framework import generics, permissions
from rest_framework.generics import RetrieveAPIView


class CompanyDetailView(RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CompanySettingsListCreateView(generics.ListCreateAPIView):
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

class CompanySettingsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'company_id'

class GroupListView(generics.ListAPIView):
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

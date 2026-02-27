from companies.models import Company, CompanySettings
from django.contrib.auth.models import Group
from rest_framework import serializers


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class CompanySettingsSerializer(serializers.ModelSerializer):
    chatbot_allowed_groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all()
    )

    class Meta:
        model = CompanySettings
        fields = [
            'id',
            'company',
            'enable_notifications',
            'report_negative_availability',
            'report_orders_awaiting_confirmation',
            'open_default_page',
            'enable_chatbot',
            'chatbot_allowed_groups',
        ]

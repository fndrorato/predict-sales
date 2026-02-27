from django.contrib.auth.models import Group
from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=100)  # Obrigatório

    # Campos opcionais
    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=2, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Campos para logos
    logo_login = models.ImageField(upload_to='logos/', blank=True, null=True)
    logo_template = models.ImageField(upload_to='logos/', blank=True, null=True)
    logo_icon = models.ImageField(upload_to='logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class CompanySettings(models.Model):
    
    PAGES_CHOICES = [
        ('dashboard', 'Dashboard'),
        ('order', 'Ordem de Compra'),
    ]
        
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name="settings")
    enable_notifications = models.BooleanField(default=True)
    report_negative_availability = models.BooleanField(default=True)
    report_orders_awaiting_confirmation = models.BooleanField(default=True)
    report_items_with_stock_no_sales = models.BooleanField(default=True)
    view_sales_last_weeks = models.BooleanField(default=True)
    open_default_page = models.CharField(max_length=20, choices=PAGES_CHOICES)
    enable_chatbot = models.BooleanField(default=True)
    chatbot_allowed_groups = models.ManyToManyField(Group, blank=True, related_name="companies_with_chatbot")    

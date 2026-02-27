from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v1/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    path('api/v1/', include('authentication.urls')),
    path('api/v1/', include('companies.urls')),
    path('api/v1/', include('dashboard.urls')),
    path('api/v1/', include('groups.urls')),
    path('api/v1/', include('items.urls')),
    path('api/v1/', include('orders.urls')),
    path('api/v1/', include('sales.urls')),
    path('api/v1/', include('stores.urls')),
    path('api/v1/', include('suppliers.urls')),
    path('api/v1/', include('users.urls')),
    path('api/v1/', include('notifications.urls')),
    path("api/v1/", include("chatbot.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

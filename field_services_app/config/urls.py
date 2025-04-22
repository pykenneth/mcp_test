"""URL Configuration for Field Services App"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

# Schema view for API documentation
schema_view = get_schema_view(
    openapi.Info(
        title="Field Services API",
        default_version='v1',
        description="API for the Field Services Application",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Main URL patterns
urlpatterns = [
    # Admin site
    path('admin/', admin.site.urls),
    
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    # JWT token authentication
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # App URLs - These will be implemented as the apps are developed
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/projects/', include('apps.projects.urls')),
    path('api/v1/work-orders/', include('apps.work_orders.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/documents/', include('apps.documents.urls')),
    path('api/v1/technicians/', include('apps.technicians.urls')),
    path('api/v1/customers/', include('apps.customers.urls')),
    path('api/v1/billing/', include('apps.billing.urls')),
    path('api/v1/training/', include('apps.training.urls')),
    path('api/v1/communication/', include('apps.communication.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/whatsapp/', include('apps.whatsapp.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add debug toolbar in development
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]

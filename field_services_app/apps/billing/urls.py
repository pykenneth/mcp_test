from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'billing'

router = DefaultRouter()
router.register('invoices', views.InvoiceViewSet, basename='invoice')
router.register('invoice-items', views.InvoiceItemViewSet, basename='invoice-item')
router.register('payments', views.PaymentViewSet, basename='payment')
router.register('pricing-tiers', views.PricingTierViewSet, basename='pricing-tier')
router.register('pricing-items', views.PricingItemViewSet, basename='pricing-item')
router.register('expenses', views.ExpenseViewSet, basename='expense')

urlpatterns = [
    path('', include(router.urls)),
]

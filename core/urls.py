from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CrateViewSet, DeliveryBatchViewSet, CustomerViewSet, get_user_group, VehicleViewSet, ContactViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'crates', CrateViewSet)
router.register(r'delivery_batches', DeliveryBatchViewSet)
router.register(r'customers', CustomerViewSet)
router.register('vehicles', VehicleViewSet)
router.register('contacts', ContactViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('get_group/', get_user_group, name='get_user_group'),
    path('', include(router.urls)),
    # Your other URLs
]

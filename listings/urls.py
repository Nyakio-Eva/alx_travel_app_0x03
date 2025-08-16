from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet , initiate_payment, verify_payment 

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

urlpatterns = [
    path('', include(router.urls)),
    path('payments/initiate/<int:booking_id>/', initiate_payment, name='initiate_payment'),
    path('payments/verify/', verify_payment, name='verify_payment'),
]

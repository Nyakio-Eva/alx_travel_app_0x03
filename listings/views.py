
import requests
import uuid

# Create your views here.
from django.shortcuts import render
from rest_framework import viewsets
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_payment_confirmation_email, send_booking_confirmation_email


from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status


CHAPA_BASE_URL = "https://api.chapa.co/v1"

@api_view(['POST'])
def initiate_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    tx_ref = str(uuid.uuid4())  # unique transaction ref

    payload = {
        "amount": str(booking.total_price),
        "currency": "ETB",
        "email": booking.user.email,
        "first_name": booking.user.first_name,
        "last_name": booking.user.last_name,
        "tx_ref": tx_ref,
        "callback_url": "http://localhost:8000/api/payments/verify/",  # adjust for prod
        "return_url": "http://localhost:8000/payment/success/",
        "customization[title]": "Booking Payment",
        "customization[description]": "Payment for booking"
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(f"{CHAPA_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if data.get('status') == 'success':
        # Create payment record
        Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            transaction_id=tx_ref,
            status='Pending'
        )
        return Response({"payment_url": data['data']['checkout_url']})
    else:
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.query_params.get('tx_ref')
    if not tx_ref:
        return Response({"error": "Transaction reference required"}, status=status.HTTP_400_BAD_REQUEST)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    }

    response = requests.get(f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}", headers=headers)
    data = response.json()

    if data.get('status') == 'success':
        payment = get_object_or_404(Payment, transaction_id=tx_ref)
        if data['data']['status'] == 'success':
            payment.status = 'Completed'
            payment.save()
            # Trigger email via Celery (later step)
            return Response({"message": "Payment verified successfully"})
        else:
            payment.status = 'Failed'
            payment.save()
            return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def verify_payment(request):
    tx_ref = request.query_params.get('tx_ref')
    if not tx_ref:
        return Response({"error": "Transaction reference required"}, status=status.HTTP_400_BAD_REQUEST)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
    }

    response = requests.get(f"{CHAPA_BASE_URL}/transaction/verify/{tx_ref}", headers=headers)
    data = response.json()

    if data.get('status') == 'success':
        payment = get_object_or_404(Payment, transaction_id=tx_ref)
        if data['data']['status'] == 'success':
            payment.status = 'Completed'
            payment.save()

            # Send confirmation email in background
            send_payment_confirmation_email.delay(payment.booking.user.email, payment.booking.id)

            return Response({"message": "Payment verified successfully"})
        else:
            payment.status = 'Failed'
            payment.save()
            return Response({"message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    
        

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer



class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        booking = serializer.save(user=self.request.user)
        # Trigger Celery task
        send_booking_confirmation_email.delay(
            booking.user.email,
            booking.listing.title,
            booking.date
        )
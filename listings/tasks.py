
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

@shared_task
def send_payment_confirmation_email(user_email, booking_id):
    subject = "Payment Confirmation - Booking #{0}".format(booking_id)
    message = (
        "Hello,\n\n"
        "We have received your payment for booking #{0}.\n"
        "Your booking is now confirmed.\n\n"
        "Thank you for choosing us!"
    ).format(booking_id)
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # make sure this is set in settings.py
        [user_email],
        fail_silently=False,
    )

@shared_task
def send_booking_confirmation_email(user_email, listing_name, booking_date):
    subject = "Booking Confirmation"
    message = f"Your booking for {listing_name} on {booking_date} has been confirmed!"
    from_email = None  # uses DEFAULT_FROM_EMAIL from settings
    recipient_list = [user_email]

    send_mail(subject, message, from_email, recipient_list)
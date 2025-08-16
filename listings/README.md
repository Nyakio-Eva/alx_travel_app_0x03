### Payment initiation log

[2025-08-16 15:20:11] "POST /api/payments/initiate/1/ HTTP/1.1" 200 212
Response:
{
  "payment_url": "https://checkout.chapa.co/checkout/tx_ref=TX-987654321"
}


### Payment verification log

[2025-08-16 15:21:47] "GET /api/payments/verify/?tx_ref=TX-987654321 HTTP/1.1" 200 72
Response:
{
  "message": "Payment verified successfully"
}

### Payment model entry
>>> from listings.models import Payment
>>> Payment.objects.last()
<Payment: Payment for booking 1 - Completed>

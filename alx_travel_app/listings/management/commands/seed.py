# listings/management/commands/seed.py

from django.core.management.base import BaseCommand
from listings.models import Listing, Booking, Review
from django.utils import timezone
import uuid
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Seed the database with sample listings, bookings, and reviews.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # Clear old data
        Review.objects.all().delete()
        Booking.objects.all().delete()
        Listing.objects.all().delete()

        for i in range(5):
            listing = Listing.objects.create(
                title=f"Sample Listing {i+1}",
                description="A wonderful place to stay!",
                location=random.choice(["Nairobi", "Mombasa", "Kisumu"]),
                price_per_night=random.uniform(50.0, 200.0),
            )

            # Add 2 bookings per listing
            for j in range(2):
                check_in = timezone.now().date() + timedelta(days=random.randint(1, 10))
                check_out = check_in + timedelta(days=random.randint(2, 5))
                Booking.objects.create(
                    listing=listing,
                    guest_name=f"Guest {j+1} for {listing.title}",
                    check_in=check_in,
                    check_out=check_out,
                )

            # Add 1 review per listing
            Review.objects.create(
                listing=listing,
                reviewer_name=f"Reviewer {i+1}",
                rating=random.randint(3, 5),
                comment="Great stay! Highly recommended.",
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))

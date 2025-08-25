from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

import random
APPROVAL_CHOICES = [
    ('pending', 'Pending Approval'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]
class User(AbstractUser):
    is_driver = models.IntegerField(default=0, blank=True, null=True)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=50, default='', blank=True, null=True)
    is_user = models.IntegerField(default=0, blank=True, null=True)
    driving_license = models.FileField(upload_to='documents/driving_license/', null=True, blank=True)
    rc_book = models.FileField(upload_to='documents/rc_book/', null=True, blank=True)
    aadhaar = models.FileField(upload_to='documents/aadhaar/', null=True, blank=True)
    pan_card = models.FileField(upload_to='documents/pan_card/', null=True, blank=True)
    vehicle_type = models.CharField(max_length=50, null=True, blank=True)
    model = models.CharField(max_length=50, null=True, blank=True)
    plate_number = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True) 
    approval_state = models.CharField(
        max_length=20,
        choices=APPROVAL_CHOICES,
        default='pending'
    )
    
class Ride(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    VEHICLE_CHOICES = [
        ('bike', 'Bike'),
        ('auto', 'Auto'),
        ('car_city', 'Car (City)'),
        ('tourism_car', 'Tourism Car'),
    ]
    user = models.ForeignKey(User, related_name='rides', on_delete=models.CASCADE)
    driver = models.ForeignKey(User, related_name='assigned_rides', null=True, blank=True, on_delete=models.SET_NULL)
    pickup = models.CharField(max_length=255)
    drop = models.CharField(max_length=255)
    distance_km = models.FloatField(default=0)  
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_CHOICES, default='car_city')
    fare = models.FloatField(default=0)  
    driver_incentive = models.FloatField(default=0)  
    customer_reward = models.JSONField(default=dict, blank=True) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completed = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    rejected_by = models.ManyToManyField(User, related_name='rejected_rides', blank=True)

    def __str__(self):
        return f"Ride {self.id} - {self.user.username} ({self.status})"


class DriverLocation(models.Model):
    driver = models.OneToOneField(User, on_delete=models.CASCADE, related_name='location')
    latitude = models.FloatField()
    longitude = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ride = models.OneToOneField(Ride, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    def is_valid(self):
        return not self.is_used and (timezone.now() - self.created_at).total_seconds() < 300
    

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} -> {self.user.username}"

class FareRule(models.Model):
    VEHICLE_TYPES = [
        ("bike", "Bike"),
        ("auto", "Auto"),
        ("car_city", "City Car"),
        ("tourism_car", "Tourism Car"),
    ]

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    min_distance = models.FloatField(default=0)   # e.g. 0, 5, 10
    max_distance = models.FloatField(null=True, blank=True)  # None = "Above"
    per_km_rate = models.FloatField()  # e.g. 8, 9, 10, etc.

    def __str__(self):
        if self.max_distance:
            return f"{self.vehicle_type}: {self.min_distance}-{self.max_distance} km → ₹{self.per_km_rate}/km"
        return f"{self.vehicle_type}: {self.min_distance}+ km → ₹{self.per_km_rate}/km"
    
# Reward based on distance
class DistanceReward(models.Model):
    vehicle_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Enter vehicle type (admin can add new types dynamically)"
    )
    min_distance = models.FloatField()
    max_distance = models.FloatField(null=True, blank=True)  # max_distance can be None for open-ended
    cashback = models.FloatField(default=0)
    water_bottles = models.IntegerField(default=0)
    tea = models.IntegerField(default=0)
    discount = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.min_distance}-{self.max_distance} km Reward"

# Tourism special offers
class TourismOffer(models.Model):
    name = models.CharField(max_length=100)
    discount = models.CharField(max_length=100, blank=True, null=True)
    tea = models.IntegerField(default=0)
    water_bottles = models.IntegerField(default=0)
    long_term_days = models.IntegerField(default=0)  # For multi-day bookings

    def __str__(self):
        return self.name
    
class IntegrationSettings(models.Model):
    maps_api_key = models.CharField(max_length=255, blank=True, null=True)
    sms_api_key = models.CharField(max_length=255, blank=True, null=True)
    payment_api_key = models.CharField(max_length=255, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Integration Settings"
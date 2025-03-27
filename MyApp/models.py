# D:\TaskLink\TaskLink\MyApp\models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_otp_verified = models.BooleanField(default=False)
    is_worker = models.BooleanField(default=False)
    worker_type = models.CharField(max_length=100, blank=True, null=True)
    experience = models.PositiveIntegerField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_subscribed = models.BooleanField(default=False)
    subscription_date = models.DateTimeField(blank=True, null=True)

class WorkerReview(models.Model):
    worker = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='given_reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('worker', 'reviewer')
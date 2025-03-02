from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class UserActivity(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']

class KnownDevice(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    fingerprint = models.CharField(max_length=64)
    name = models.CharField(max_length=100)
    last_used = models.DateTimeField(auto_now=True)
    is_trusted = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'fingerprint']
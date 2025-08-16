from django.db import models

# Create your models here.

class TrackingUpdate(models.Model):
    order_id = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    sender = models.CharField(max_length=50)  # "user" or "saathi"
    timestamp = models.DateTimeField(auto_now_add=True)

class ChatMessage(models.Model):
    order_id = models.CharField(max_length=100)
    sender = models.CharField(max_length=50)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class TrackingHistory(models.Model):
    order_id = models.CharField(max_length=100)
    sender = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
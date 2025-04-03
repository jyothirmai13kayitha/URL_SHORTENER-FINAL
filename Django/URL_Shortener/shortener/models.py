from django.db import models
from django.contrib.auth.models import User
from shortuuid.django_fields import ShortUUIDField
from django.utils import timezone

class ShortenedURL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = ShortUUIDField(
        length=8,
        max_length=8,
        primary_key=True,
        editable=False,
        alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )
    custom_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    click_count = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.original_url} → {self.get_short_url()}"

    def get_short_url(self):
        return self.custom_code if self.custom_code else self.short_code

    class Meta:
        ordering = ['-created_at']
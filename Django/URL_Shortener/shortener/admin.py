from django.contrib import admin
from .models import ShortenedURL

class ShortenedURLAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'custom_code', 'original_url', 'click_count', 'created_by', 'created_at', 'expires_at')
    search_fields = ('original_url', 'short_code', 'custom_code')
    list_filter = ('created_at', 'expires_at')
    readonly_fields = ('short_code', 'click_count', 'created_at')

admin.site.register(ShortenedURL, ShortenedURLAdmin)
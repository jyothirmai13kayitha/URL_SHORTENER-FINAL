from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from bs4 import BeautifulSoup
import requests
from django.views.decorators.csrf import csrf_exempt

from .models import ShortenedURL
from shortuuid import ShortUUID
from urllib.parse import urlparse
from datetime import timedelta
from django.utils import timezone

@csrf_exempt
def index(request):
    return render(request, 'shortener/index.html')


@login_required
def shorten_url(request):
    if request.method == 'POST':
        original_url = request.POST.get('original_url')
        custom_code = request.POST.get('custom_code', '').strip()
        expiration_days = request.POST.get('expiration_days', 0)

        # Validate URL
        val = URLValidator()
        try:
            val(original_url)
        except ValidationError:
            messages.error(request, "Invalid URL provided")
            return redirect('index')

        # Check if custom code is available if provided
        if custom_code:
            if ShortenedURL.objects.filter(custom_code=custom_code).exists():
                messages.error(request, "Custom code already in use")
                return redirect('index')

        # Get page title
        try:
            response = requests.get(original_url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title"
        except:
            title = "No title"

        # Create shortened URL
        shortened_url = ShortenedURL(
            original_url=original_url,
            created_by=request.user if request.user.is_authenticated else None,
            title=title
        )

        if custom_code:
            shortened_url.custom_code = custom_code

        if expiration_days and expiration_days.isdigit() and int(expiration_days) > 0:
            shortened_url.expires_at = timezone.now() + timedelta(days=int(expiration_days))

        shortened_url.save()

        messages.success(request, "URL shortened successfully!")
        return render(request, 'shortener/result.html', {
            'shortened_url': shortened_url,
            'base_url': request.build_absolute_uri('/')
        })

    return redirect('index')


def redirect_original(request, code):
    url_obj = get_object_or_404(ShortenedURL, short_code=code) if len(code) == 8 else \
        get_object_or_404(ShortenedURL, custom_code=code)

    # Check if URL is expired
    if url_obj.expires_at and url_obj.expires_at < timezone.now():
        return HttpResponse("This shortened URL has expired", status=410)

    # Increment click count
    url_obj.click_count += 1
    url_obj.save()

    return redirect(url_obj.original_url)


@login_required
def dashboard(request):
    user_urls = ShortenedURL.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'shortener/dashboard.html', {'urls': user_urls})


@login_required
def url_stats(request, code):
    url_obj = get_object_or_404(ShortenedURL, created_by=request.user, short_code=code) if len(code) == 8 else \
        get_object_or_404(ShortenedURL, created_by=request.user, custom_code=code)
    return render(request, 'shortener/stats.html', {'url': url_obj})
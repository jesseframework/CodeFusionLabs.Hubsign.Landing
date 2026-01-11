from django.shortcuts import render


def index(request):
    """Landing page view."""
    return render(request, 'landing/index.html')

from django.shortcuts import render
from apps.recipes.models import Recipe


def home(request):
    featured = Recipe.objects.filter(is_active=True).order_by('-created_at')[:4]
    return render(request, 'core/home.html', {'featured': featured})


def sustainability(request):
    return render(request, 'core/sustainability.html')

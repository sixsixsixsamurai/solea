from django.shortcuts import render, get_object_or_404
from .models import Recipe, Category


def menu(request):
    category_slug = request.GET.get('category')
    sort = request.GET.get('sort')
    search = request.GET.get('search', '').strip()

    recipes = Recipe.objects.filter(is_active=True).select_related('category')

    if category_slug:
        recipes = recipes.filter(category__slug=category_slug)

    if search:
        recipes = recipes.filter(title__icontains=search)

    if sort == 'price_asc':
        recipes = recipes.order_by('price')
    elif sort == 'price_desc':
        recipes = recipes.order_by('-price')
    elif sort == 'quick':
        recipes = recipes.order_by('cook_time')
    else:
        recipes = recipes.order_by('-created_at')

    categories = Category.objects.all()

    return render(request, 'recipes/menu.html', {
        'recipes': recipes,
        'categories': categories,
        'current_category': category_slug,
        'current_sort': sort,
        'search': search,
    })


def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug, is_active=True)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

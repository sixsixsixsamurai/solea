from django.shortcuts import render, get_object_or_404
from collections import Counter
import random
from .models import Recipe, Category


def _get_recommendations(request, count=4):
    from apps.orders.models import Order

    if request.user.is_authenticated:
        past_orders = list(
            Order.objects.filter(user=request.user, status=Order.Status.DELIVERED)
            .prefetch_related('items__recipe__category')
        )
    else:
        if not request.session.session_key:
            return []
        past_orders = list(
            Order.objects.filter(
                session_key=request.session.session_key,
                status=Order.Status.DELIVERED
            ).prefetch_related('items__recipe__category')
        )

    if not past_orders:
        half = count // 2
        vegan = list(Recipe.objects.filter(is_active=True, category__slug='vegan').select_related('category').prefetch_related('ingredients__ingredient').order_by('?')[:half])
        protein = list(Recipe.objects.filter(is_active=True, category__slug='protein').select_related('category').prefetch_related('ingredients__ingredient').order_by('?')[:count - half])
        result = vegan + protein
        random.shuffle(result)
        return result

    order_category_counts = Counter()
    for order in past_orders:
        cats_in_order = Counter()
        for item in order.items.all():
            if item.recipe.category:
                cats_in_order[item.recipe.category.slug] += item.quantity
        if cats_in_order:
            order_category_counts[cats_in_order.most_common(1)[0][0]] += 1

    if not order_category_counts:
        return []

    total_orders = sum(order_category_counts.values())
    recommended = []

    for cat_slug, cat_order_count in order_category_counts.most_common():
        n = max(1, round(cat_order_count / total_orders * count))
        cat_recipes = list(
            Recipe.objects.filter(is_active=True, category__slug=cat_slug)
            .select_related('category')
            .prefetch_related('ingredients__ingredient')
            .order_by('?')[:n]
        )
        recommended.extend(cat_recipes)

    random.shuffle(recommended)
    return recommended[:count]


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
    recommended = _get_recommendations(request)

    return render(request, 'recipes/menu.html', {
        'recipes': recipes,
        'categories': categories,
        'current_category': category_slug,
        'current_sort': sort,
        'search': search,
        'recommended': recommended,
    })


def recipe_detail(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug, is_active=True)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})

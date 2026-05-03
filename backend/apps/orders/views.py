from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Sum
from apps.recipes.models import Recipe
from .models import Order, OrderItem


def _get_or_create_cart(request):
    if request.user.is_authenticated:
        order, _ = Order.objects.get_or_create(
            user=request.user,
            status=Order.Status.PENDING,
        )
    else:
        if not request.session.session_key:
            request.session.create()
        request.session.modified = True  # гарантирует Set-Cookie в ответе
        order, _ = Order.objects.get_or_create(
            session_key=request.session.session_key,
            status=Order.Status.PENDING,
        )
    return order


def cart_detail(request):
    order = _get_or_create_cart(request)
    items = order.items.select_related('recipe')
    return render(request, 'orders/cart.html', {'order': order, 'items': items})


@require_POST
def cart_add(request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id, is_active=True)
    order = _get_or_create_cart(request)
    item, created = OrderItem.objects.get_or_create(
        order=order,
        recipe=recipe,
        defaults={'unit_price': recipe.price, 'quantity': 1}
    )
    if not created:
        item.quantity += 1
        item.save()
    order.recalculate_total()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.db.models import Sum
        count = order.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({'success': True, 'cart_count': count})
    return redirect(request.META.get('HTTP_REFERER') or 'orders:cart')


@require_POST
def place_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'login_required'}, status=403)
    order = _get_or_create_cart(request)
    if not order.items.exists():
        return JsonResponse({'success': False, 'error': 'Cart is empty'}, status=400)

    city      = request.POST.get('city', '').strip()
    street    = request.POST.get('street', '').strip()
    house     = request.POST.get('house', '').strip()
    apartment = request.POST.get('apartment', '').strip()

    if not city or not street or not house:
        return JsonResponse({'success': False, 'error': 'Address is incomplete'}, status=400)

    address_parts = [city, street, house]
    if apartment:
        address_parts.append(apartment)
    order.delivery_address = ', '.join(address_parts)
    order.status = Order.Status.DELIVERED
    order.save(update_fields=['delivery_address', 'status'])

    return JsonResponse({'success': True, 'order_id': order.id})


def cart_data(request):
    order = _get_or_create_cart(request)
    items = order.items.select_related('recipe').all()
    cart_count = order.items.aggregate(total=Sum('quantity'))['total'] or 0
    data = {
        'cart_count': cart_count,
        'total_price': str(order.total_price),
        'items': [
            {
                'id': item.id,
                'title': item.recipe.title,
                'image': item.recipe.image.url if item.recipe.image else None,
                'unit_price': str(item.unit_price),
                'quantity': item.quantity,
                'subtotal': str(item.subtotal),
            }
            for item in items
        ],
    }
    return JsonResponse(data)


@require_POST
def cart_remove(request, item_id):
    order = _get_or_create_cart(request)
    item = get_object_or_404(OrderItem, pk=item_id, order=order)
    item.delete()
    order.recalculate_total()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = order.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({'success': True, 'cart_count': cart_count, 'total_price': str(order.total_price)})
    return redirect('orders:cart')


@require_POST
def cart_update(request, item_id):
    order = _get_or_create_cart(request)
    item = get_object_or_404(OrderItem, pk=item_id, order=order)
    qty = int(request.POST.get('quantity', 1))
    if qty < 1:
        item.delete()
    else:
        item.quantity = qty
        item.save()
    order.recalculate_total()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = order.items.aggregate(total=Sum('quantity'))['total'] or 0
        return JsonResponse({'success': True, 'cart_count': cart_count, 'total_price': str(order.total_price)})
    return redirect('orders:cart')

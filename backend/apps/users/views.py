from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, LoginForm


def _merge_guest_cart(request, user):
    """Merge the guest session cart into the authenticated user's cart.

    Called right after login or registration so items added while browsing
    as a guest are not lost. If the same recipe already exists in the user's
    cart, quantities are combined rather than duplicated.
    """
    session_key = request.session.session_key
    if not session_key:
        return

    from apps.orders.models import Order, OrderItem
    guest_order = Order.objects.filter(
        session_key=session_key,
        status=Order.Status.PENDING
    ).first()
    if not guest_order or not guest_order.items.exists():
        return

    user_order, _ = Order.objects.get_or_create(
        user=user,
        status=Order.Status.PENDING
    )

    for guest_item in guest_order.items.all():
        user_item, created = OrderItem.objects.get_or_create(
            order=user_order,
            recipe=guest_item.recipe,
            defaults={'unit_price': guest_item.unit_price, 'quantity': guest_item.quantity}
        )
        if not created:
            # Recipe already in user cart — add guest quantity on top
            user_item.quantity += guest_item.quantity
            user_item.save()

    user_order.recalculate_total()
    # Remove the guest cart so it doesn't linger in the database
    guest_order.delete()


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    next_url = request.GET.get('next', '')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            _merge_guest_cart(request, user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect(next_url or 'core:home')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form, 'next': next_url})


def user_login(request):
    if request.user.is_authenticated:
        return redirect('core:home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                _merge_guest_cart(request, user)
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('core:home')


@login_required
def profile(request):
    orders = request.user.orders.exclude(status='pending').order_by('-created_at')
    total_spent = sum(o.total_price for o in orders)
    return render(request, 'users/profile.html', {'orders': orders, 'total_spent': total_spent})

from django.db.models import Sum
from .models import Order


def cart_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            order = Order.objects.filter(user=request.user, status=Order.Status.PENDING).first()
        elif request.session.session_key:
            order = Order.objects.filter(
                session_key=request.session.session_key,
                status=Order.Status.PENDING
            ).first()
        else:
            order = None
        if order:
            count = order.items.aggregate(total=Sum('quantity'))['total'] or 0
    except Exception:
        pass
    return {'cart_count': count}

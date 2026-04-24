from django.shortcuts import render
from .models import Partner


def partners(request):
    partner_list = Partner.objects.filter(is_active=True)
    return render(request, 'partners/partners.html', {'partners': partner_list})

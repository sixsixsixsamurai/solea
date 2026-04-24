from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.cart_detail, name='cart'),
    path('data/', views.cart_data, name='data'),
    path('place-order/', views.place_order, name='place_order'),
    path('add/<int:recipe_id>/', views.cart_add, name='add'),
    path('remove/<int:item_id>/', views.cart_remove, name='remove'),
    path('update/<int:item_id>/', views.cart_update, name='update'),
]

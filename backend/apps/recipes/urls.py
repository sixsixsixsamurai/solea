from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.menu, name='menu'),
    path('<slug:slug>/', views.recipe_detail, name='detail'),
]

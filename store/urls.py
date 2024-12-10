from django.contrib.auth import views as auth_views
from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('product/<int:id>', product, name='product'),
    path('add_to_cart/<int:id>/', add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('cart/', cart, name='cart'),
    path('checkout/', checkout, name='checkout'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('profile', profile, name='profile'),
    path('search/', search_products, name='search_products'),

]
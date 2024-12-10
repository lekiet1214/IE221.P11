from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.admin import AdminSite
from .models import Product, Cart, Order, Customer, CartItem
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# Register your models here.

# admin.site.register(Product)
# admin.site.register(Cart)
# admin.site.register(Order)
# admin.site.register(Customer)
# admin.site.register(CartItem)



class CustomAdminSite(AdminSite):
    site_header = 'Store Admin'
    site_title = 'Store Admin Portal'
    index_title = 'Welcome to Store Admin Portal'

custom_admin_site = CustomAdminSite(name='custom_admin')

@admin.register(Product, site=custom_admin_site)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')  # Columns in the list view
    search_fields = ('name', 'description')    # Fields to search in


# Register the Customer model with search functionality
@admin.register(Customer, site=custom_admin_site)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')
# custom_admin_site.register(Product)
custom_admin_site.register(Cart)
custom_admin_site.register(Order)
# custom_admin_site.register(Customer)
custom_admin_site.register(CartItem)
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)
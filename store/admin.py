from django.contrib import admin
from .models import Category, Product, Profile, Address, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'available', 'created_at')
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(OrderItem)

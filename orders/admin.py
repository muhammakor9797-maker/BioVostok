from django.contrib import admin
from .models import Order, OrderItem, ShippingMethod


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    readonly_fields = ['price', 'quantity']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'phone', 'country', 
                    'shipping_method', 'created', 'paid', 'get_total_cost']
    list_filter = ['paid', 'created', 'shipping_method', 'country']
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'address']
    readonly_fields = ['created', 'updated', 'get_total_cost']
    inlines = [OrderItemInline]


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'min_days', 'max_days', 'available_worldwide', 'active']
    list_filter = ['active', 'available_worldwide']


admin.site.site_header = 'Управление магазином'
admin.site.site_title = 'Админ панель'

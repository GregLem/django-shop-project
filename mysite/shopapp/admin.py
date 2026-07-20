from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from .models import Product, Order
from .admin_mixins import ExportAsCSVMixin


class OrderInline(admin.TabularInline):
    model = Product.orders.through
    extra = 0
    classes = ("collapse",)
    verbose_name = "Заказ"
    verbose_name_plural = "Заказы с этим товаром"


@admin.action(description="Архивировать выбранные товары")
def mark_archived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=True)


@admin.action(description="Разархивировать выбранные товары")
def mark_unarchived(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet):
    queryset.update(archived=False)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    actions = [mark_archived, mark_unarchived, "export_csv"]
    inlines = [OrderInline]
    
    list_display = ("pk", "name", "description_short", "price", "discount", "archived")
    list_display_links = ("pk", "name")
    ordering = ("name",)
    search_fields = ("name", "description", "price", "discount")
    list_filter = ("archived", "discount")
    
    fieldsets = (
        (None, {
            "fields": ("name", "description"),
        }),
        ("Price options", {
            "fields": ("price", "discount"),
            "classes": ("collapse", "wide"),
        }),
        ("Extra options", {
            "fields": ("archived",),
            "classes": ("collapse",),
            "description": "Extra options. Field 'archived' is for soft delete",
        }),
    )

    def description_short(self, obj: Product) -> str:
        if len(obj.description) < 48:
            return obj.description
        return obj.description[:48] + "..."
    description_short.short_description = "Краткое описание"


class ProductInline(admin.StackedInline):
    model = Order.products.through
    extra = 0
    classes = ("collapse",)
    verbose_name = "Товар"
    verbose_name_plural = "Товары в заказе"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ("delivery_address", "promocode", "created_at", "user_verbose")
    list_filter = ("created_at",)
    search_fields = ("promocode", "delivery_address")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
    user_verbose.short_description = "Пользователь"
    user_verbose.admin_order_field = "user__username"
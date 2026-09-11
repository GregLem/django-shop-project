from timeit import default_timer

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
    PermissionRequiredMixin,
)
from django.contrib.auth.models import Group
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render, reverse, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import GroupForm, ProductForm
from .models import Order, Product, ProductImage


# ============================================================
# ГЛАВНАЯ СТРАНИЦА
# ============================================================

class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ("laptop", 1999),
            ("desktop", 2999),
            ("laptop", 1999),
            ("smartphone", 999),
        ]

        context = {
            "time_running": default_timer(),
            "products": products,
        }

        return render(
            request,
            "shopapp/shop-index.html",
            context=context,
        )


# ============================================================
# ГРУППЫ
# ============================================================

class GroupListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related(
                "permissions"
            ).all(),
        }

        return render(
            request,
            "shopapp/groups_list.html",
            context=context,
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)

        if form.is_valid():
            form.save()

        return redirect(request.path)


# ============================================================
# ТОВАРЫ
# ============================================================

class ProductDetailView(DetailView):
    queryset = Product.objects.prefetch_related("images").all()
    template_name = "shopapp/product-details.html"
    context_object_name = "product"


class ProductListView(ListView):
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "shopapp/create-product.html"
    success_url = reverse_lazy("shopapp:products_list")

    def test_func(self):
        return self.request.user.has_perm("shopapp.add_product")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def test_func(self):
        product = self.get_object()
        user = self.request.user

        return user.is_superuser or (
            user.has_perm("shopapp.change_product")
            and product.created_by == user
        )

    def form_valid(self, form):
        response = super().form_valid(form)

        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )

        return response

    def get_success_url(self):
        return reverse(
            "shopapp:product_details",
            kwargs={"pk": self.object.pk},
        )


class ProductDeleteView(DeleteView):
    model = Product
    template_name = "shopapp/product_confirm_delete.html"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()

        self.object.archived = True
        self.object.save()

        return HttpResponseRedirect(success_url)


# ============================================================
# ЗАКАЗЫ
# ============================================================

class OrderListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )

    template_name = "shopapp/order_list.html"
    context_object_name = "orders"


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "shopapp/order-details.html"
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects
            .select_related("user")
            .prefetch_related("products")
        )


class OrderCreateView(CreateView):
    model = Order
    fields = (
        "delivery_address",
        "promocode",
        "user",
        "products",
    )
    template_name = "shopapp/order_create.html"
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = (
        "delivery_address",
        "promocode",
        "user",
        "products",
    )
    template_name = "shopapp/order_update.html"

    def get_success_url(self):
        return reverse(
            "shopapp:order_details",
            kwargs={"pk": self.object.pk},
        )


class OrderDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = "shopapp.delete_order"
    model = Order
    template_name = "shopapp/order_confirm_delete.html"
    success_url = reverse_lazy("shopapp:order_list")


# ============================================================
# ЭКСПОРТ ТОВАРОВ В JSON
# ============================================================

class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()

        products_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]

        return JsonResponse(
            {"products": products_data}
        )


# ============================================================
# ЭКСПОРТ ЗАКАЗОВ В JSON
# Только для staff-пользователей
# ============================================================

@method_decorator(
    user_passes_test(lambda u: u.is_staff),
    name="dispatch",
)
class OrdersDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = (
            Order.objects
            .select_related("user")
            .prefetch_related("products")
            .all()
        )

        orders_data = [
            {
                "id": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "product_ids": [
                    product.pk
                    for product in order.products.all()
                ],
            }
            for order in orders
        ]

        return JsonResponse(
            {"orders": orders_data}
        )
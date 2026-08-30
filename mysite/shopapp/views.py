from timeit import default_timer
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import ProductForm, GroupForm
from .models import Product, Order
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('laptop', 1999),
            ('desktop', 2999),
            ('laptop', 1999),
            ('smartpone',999),

        ]
        context = {
            'time_running': default_timer(),
            'products':products,
        }
        return render(request,'shopapp/shop-index.html',context=context)

class GroupListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups_list.html', context=context)
    def post(self, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
           
        return redirect(request.path)

class ProductDetailView(DetailView):
    model = Product
    template_name = "shopapp/product-details.html"
    context_object_name = "product"

class ProductListView(ListView):
    # model = Product
    template_name = "shopapp/products-list.html"
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


def create_product(request: HttpRequest) -> HttpResponse:

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            #Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:products_list") 
            return redirect(url)
    else:
        form = ProductForm()

    context = {
        "form": form,
    }

    return render(request, "shopapp/create-product.html", context)

# class ProductCreateView(UserPassesTestMixin,CreateView):
#     def test_func(self):
#         return self.request.user.groups.filter(name="secret_group").exists()
#     model = Product
#     form_class = ProductForm
#     template_name = "shopapp/create-product.html"
#     success_url = reverse_lazy("shopapp:products_list")

# shopapp/views.py

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

class ProductUpdateView(UpdateView):
    # model = Product
    # fields = ("name", "price", "description")
    # template_name = "shopapp/product_update_form.html"
    model = Product
    fields = ("name", "price", "description")
    template_name_suffix = "_update_form"  # → ищет product_update_form.html

    def test_func(self):
        product = self.get_object()
        user = self.request.user
        return user.is_superuser or (
            user.has_perm("shopapp.change_product") and
            product.created_by == user
        )

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})

class ProductDeleteView(DeleteView):
    model = Product
    template_name = "shopapp/product_confirm_delete.html"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)



class OrderListView(LoginRequiredMixin, ListView):
    queryset = Order.objects.select_related(
        "user"
    ).prefetch_related("products")

    template_name = "shopapp/orders_list.html"
    context_object_name = "orders"

class OrderDetailView(PermissionRequiredMixin,DetailView):
    model = Order
    template_name = "shopapp/order-details.html"
    context_object_name = "order"
    permission_required = "shopapp.view_order"

    def get_queryset(self):
        return (
            Order.objects
            .select_related("user")
            .prefetch_related("products")
        )
class OrderCreateView(CreateView):
    model = Order
    fields = ("delivery_address", "promocode", "user", "products")
    template_name = "shopapp/order_create.html"
    success_url = reverse_lazy("shopapp:order_list")


class OrderUpdateView(UpdateView):
    model = Order
    fields = ("delivery_address", "promocode", "user", "products")
    template_name = "shopapp/order_update.html"

    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})

class OrderDeleteView(PermissionRequiredMixin,DeleteView):
    permission_required = "shopapp.view_order"
    model = Order
    template_name = "shopapp/order_confirm_delete.html"
    success_url = reverse_lazy("shopapp:order_list")

class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
           { "pk" : product.pk,
            "name": product.name,
            "price": str(product.price),
            "archived": product.archived,
           }
           for product in products
        ]
        return JsonResponse({"products": products_data})


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class OrdersDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        orders = Order.objects.select_related('user').prefetch_related('products').all()
        orders_data = [
            {
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'product_ids': [p.pk for p in order.products.all()]
            }
            for order in orders
        ]
        return JsonResponse({'orders': orders_data})
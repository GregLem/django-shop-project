from timeit import default_timer
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from .forms import ProductForm, GroupForm
from .models import Product, Order


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

class ProductDetailView(View):
    def get(self, request: HttpRequest, product_id: int) -> HttpResponse:
        product = get_object_or_404(Product, pk=product_id)
        context = {
            "product": product,
        }
        return render(request, 'shopapp/product-details.html', context=context)

class ProductListView(TemplateView):
    template_name = "shopapp/products-list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        return context



def create_product(request: HttpRequest) -> HttpResponse:

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            #Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:products-list") 
            return redirect(url)
    else:
        form = ProductForm()

    context = {
        "form": form,
    }

    return render(request, "shopapp/create-product.html", context)

def orders_list(request: HttpRequest):
    context = {
        "orders" : Order.objects.select_related('user').prefetch_related("products").all()
    }
    return render(request, "shopapp/orders_list.html", context=context)

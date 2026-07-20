from timeit import default_timer
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.http import HttpRequest

from .models import Product, Order

# Create your views here.
def shop_index(request: HttpRequest):
    # print(request.path)
    # print(request.method)
    # print(request.headers)
    # return HttpResponse('<h1>Hello World')
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

def groups_list(request: HttpRequest):
    context = {
        "groups": Group.objects.prefetch_related('permissions').all(),
    }
    return render(request, 'shopapp/groups_list.html', context=context)

def products_list(request: HttpRequest):
    context = {
        "products": Product.objects.all(),
    }
    return render(request, 'shopapp/products-list.html', context=context)

def orders_list(request: HttpRequest):
    context = {
        "orders" : Order.objects.select_related('user').prefetch_related("products").all()
    }
    return render(request, "shopapp/orders_list.html", context=context)

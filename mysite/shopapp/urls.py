from django.urls import path
from .views import (ShopIndexView,
                    GroupListView,
                    OrderListView,
                    OrderDetailView, 
                    ProductDetailView, 
                    ProductListView,
                    create_product)



app_name = 'shopapp'

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),

    path(
    "products/create/",
    create_product,
    name="create_product",
   ),
    path(
        "products/",
        ProductListView.as_view(),
        name="products_list",
    ),

    path(
        "products/<int:pk>/",
        ProductDetailView.as_view(),
        name="product_details",
    ),

    path(
        "orders/",
        OrderListView.as_view(),
        name="order_list",
    ),

    path(
        "orders/<int:pk>/",
        OrderDetailView.as_view(),
        name="order_details",
    ),
]
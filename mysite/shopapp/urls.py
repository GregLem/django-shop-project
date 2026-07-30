from django.urls import path
from .views import (ShopIndexView,
GroupListView, orders_list, create_product, ProductDetailView, ProductListView)



app_name = 'shopapp'

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("groups/", GroupListView.as_view(), name="groups_list"),
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/create/", create_product, name="create_product"),
    path(
        "products/<int:product_id>/",
        ProductDetailView.as_view(),
        name="product_details",
    ),
    path("orders/", orders_list, name="orders_list"),
]
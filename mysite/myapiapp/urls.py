from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import hello_world_view, GroupsListView
from shopapp.views import ProductViewSet, OrderViewSet


router = DefaultRouter()

router.register("products", ProductViewSet)
router.register("orders", OrderViewSet)


urlpatterns = [
    path("hello/", hello_world_view, name="hello"),
    path("groups/", GroupsListView.as_view(), name="groups"),
    path("", include(router.urls)),
]
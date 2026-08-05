from django.urls import path
from .views import login_view
from django.contrib.auth.views import LoginView


app_name = "myaut"

urlpatterns = [
    #path("login/", login_view, name="login"),
    path("login/", LoginView.as_view(template_name="myaut/login.html", redirect_authenticated_user=True), name="login"),
]
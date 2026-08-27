from django.urls import path
from .views import login_view
from django.contrib.auth.views import LoginView
from . views import (set_cookie_view,
                    get_cookie_view,
                    set_session_view, 
                    get_session_view,
                    logout_view,
                    MyLogoutView,
                    AboutMeView,
                    RegisterView,
                    FooBarView)

app_name = "myaut"

urlpatterns = [
    #path("login/", login_view, name="login"),
    path("login/", LoginView.as_view(template_name="myaut/login.html",
                                    redirect_authenticated_user=True),
                                    name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("cookie/set/", set_cookie_view, name="set_cookie"),
    path("cookie/get/", get_cookie_view, name="get_cookie"),

    path("session/set/", set_session_view, name="set_session"),
    path("session/get/", get_session_view, name="get_session"),

    #path("logout/", logout_view, name="logout"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("about-me/", AboutMeView.as_view(), name="about-me"),
    path("foo-bar/", FooBarView.as_view(), name="foo-bar"),
]
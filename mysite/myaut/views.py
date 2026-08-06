from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView

def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect("/admin/")
        return render(request, "myaut/login.html")
    
    username = request.POST.get("username")
    password = request.POST.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect("/admin/")
    return render(request, "myaut/login.html", context={"error": "Invalid username or password"})

def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect(reverse("myaut:login"))

class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myaut:login")

def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie has been set.")
    response.set_cookie("fizz", "buzz", max_age=3600)  # Cookie expires in 1 hour   
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "Default Value")
    return HttpResponse(f"Cookie value: {value}")

def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session value has been set.")

def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "Default Value")
    return HttpResponse(f"Session value: {value}")
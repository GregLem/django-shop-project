from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.forms import UserCreationForm 
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

from .models import Profile


class AboutMeView(TemplateView):
    template_name = "myaut/about-me.html"

class RegisterView(CreateView):
    # model = User
    form_class = UserCreationForm
    template_name = "myaut/register.html"
    success_url = reverse_lazy("myaut:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        Profile.objects.create(user=user)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request,
                            username=username,
                            password=password,)
        login(request=self.request, user=user)
        
        return response   

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

@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        response = HttpResponse("Cookie has been set.")
        response.set_cookie("fizz", "buzz", max_age=3600)  # Cookie expires in 1 hour   
        return response
    response = HttpResponse("Cookie has been set.")
    response.set_cookie("fizz", "buzz", max_age=3600)  # Cookie expires in 1 hour   
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "Default Value")
    return HttpResponse(f"Cookie value: {value}")

@permission_required("myaut.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session value has been set.")

@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "Default Value")
    return HttpResponse(f"Session value: {value}")

class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})

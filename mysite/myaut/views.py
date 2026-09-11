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
from django.shortcuts import render, redirect, get_object_or_404

from .models import Profile
from .forms import ProfileForm


class AboutMeView(TemplateView):
    template_name = "myaut/about-me.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            profile, created = Profile.objects.get_or_create(user=self.request.user)
            context["profile"] = profile
            context["profile_form"] = ProfileForm(instance=profile)
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("myaut:login")

        profile, created = Profile.objects.get_or_create(user=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("myaut:about-me")

        return render(request, self.template_name, {
            "profile": profile,
            "profile_form": form,
        })


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myaut/register.html"
    success_url = reverse_lazy("myaut:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        Profile.objects.create(user=user)
        login(self.request, user)
        return response



class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myaut:login")


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        response = HttpResponse("Cookie has been set.")
        response.set_cookie("fizz", "buzz", max_age=3600)
        return response
    response = HttpResponse("Cookie has been set.")
    response.set_cookie("fizz", "buzz", max_age=3600)
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


class UsersListView(ListView):
    model = User
    template_name = "myaut/users_list.html"
    context_object_name = "users"


class UserProfileView(DetailView):
    model = User
    template_name = "myaut/user_profile.html"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile, created = Profile.objects.get_or_create(user=self.object)  # ← get_or_create
        context["profile"] = profile
        context["can_edit"] = (
            self.request.user.is_staff or
            self.request.user == self.object
        )
        return context

class ProfileUpdateView(UpdateView):
    model = Profile
    form_class = ProfileForm
    template_name = "myaut/profile_update.html"

    def get_object(self, queryset=None):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        return user.profile

    def dispatch(self, request, *args, **kwargs):
        profile = self.get_object()

        if not (request.user.is_staff or request.user == profile.user):
            return HttpResponse("Доступ запрещён", status=403)

        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            "myaut:user_profile",
            kwargs={"pk": self.object.user.pk}
        )
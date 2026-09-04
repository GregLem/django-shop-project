from django import forms
from django.contrib.auth.models import Group

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ("name", "description", "price", "discount", "preview")


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name",)
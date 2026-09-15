from django import forms
from django.contrib.auth.models import Group

from .models import Order, Product 


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            result = []
            for item in data:
                result.append(single_file_clean(item, initial))
            return result

        return single_file_clean(data, initial)


class ProductForm(forms.ModelForm):

    images = MultipleFileField(
        required=False,
    )

    class Meta:
        model = Product
        fields = (
            "name",
            "description",
            "price",
            "discount",
            "preview",
        )


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ("name",)


# ============================================================
# ФОРМА ЗАКАЗА (новый класс)
# ============================================================

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ("delivery_address", "promocode", "products")
        labels = {
            "delivery_address": "Адрес доставки",
            "promocode": "Промокод",
            "products": "Товары",
        }
        widgets = {
            "delivery_address": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "г. Москва, ул. Тверская, д. 10, кв. 5"
                }
            ),
            "promocode": forms.TextInput(
                attrs={
                    "placeholder": "WELCOME2026"
                }
            ),
            "products": forms.SelectMultiple(
                attrs={
                    "size": 6
                }
            ),
        }
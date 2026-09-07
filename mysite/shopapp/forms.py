from django import forms
from django.contrib.auth.models import Group

from .models import Product


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
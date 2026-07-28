from django import forms

class ProductForm(forms.Form):
    name = forms.CharField(max_length=100, label="Product Name")
    price = forms.DecimalField(min_value=1,max_value=100000)
    description = forms.CharField(widget=forms.Textarea, label="Product Description")
    # discount = forms.IntegerField(min_value=0, max_value=100, label="Discount (%)")
    archived = forms.BooleanField(required=False, label="Archived")
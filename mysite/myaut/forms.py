from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("bio", "agreement_accepted", "avatar")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3}),
        }
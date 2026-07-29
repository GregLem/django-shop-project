from django import forms
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

class UserBioForm(forms.Form):
    name = forms.CharField(max_length=100, label="Your name")
    age = forms.IntegerField(label="Your age", min_value=1, max_value=120)
    bio = forms.CharField(label="Biography", widget=forms.Textarea)

def validate_file_name(file: InMemoryUploadedFile) -> None:
    if not file.name.endswith('.txt'):
        raise ValidationError("Only .txt files are allowed.")

class UploadFileForm(forms.Form):
    file = forms.FileField(label="Upload a file")

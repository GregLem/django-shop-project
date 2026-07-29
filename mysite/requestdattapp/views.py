from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from .forms import UserBioForm, UploadFileForm


def process_get_view(request: HttpRequest) -> HttpResponse:
    a = request.GET.get("a", " ")
    b = request.GET.get("b", " ")
    result = a + b
    context = {
        "a": a,
        "b": b,
        "result":result,
    }
    return render(request,'requestdattapp/request-query-params.html', context=context)

def user_form(request: HttpRequest) -> HttpResponse:
    context = {
        "form": UserBioForm(),
    }
    return render(request, 'requestdattapp/user-bio-form.html',context=context)

def handle_file_upload(request: HttpRequest):

    form = UploadFileForm(request.POST, request.FILES)

    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            myfile = form.cleaned_data["file"]
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            print(f"File {filename} uploaded successfully!")
    else:
        form = UploadFileForm()

    context = {
        "form": form, 
        }

    return render(
        request,
        "requestdattapp/file-upload.html", context=context
    )              
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


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
    return render(request, 'requestdattapp/user-bio-form.html')

def handle_file_upload(request: HttpRequest) -> HttpResponse:
    if request.method == "POST" and request.FILES.get("myfile"):
        myfile = request.FILES["myfile"]
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        print("saved file", filename)
    return render(request, 'requestdattapp/file-upload.html')              
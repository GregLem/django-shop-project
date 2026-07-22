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

def handle_file_upload(request: HttpRequest):

    if request.method == "POST":

        myfile = request.FILES.get("myfile")

        if myfile:

            if myfile.size > 1024 * 1024:

                return HttpResponse(
                    "File size must be less than 1 MB",
                    status=400,
                )

            fs = FileSystemStorage()

            filename = fs.save(myfile.name, myfile)

            return HttpResponse(
                f"File {filename} uploaded successfully!"
            )

    return render(
        request,
        "requestdattapp/file-upload.html",
    )              
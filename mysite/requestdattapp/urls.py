# requestdattapp/urls.py

from django.urls import path
from .views import process_get_view, user_form, handle_file_upload    # ← импорт из views.py

app_name = 'requestdattapp'

urlpatterns = [
    path('get/', process_get_view, name='process_get'),
    path('bio/', user_form, name='user_form'),
    path('upload/', handle_file_upload, name='file-upload'),

]
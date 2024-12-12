
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin_latin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from administration.views import AdminLogin, Home

urlpatterns = [
    path('',Home.as_view(),name='admin-home'),
    path('admin_login/',AdminLogin.as_view(),name='admin-login'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

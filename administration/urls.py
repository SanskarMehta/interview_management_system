from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from administration.views import AdminLogin, Home, AdminAfterLogin, ShowUser, ShowInterviewers, ShowCompany, \
    CompanyAcceptanceByAdmin, DetailsOfUser, DetailsOfInterviewer, AdminUpdateUserDetails, UserRegisterByAdmin, \
    CompanyRegisterByAdmin, BlockUnblock

urlpatterns = [
    path('', Home.as_view(), name='admin-home'),
    path('admin_login/', AdminLogin.as_view(), name='admin-login'),
    path('admin_after_login/', AdminAfterLogin.as_view(), name='admin-after-login'),
    path('admin_logout/', auth_view.LogoutView.as_view(template_name='administration/logout.html'),
         name='admin-logout'),
    path('show_users/', ShowUser.as_view(), name='show-users'),
    path('show_interviewers/', ShowInterviewers.as_view(), name='show-interviewers'),
    path('show_companies/', ShowCompany.as_view(), name='show-companies'),
    path('company_acceptance/', CompanyAcceptanceByAdmin.as_view(), name='company-acceptance'),
    path('details_user/<int:pk>', DetailsOfUser.as_view(), name='admin-user-details'),
    path('details_interviewer/<int:pk>', DetailsOfInterviewer.as_view(), name='admin-interviewer-details'),
    path('update_admin_info/<int:pk>', AdminUpdateUserDetails.as_view(), name='admin-update-profile'),
    path('user_register_admin/', UserRegisterByAdmin.as_view(), name='user-register-admin'),
    path('company_register_admin/', CompanyRegisterByAdmin.as_view(), name='company-register-admin'),
    path('block_unblock/', BlockUnblock.as_view(), name='block-unblock'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from user_login.views import UserLogin, UserRegister, InterviewerHome, UserHome, CompanyHome, CompanyRegister, \
    UserDetailsForm, CompanyJobOpenings, HomeView, CompanyAddInterviewer, InterviewerDetailsForm, JobListsApply, \
    AfterJobApply, UserChangePassword, CompanyChangePassword, InterviewerChangePassword, CompanyCareer, JobLists, \
    UserAppliedJobs, UserProfile, InterviewerProfile, ShowInterviewers, UpdateUserDetails, \
    UpdateInterviewerDetails, ShowAppliedUser, JobOpeningUpdate, ShowAcceptedInterviewers, \
    ScheduleApplicantInterview, InterviewType, GetTimeSlot, ShowInterviewerScheduled, ApplicantDetails, \
    ShowDetailSchedule, DetailsInterviewer, UserMessage, CompanyMessage, InterviewerMessage, UserFeedbackView, \
    RescheduleRequest, ShowRescheduleRequests, FeedbackOfInterviewer, PostInterviewProcess, DeactivateAccount, \
    ReactivateAccount, ReactivationUser
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', UserLogin.as_view(), name='login'),
    path('register/', UserRegister.as_view(), name='register'),
    path('company_register/', CompanyRegister.as_view(), name='company-register'),
    path('interviewer_home/', InterviewerHome.as_view(), name='interviewer-home'),
    path('user_home/', UserHome.as_view(), name='user-home'),
    path('company_home/', CompanyHome.as_view(), name='company-home'),
    path('user_details_form/', UserDetailsForm.as_view(), name='user-details-form'),
    path('interviewer_details_form/', InterviewerDetailsForm.as_view(), name='interviewer-details-form'),
    path('company_job_openings/', CompanyJobOpenings.as_view(), name='company-job-openings'),
    path('logout/', auth_view.LogoutView.as_view(template_name='user_login/base.html'), name='logout'),
    path('company_add_interviewer', CompanyAddInterviewer.as_view(), name='company-add-interviewer'),
    path('job_lists/', JobLists.as_view(), name='job-lists'),
    path('job_lists/<int:pk>', JobListsApply.as_view(), name='job-apply'),
    path('after_apply/', AfterJobApply.as_view(), name='after-apply'),
    path('user_change_password/', UserChangePassword.as_view(), name='user-change-password'),
    path('interviewer_change_password/', InterviewerChangePassword.as_view(), name='interviewer-change-password'),
    path('company_change_password/', CompanyChangePassword.as_view(), name='company-change-password'),
    path('user_password_changed/', auth_view.LogoutView.as_view(template_name='user_login/user_password_changed.html'),
         name='user_password_changed'),
    path('interviewer_password_changed/',
         auth_view.LogoutView.as_view(template_name='user_login/interviewer_password_changed.html'),
         name='interviewer_password_changed'),
    path('company_password_changed/',
         auth_view.LogoutView.as_view(template_name='user_login/company_password_changed.html'),
         name='company_password_changed'),
    path('career/', CompanyCareer.as_view(), name='company-career'),
    path('job_applied/', UserAppliedJobs.as_view(), name='user-job-apply'),
    path('user_profile/', UserProfile.as_view(), name='user-profile'),
    path('interviewer_profile/', InterviewerProfile.as_view(), name='interviewer-profile'),
    path('interviewer_update_profile/', UpdateInterviewerDetails.as_view(), name='interviewer-update-profile'),
    path('show_interviewers/', ShowInterviewers.as_view(), name='show-interviewers'),
    path('user_update_profile/', UpdateUserDetails.as_view(), name='user-update-profile'),
    path('show_applicants/', ShowAppliedUser.as_view(), name='company-applicants'),
    path('career/<int:pk>', JobOpeningUpdate.as_view(), name='update-job'),
    path('show_accepted_applicants/', ShowAcceptedInterviewers.as_view(), name='show-accepted-applicants'),
    path('show_accepted_applicants/<int:pk>', ScheduleApplicantInterview.as_view(), name='technical-interview'),
    path('get_interviewers/', InterviewType.as_view(), name='get-interviewer'),
    path('get_time_slot/', GetTimeSlot.as_view(), name='get-time-slot'),
    path('show_interviewer_scheduled/', ShowInterviewerScheduled.as_view(), name='show-interviewer-scheduled'),
    path('applicant_details/<int:pk>', ApplicantDetails.as_view(), name='applicant_details'),
    path('detail_schedule/<int:pk>', ShowDetailSchedule.as_view(), name='detail-schedule'),
    path('interviewer_details/<int:pk>', DetailsInterviewer.as_view(), name='interviewer-details'),
    path('user_messages/', UserMessage.as_view(), name='user-messages'),
    path('interviewer_messages/', InterviewerMessage.as_view(), name='interviewer-messages'),
    path('company_messages/', CompanyMessage.as_view(), name='company-messages'),
    path('user_feedback/<int:pk>', UserFeedbackView.as_view(), name='user-feedback'),
    path('reschedule_req/<int:pk>', RescheduleRequest.as_view(), name='reschedule-request'),
    path('show_requests_reschedule/', ShowRescheduleRequests.as_view(), name='show-request-reschedule'),
    path('post_interview/<int:pk>', FeedbackOfInterviewer.as_view(), name='post-interview'),
    path('post_interview_applications/', PostInterviewProcess.as_view(), name='post-interview-application'),
    path('password-reset/', auth_view.PasswordResetView.as_view(template_name='user_login/password_reset.html'),
         name="password_reset"),
    path('password-reset/done/',
         auth_view.PasswordResetDoneView.as_view(template_name='user_login/password_reset_done.html'),
         name="password_reset_done"),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_view.PasswordResetConfirmView.as_view(template_name='user_login/password_reset_confirm.html'),
         name="password_reset_confirm"),
    path('password-reset-complete/',
         auth_view.PasswordResetCompleteView.as_view(template_name='user_login/password_reset_complete.html'),
         name="password_reset_complete"),
    path('deactivate/<int:pk>', DeactivateAccount.as_view(), name='deactivate'),
    path('reactivate/', ReactivateAccount.as_view(), name='reactivate'),
    path('reactivate/user_info/', ReactivationUser.as_view(), name='reactivation'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

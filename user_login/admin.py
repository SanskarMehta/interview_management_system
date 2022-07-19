from django.contrib import admin
from user_login.models import CustomUser, CompanyAcceptance, UserDetails, JobOpenings, InterviewerCompany, InterviewerType, InterviewerDetails, UserJobApplied, UserInterview, Interview, Notification, InterviewerFeedback, UserFeedback, RescheduleRequests, BlockUser

admin.register(CustomUser)
admin.register(CompanyAcceptance)
admin.register(UserDetails)
admin.register(JobOpenings)
admin.register(InterviewerCompany)
admin.register(InterviewerType)
admin.register(InterviewerDetails)
admin.register(UserJobApplied)
admin.register(UserInterview)
admin.register(Interview)
admin.register(Notification)
admin.register(InterviewerFeedback)
admin.register(UserFeedback)
admin.register(RescheduleRequests)
admin.register(BlockUser)

from django.contrib import admin
from user_login.models import CustomUser, CompanyAcceptance, UserDetails, InterviewerCompany, JobOpenings, InterviewerType, UserJobApplied

admin.site.register(CustomUser)
admin.site.register(CompanyAcceptance)
admin.site.register(UserDetails)
admin.site.register(InterviewerType)
admin.site.register(InterviewerCompany)
admin.site.register(JobOpenings)
admin.site.register(UserJobApplied)
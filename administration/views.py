from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView

from user_login.models import CustomUser, InterviewerDetails, CompanyAcceptance, UserDetails


class Home(TemplateView):
    template_name = 'administration/base.html'


class AdminLogin(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'administration/login.html')

    def post(self, request, *args, **kwargs):
        administrator = authenticate(
            username=request.POST['username'],
            password=request.POST['password'],
        )
        if administrator is not None:
            if administrator.is_superuser:
                login(request, administrator)
                return redirect('admin-home')
            else:
                messages.info(request, "You unable to access this site.")
                return redirect('admin-login')
        messages.info(request, "You unable to access this site because your credentials are wrong.")
        return render(request, 'administration/login.html')


class ShowInterviewers(View):
    def get(self, request, *args, **kwargs):
        interviewers = InterviewerDetails.objects.all()
        return render(request,'administration/ShowInterviewers.html',{'interviewers':interviewers})


class ShowUser(View):
    def get(self, request, *args, **kwargs):
        Users = CustomUser.objects.exclude(Q(is_company=True)|Q(is_interviewer=True)|Q(is_superuser=True))
        return render(request,'administration/ShowUsers.html',{'users':Users})


class ShowCompany(View):
    def get(self, request, *args, **kwargs):
        company = CompanyAcceptance.objects.select_related('company').all()
        return render(request,'administration/ShowUsers.html',{'company':company})


class DetailsOfUser(View):
    def get(self, request, *args, **kwargs):
        user_details = UserDetails.objects.get(user_id=kwargs['pk'])
        return render(request,'administration/DetailsUser.html',{'user_detail':user_details})


class DetailsOfInterviewer(View):
    def get(self, request, *args, **kwargs):
        interviewer_details = InterviewerDetails.objects.get(user_id=kwargs['pk'])
        return render(request,'administration/DetailsInterviewer.html',{'interviewer_details':interviewer_details})


class CompanyRegisterByAdmin(View):
    pass


class UserRegisterByAdmin(View):
    pass


class InterviewerRegisterByAdmin(View):
    pass




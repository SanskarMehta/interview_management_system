import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from user_login.forms import UpdateUserDetailForm, UserEmailUpdateForm
from user_login.models import CustomUser, InterviewerDetails, CompanyAcceptance, UserDetails, InterviewerCompany, \
    Notification, BlockUser


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
                return redirect('admin-after-login')
            else:
                messages.info(request, "You unable to access this site.")
                return redirect('admin-login')
        messages.info(request, "You unable to access this site because your credentials are wrong.")
        return render(request, 'administration/login.html')


class AdminAfterLogin(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'administration/admin_home.html')


class ShowInterviewers(View):
    def get(self, request, *args, **kwargs):
        interviewers = InterviewerDetails.objects.all()
        return render(request, 'administration/ShowInterviewers.html', {'interviewers': interviewers})


class ShowUser(View):
    def get(self, request, *args, **kwargs):
        Users = CustomUser.objects.filter(is_company=False, is_interviewer=False, is_superuser=False)
        return render(request, 'administration/ShowUsers.html', {'users': Users})


class ShowCompany(View):
    def get(self, request, *args, **kwargs):
        company = CompanyAcceptance.objects.select_related('company').all()
        return render(request, 'administration/ShowCompanies.html', {'companies': company})


class DetailsOfUser(View):
    def get(self, request, *args, **kwargs):
        user_details = UserDetails.objects.get(user_id=kwargs['pk'])
        return render(request, 'administration/DetailsUser.html', {'user_detail': user_details})


class DetailsOfInterviewer(View):
    def get(self, request, *args, **kwargs):
        interviewer_details = InterviewerDetails.objects.get(id=kwargs['pk'])
        company_name = InterviewerCompany.objects.get(interviewer=interviewer_details.interviewer)
        return render(request, 'administration/DetailsInterviewer.html',
                      {'interviewer_detail': interviewer_details, 'company': company_name.company.username})


class CompanyRegisterByAdmin(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'administration/user_register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']
        if password2 == password:
            if CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'Username is already is taken.')
                return redirect('company-register-admin')
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email is already exist.')
                return redirect('company-register-admin')
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password,
                                                      is_company=True)
                user.save()
                company_acceptance = CompanyAcceptance(company=user)
                company_acceptance.save()
                notification_message = username + "is a new company and it has registered in our portal.It wants to use our services."
                admin_notification = Notification.objects.create(sender=user, receiver=request.user,
                                                                 message=notification_message)
                admin_notification.save()
                return redirect('company-acceptance')
        else:
            return render(request, 'administration/user_register.html')


class UserRegisterByAdmin(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'administration/user_register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']
        if password2 == password:
            if CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'Username is already is taken.')
                return redirect('user-register-admin')
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email is already exist.')
                return redirect('user-register-admin')
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                user.save()
                return redirect('show-users')
        else:
            messages.info(request, 'Your passwords are not matched.')
            return render(request, 'administration/user_register.html')


class InterviewerRegisterByAdmin(View):
    pass


class CompanyAcceptanceByAdmin(View):
    def get(self, reqeust, *args, **kwargs):
        companies = CompanyAcceptance.objects.filter(is_accepted=False)
        return render(reqeust, 'administration/company_accept.html', {'companies': companies})


class AdminUpdateUserDetails(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = UpdateUserDetailForm(instance=request.user.userdetails)
        form2 = UserEmailUpdateForm(instance=request.user)
        return render(request, 'administration/admin_update_profile.html', {'form': form, 'form2': form2})

    def post(self, request, *args, **kwargs):
        form = UpdateUserDetailForm(request.POST, instance=request.user.userdetails)
        form2 = UserEmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if form2.is_valid():
                form2.save()
                # messages.success(request,'Succefully Updated the Values and Email')
                return redirect('admin-user-details', pk=request.user.id)
            else:
                # messages.success(request,'Succefully Updated the Values')
                return redirect('user-profile')
        else:
            return redirect('admin-update-profile')


@method_decorator(csrf_exempt, name='dispatch')
class BlockUnblock(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        request_data = request.read()
        form_data = json.loads(request_data.decode('utf-8'))
        user_id = form_data.get('user_id')
        block_status = form_data.get('data_status')
        if block_status == '1':
            message = form_data.get('message')
            block_user = CustomUser.objects.get(id=user_id)
            block_user.is_block = True
            block_user.save()
            user = CustomUser.objects.get(id=user_id)
            block = BlockUser.objects.create(user=user, reason=message)
            block.save()
        else:
            block_user = CustomUser.objects.get(id=user_id)
            block_user.is_block = False
            block_user.save()
        return JsonResponse({'message': 'Completed Successfully'})


@method_decorator(csrf_exempt,name='dispatch')
class CompanyAcceptReject(LoginRequiredMixin,View):
    def post(self,request, *args , **kwargs):
        form_data = request.read()
        request_data = json.loads(form_data.decode('utf-8'))
        company_id = request_data.get('company_id')
        print(company_id)
        acceptance_status = request_data.get('acceptance_status')
        print(acceptance_status)
        if acceptance_status == "0":
            Company=CompanyAcceptance.objects.get(id=int(company_id))
            Company.is_accepted = True
            Company.save()
        else:
            Company=CompanyAcceptance.objects.get(id=int(company_id))
            Company.is_accepted = False
            Company.save()
        return JsonResponse({'msg':'Thank You for choosing us'})
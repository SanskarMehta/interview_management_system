import os
from datetime import datetime
import json
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import permission_required
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import UpdateView, TemplateView
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser

from user_login.forms import UpdateUserDetailForm, UpdateInterviewerDetailForm, UserEmailUpdateForm, UpdateJobOpenings, \
    ScheduleInterviews, UserFeedbackByInterviewer
from user_login.models import CustomUser, CompanyAcceptance, UserDetails, InterviewerCompany, JobOpenings, \
    InterviewerType, InterviewerDetails, UserJobApplied, UserInterview, Interview, Notification, InterviewerFeedback, \
    RescheduleRequests, UserFeedback
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/base.html')


class UserLogin(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/login.html')

    def post(self, request, *args, **kwargs):
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password'],
        )
        if user is not None:
            if user.is_block == False:
                if user.is_activated == True:
                    if user.is_interviewer:
                        login(request, user)
                        if user.is_first_time:
                            return redirect('interviewer-details-form')
                        else:
                            return redirect('interviewer-home')
                    elif user.is_company:
                        company_accepted = CompanyAcceptance.objects.filter(company=user).get()
                        if company_accepted.is_accepted:
                            login(request, user)
                            return redirect('company-home')
                        else:
                            messages.info(request,
                                          'Your company is not accepted from the admin side. You can login after accepted by admin.')
                            return redirect('login')
                    else:
                        login(request, user)
                        if user.is_first_time:
                            print(user.id)
                            return redirect('user-details-form')
                        else:
                            return redirect('user-home')
                else:
                    messages.info(request, 'Your account is deactivated. Please reactivate your account. ')
                    return redirect('login')
            else:
                messages.info(request, "Your account is blocked by admin. Please call on number : 129121####.")
                return redirect('login')
        else:
            messages.info(request, 'You unable to register because credentials are not matching')
            return render(request, 'user_login/login.html')


class UserRegister(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']
        if password2 == password:
            if CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'Username is already is taken.')
                return redirect('user-register')
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email is already exist.')
                return redirect('user-register')
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                user.save()
                return redirect('login')
        else:
            messages.info(request, 'Your passwords are not matched.')
            return render(request, 'user_login/register.html')


class InterviewerHome(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/interviewer_home.html')


class UserHome(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/user_home.html')


class CompanyHome(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/company_home.html')


class CompanyRegister(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/company_register.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']
        if password2 == password:
            if CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'Username is already is taken.')
                return redirect('company-register')
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email is already exist.')
                return redirect('company-register')
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password,
                                                      is_company=True)
                user.save()
                company_acceptance = CompanyAcceptance(company=user)
                company_acceptance.save()
                notification_message = username + "is a new company and it has registered in our portal.It wants to use our services."
                admin_notification = Notification.objects.create(sender=user, receiver='admin',
                                                                 message=notification_message)
                admin_notification.save()
                return redirect('login')
        else:
            return render(request, 'user_login/company_register.html')


class UserDetailsForm(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/user_details_form.html')

    def post(self, request, *args, **kwargs):
        user_phone = request.POST['mobilenumber']
        user_technology = request.POST['technology']
        user_10th_marks = request.POST['marks_10th']
        user_12th_marks = request.POST['marks_12th']
        user_CPI = request.POST['cpi']
        user_CV = request.FILES['cvfile']

        if float(user_10th_marks) <= 100 and float(user_12th_marks) <= 100 and float(user_CPI) <= 10:
            if user_CV.content_type == 'application/pdf' or user_CV.content_type == 'application/msword':
                userdetails = UserDetails.objects.create(user=request.user, user_phone=user_phone,
                                                         user_technology=user_technology,
                                                         user_10th_marks=user_10th_marks,
                                                         user_12th_marks=user_12th_marks, user_CPI=user_CPI,
                                                         user_CV=user_CV)
                userdetails.save()
                user = CustomUser.objects.get(id=request.user.id)
                user.is_first_time = False
                user.save()
                return redirect('user-home')
            else:
                messages.info(request, "Please Upload .PDF or .DOC file")
                return render(request, 'user_login/user_details_form.html')
        else:
            messages.info(request, "Your result must be less than or equal to 100")
            return render(request, 'user_login/user_details_form.html')


class CompanyJobOpenings(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = request.user.username
        return render(request, 'user_login/company_job_opening.html', {'company': company})

    def post(self, request, *args, **kwargs):
        job_location = request.POST['job_location']
        job_role = request.POST['job_role']
        description = request.POST['description']
        job_open = JobOpenings.objects.create(company=request.user, job_location=job_location, job_role=job_role,
                                              description=description)
        job_open.save()
        messages = 'new job is added to ' + request.user.username + ". It is related to " + job_role + "."
        users = CustomUser.objects.filter(is_interviewer=False, is_company=False)
        for user in users:
            notification_message = Notification.objects.create(sender=request.user, receiver=user,
                                                               message=messages)
            notification_message.save()
        return redirect('company-career')


class CompanyAddInterviewer(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = request.user.username
        return render(request, 'user_login/company_add_interviewer.html', {'company': company})

    def post(self, request, *args, **kwargs):
        company = request.user
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']
        if password == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'Username is already is taken.')
                return redirect('company-add-interviewer')
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email is already exist.')
                return redirect('company-add-interviewer')
            else:
                interviewer = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                             is_interviewer=True)
                interviewer.save()
                interviewer_company = InterviewerCompany.objects.create(company=company, interviewer=interviewer)
                interviewer_company.save()
                email_message = 'Hiii \n I am sending your credentials of portal login and after login please fill your details and if you want then please change your password also.\nThank You.\n ID: ' + email + " Password: " + password + "."
                print(request.user.email)
                a = send_mail('Interviewer Credentials', email_message, request.user.email, [email],
                              fail_silently=False, )
                print(a)
                return redirect('show-interviewers')
        else:
            messages.info(request, "Your password's are not matching so you unable to create account.")
            return redirect('company-add-interviewer')
        company = request.user.username
        return render(request, 'user_login/company_add_interviewer.html', {'company': company})


class InterviewerDetailsForm(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        InterviewerTypes = InterviewerType.objects.all()
        list1 = []
        for i in InterviewerTypes:
            list1.append(i.type)
        return render(request, 'user_login/interviewer_details_form.html', {'interviewer_type': list1})

    def post(self, request, *args, **kwargs):
        InterviewerTypes = InterviewerType.objects.all()
        list1 = []
        for i in InterviewerTypes:
            list1.append(i.type)
        phone_number = request.POST['mobilenumber']
        technology = request.POST['technology']
        job_role = request.POST['job_role']
        experience = request.POST['experience']
        type_of_interviewer_str = request.POST['interviewer_type']
        # print(type(type_of_interviewer_str))
        type_of_interviewer = InterviewerType.objects.get(type=type_of_interviewer_str)
        interviewer = InterviewerDetails.objects.create(interviewer=request.user, type_interviewer=type_of_interviewer,
                                                        interviewer_phone=phone_number,
                                                        interviewer_technology=technology, job_role=job_role,
                                                        Experience=experience)
        interviewer.save()
        user = CustomUser.objects.get(id=request.user.id)
        user.is_first_time = False
        user.save()
        return redirect('interviewer-home')


class JobLists(LoginRequiredMixin, View):


    def get(self, request, *args, **kwargs):
        job_lists = JobOpenings.objects.all()
        return render(request, 'user_login/job_lists.html', {'job_lists': job_lists})


class JobListsApply(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        job_lists = JobOpenings.objects.all()
        print(self.kwargs)
        id1 = self.kwargs['pk']
        company = JobOpenings.objects.get(id=id1)
        if company is not None:
            job_application = UserJobApplied.objects.create(user=request.user, job=company)
            job_application.save()
            notification_message = request.user.username + ' is applied in your company.'
            admin_message = Notification.objects.create(sender=request.user, receiver=company.company,
                                                        message=notification_message)
            admin_message.save()
            return render(request, 'user_login/after_apply.html', {'username': request.user.username})
        return render(request, 'user_login/job_lists.html', {'job_lists': job_lists})


class AfterJobApply(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return render(request, 'user_login/after_apply.html', {'Username': username})


class UserChangePassword(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return render(request, 'user_login/user_change_password.html', {'username': username})

    def post(self, request, *args, **kwargs):
        new_password = request.POST['new_password']
        confirm_password = request.POST['password2']
        old_password = request.POST['old_password']
        auth_user = authenticate(
            username=request.user.username,
            password=old_password,
        )
        if auth_user is not None:
            if new_password == confirm_password:
                user_id = request.user.id
                user = CustomUser.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                return redirect('user_password_changed')
            else:
                messages.info(request, 'Your passwords are not matching so.')
                return render(request, 'user_login/user_change_password.html', {'username': request.user.username})
        messages.info(request, 'Please enter the valid credentials')
        return render(request, 'user_login/user_change_password.html', {'username': request.user.username})


class CompanyChangePassword(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return render(request, 'user_login/company_change_password.html', {'username': username})

    def post(self, request, *args, **kwargs):
        new_password = request.POST['new_password']
        confirm_password = request.POST['password2']
        old_password = request.POST['old_password']
        auth_user = authenticate(
            username=request.user.username,
            password=old_password,
        )
        if auth_user is not None:
            if new_password == confirm_password:
                user_id = request.user.id
                user = CustomUser.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                return redirect('company_password_changed')
            else:
                messages.info(request, 'Your passwords are not matching so.')
                return render(request, 'user_login/company_change_password.html', {'username': request.user.username})
        messages.info(request, 'Please enter the valid credentials')
        return render(request, 'user_login/company_change_password.html', {'username': request.user.username})


class InterviewerChangePassword(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        username = request.user.username
        return render(request, 'user_login/interviewer_change_password.html', {'username': username})

    def post(self, request, *args, **kwargs):
        new_password = request.POST['new_password']
        confirm_password = request.POST['password2']
        old_password = request.POST['old_password']
        auth_user = authenticate(
            username=request.user.username,
            password=old_password,
        )
        if auth_user is not None:
            if new_password == confirm_password:
                user_id = request.user.id
                user = CustomUser.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                return redirect('interviewer_password_changed')
            else:
                messages.info(request, 'Your passwords are not matching so.')
                return render(request, 'user_login/interviewer_change_password.html',
                              {'username': request.user.username})
        messages.info(request, 'Please enter the valid credentials')
        return render(request, 'user_login/interviewer_change_password.html', {'username': request.user.username})


class CompanyCareer(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        jobs = JobOpenings.objects.filter(company=request.user)
        return render(request, 'user_login/company_career.html', {'jobs': jobs})

    def delete(self, request):
        request_data = request.read()
        form_data = json.loads(request_data.decode('utf-8'))
        job_id = form_data.get("job_id")
        job_delete = JobOpenings.objects.get(id=job_id)
        job_delete.delete()
        return JsonResponse({"success": True, "message": "Job Deleted Successfully"})


class UserAppliedJobs(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        jobs = UserJobApplied.objects.filter(user=request.user)
        return render(request, 'user_login/user_job_applied.html', {'jobs': jobs})


class UserProfile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_details = UserDetails.objects.filter(user=request.user)
        return render(request, 'user_login/user_profile.html', {'user_details': user_details})


class InterviewerProfile(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company_name = InterviewerCompany.objects.get(interviewer=request.user)
        interviewer_details = InterviewerDetails.objects.filter(interviewer=request.user)
        return render(request, 'user_login/interviewer_profile.html',
                      {'interviewer_details': interviewer_details, 'company': company_name.company.username})


@method_decorator(csrf_exempt, name='dispatch')
class ShowInterviewers(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        interviewers = InterviewerCompany.objects.select_related("interviewer").filter(company=request.user)
        interviewer_list = []
        for interview in interviewers:
            data = {'name': interview.interviewer.username, 'email': interview.interviewer.email,
                    'id': interview.interviewer_id}
            try:
                interview_details = InterviewerDetails.objects.get(interviewer_id=interview.interviewer_id)
                data["interviewer_phone"] = interview_details.interviewer_phone
                data["interviewer_technology"] = interview_details.interviewer_technology
                data["type_interviewer"] = interview_details.type_interviewer.type
                data["job_role"] = interview_details.job_role
                data["Experience"] = interview_details.Experience
            except InterviewerDetails.DoesNotExist as err:
                data["interviewer_phone"] = 'Not Available'
                data["interviewer_technology"] = 'Not Available'
                data["type_interviewer"] = 'Not Available'
                data["job_role"] = 'Not Available'
                data["Experience"] = 'Not Available'
                pass
            interviewer_list.append(data)
        return render(request, 'user_login/show_interviewers.html', {'interviewer_details': interviewer_list})

    def delete(self, request):
        request_data = request.read()
        form_data = json.loads(request_data.decode('utf-8'))
        interview_id = form_data.get("interviewer_id")
        custom_user_model = CustomUser.objects.get(id=interview_id)
        custom_user_model.delete()
        return JsonResponse({"success": True, "message": "Interviewer Deleted Successfully"})


class UpdateUserDetails(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = UpdateUserDetailForm(instance=request.user.userdetails)
        form2 = UserEmailUpdateForm(instance=request.user)
        return render(request, 'user_login/user_update_profile.html', {'form': form, 'form2': form2})

    def post(self, request, *args, **kwargs):
        form = UpdateUserDetailForm(request.POST, instance=request.user.userdetails)
        form2 = UserEmailUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if form2.is_valid():
                form2.save()
                # messages.success(request,'Succefully Updated the Values and Email')
                return redirect('user-profile')
            else:
                # messages.success(request,'Succefully Updated the Values')
                return redirect('user-profile')
        else:
            return redirect('user-update-profile')


class UpdateInterviewerDetails(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form1 = UpdateInterviewerDetailForm(instance=request.user.interviewerdetails)
        form2 = UserEmailUpdateForm(instance=request.user)
        return render(request, 'user_login/interviewer_update_profile.html', {'form1': form1, 'form2': form2})

    def post(self, request, *args, **kwargs):
        form1 = UpdateInterviewerDetailForm(request.POST, instance=request.user.interviewerdetails)
        form2 = UserEmailUpdateForm(request.POST, instance=request.user)
        if form1.is_valid():
            form1.save()
            if form2.is_valid():
                form2.save()
                # messages.success(request,'Succesfully Updated the Email and other fields')
                return redirect('interviewer-profile')
            else:
                # messages.success(request,'Succefully changed the values')
                return redirect('interviewer-profile')
        else:
            return redirect('interviewer-update-profile')


class ShowAppliedUser(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        applicants = UserJobApplied.objects.select_related('job', 'user').filter(job__company=request.user)
        applicant_details = []
        for applicant in applicants:
            if applicant.application_status == "Pending":
                status = applicant.application_status
                alert_class = "alert-warning"
            elif applicant.application_status == "Accepted":
                status = applicant.application_status
                alert_class = "alert-success"
            elif applicant.application_status == "Rejected":
                status = applicant.application_status
                alert_class = "alert-danger"

            data = {'name': applicant.user.username, 'email': applicant.user.email,
                    'application_status': applicant.application_status, 'job_role': applicant.job.job_role,
                    'id': applicant.id, "status": status, "alert_class": alert_class}
            try:
                user_details = UserDetails.objects.get(user_id=applicant.user_id)
                data['user_12th_marks'] = user_details.user_12th_marks
                data['user_10th_marks'] = user_details.user_10th_marks
                data['user_CPI'] = user_details.user_CPI
                data['user_technology'] = user_details.user_technology
                data['user_phone'] = user_details.user_phone
                data['user_CV'] = user_details.user_CV
            except UserDetails.DoesNotExist as err:
                print(err)
            applicant_details.append(data)
        return render(request, 'user_login/show_applied_user.html', {'applicants': applicant_details})

    def post(self, request, *args, **kwargs):
        user_application_id = request.POST.get("user_applied_job_id")
        data_status = request.POST.get("data-status")
        if data_status == '1':
            user_application = UserJobApplied.objects.get(id=user_application_id)
            user_application.application_status = "Rejected"
            user_application.save()
            user_job_accepted_application = UserInterview.objects.get(job_application=user_application)
            notification_message = 'Your application is Rejected. We are unable to shortlist your CV. Beacuse it is ' \
                                   'not matching as per our requirements. '
            admin_message = Notification.objects.create(sender=request.user, receiver=user_application.user,
                                                        message=notification_message)
            admin_message.save()
            if user_job_accepted_application is not None:
                user_job_accepted_application.delete()
        else:
            user_application = UserJobApplied.objects.get(id=user_application_id)
            user_application.application_status = "Accepted"
            user_application.save()
            user_job_accepted_application = UserInterview.objects.create(job_application=user_application)
            user_job_accepted_application.save()
            notification_message = 'Your application is accepted. We will reach out to you sortly.'
            admin_message = Notification.objects.create(sender=request.user, receiver=user_application.user,
                                                        message=notification_message)
            admin_message.save()
        return JsonResponse({'success': True, 'message': 'Interviewer Deleted Successfully'})


class JobOpeningUpdate(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = JobOpenings.objects.filter(id=self.kwargs['pk']).first()
        form1 = UpdateJobOpenings(instance=company)
        return render(request, 'user_login/company_job_openings_update.html', {'form1': form1})

    def post(self, request, *args, **kwargs):
        company = JobOpenings.objects.filter(id=self.kwargs['pk']).first()
        form1 = UpdateJobOpenings(request.POST, instance=company)
        if form1.is_valid():
            form1.save()
            messages = 'Existing job is updated in ' + request.user.username + "."
            users = CustomUser.objects.filter(is_interviewer=False, is_company=False)
            for user in users:
                notification_message = Notification.objects.create(sender=request.user, receiver=user,
                                                                   message=messages)
                notification_message.save()
            return redirect('company-career')
        return render(request, 'user_login/company_job_openings_update.html', {'form1': form1})


class ShowAcceptedInterviewers(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        applicants = UserInterview.objects.filter(job_application__job__company=request.user)
        return render(request, 'user_login/schedule_interviews.html', {'applicants': applicants})


class ScheduleApplicantInterview(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form1 = ScheduleInterviews(request.GET)
        return render(request, 'user_login/technical_interview_form.html', {'form': form1, 'pk': kwargs.get('pk')})

    def post(self, request, *args, **kwargs):
        form = ScheduleInterviews(request.POST)
        interview_type = form.data['type_interview']
        interview_type = InterviewerType.objects.get(id=int(interview_type))
        date_interview1 = form.data['interview_date']
        date_interview1 = datetime.strptime(date_interview1, '%m/%d/%Y')
        date_interview = date_interview1.strftime('%Y-%m-%d')
        interviewer = form.data['interviewer']
        time_interview = form.data['interview_time']
        interviewer = InterviewerDetails.objects.get(interviewer_id=int(interviewer))
        id = kwargs.get('pk')
        application = UserInterview.objects.get(id=id)
        schedule = Interview.objects.create(application=application, type_interview=interview_type,
                                            interviewer=interviewer, interview_date=date_interview,
                                            interview_time=time_interview)
        schedule.save()
        if form.data['type_interview'] == '4':
            application.HR_round = 'Scheduled'
        else:
            application.technical_round = 'Scheduled'
        application.save()
        if form.data['type_interview'] == '4':
            notification_message = 'Your HR interview is scheduled. To know more about it please check your ' \
                                   'application status. '
            email_subject = "HR Interview Schedule"
            email_message = "Your HR interview is scheduled on Date : " + date_interview + " Time: " + time_interview + "."
        else:
            notification_message = 'Your Technical interview is scheduled. To know more about it please check your ' \
                                   'application status. '
            email_subject = "Technical Interview Schedule"
            email_message = "Your Technical interview is scheduled on Date : " + date_interview + " Time: " + time_interview + "."
        # print(application.job_application.user)
        message = Notification.objects.create(sender=request.user, receiver=application.job_application.user,
                                              message=notification_message)
        message.save()
        message = Notification.objects.create(sender=request.user, receiver=interviewer.interviewer,
                                              message=notification_message)
        message.save()
        user_email = application.job_application.user.email
        interviewer_email = interviewer.interviewer.email
        print(request.user.email)
        a = send_mail(email_subject, email_message, request.user.email, [user_email, interviewer_email],
                      fail_silently=False, )
        print(a)
        return redirect('show-accepted-applicants')


@method_decorator(csrf_exempt, name='dispatch')
class InterviewType(View):
    def post(self, request, *args, **kwargs):
        request_data = request.read()
        form_data = json.loads(request_data.decode('utf-8'))
        type_interview_id = form_data.get("type_interview_id")
        interviewers = InterviewerCompany.objects.filter(company_id=request.user.id)
        interviewers_list = []
        for interviewer in interviewers:
            examiners = InterviewerDetails.objects.select_related('interviewer').filter(
                interviewer=interviewer.interviewer, type_interviewer_id=type_interview_id)
            for examiner in examiners:
                print('id', examiner.interviewer.id)
                print('username', examiner.interviewer.username)
                data = {'id': examiner.interviewer.id, 'username': examiner.interviewer.username}
                interviewers_list.append(data)
        return JsonResponse({"success": True, 'interviewers': interviewers_list})


@method_decorator(csrf_exempt, name='dispatch')
class GetTimeSlot(View):
    def post(self, request, *args, **kwargs):
        time_slots = ['09:00–09:30', '10:00–10:30', '11:00–11:30', '12:00–12:30', '13:00–13:30',
                      '14:00–14:30', '15:00–15:30', '16:00–16:30', '17:00–17:30']
        request_data = request.read()
        form_data = json.loads(request_data.decode('utf-8'))
        interviewer_id = form_data.get("interviewer_id")
        sch_date = form_data.get("sch_date")
        applicant = form_data.get('applicant_id')
        date_interview1 = datetime.strptime(sch_date, '%m/%d/%Y')
        sch_date = date_interview1.strftime('%Y-%m-%d')
        interviewer = InterviewerDetails.objects.get(interviewer_id=int(interviewer_id))
        interview_timings = Interview.objects.filter(
            Q(interview_date=sch_date, interviewer=interviewer) | Q(application_id=int(applicant)))
        timing_list = []
        for time1 in interview_timings:
            print(time1.interview_time)
            timing_list.append(time1.interview_time)
        final_time_slot = list(set(time_slots) - set(timing_list))
        return JsonResponse({'final_time_slot': final_time_slot})


class ShowInterviewerScheduled(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        interviewer = InterviewerDetails.objects.get(interviewer=request.user)
        interview_schedule = Interview.objects.filter(interviewer=interviewer)
        return render(request, 'user_login/interviewer_schedule.html', {'interview_schedule': interview_schedule})


class ApplicantDetails(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        applicant_details = UserInterview.objects.get(id=kwargs['pk'])
        user_details = UserDetails.objects.select_related('user').get(user_id=applicant_details.job_application.user_id)
        job_application = JobOpenings.objects.get(id=applicant_details.job_application.job_id)
        return render(request, 'user_login/application_details.html',
                      {'user_detail': user_details, 'job_application': job_application})


class ShowDetailSchedule(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_interview = UserInterview.objects.get(job_application_id=kwargs['pk'])
        print(user_interview)
        interviews = Interview.objects.filter(application=user_interview)
        print(interviews)
        return render(request, 'user_login/detail_interview_schedule.html', {'interviews': interviews})


class DetailsInterviewer(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        interviewer_detail = InterviewerDetails.objects.get(id=kwargs['pk'])
        company_name = InterviewerCompany.objects.get(interviewer_id=interviewer_detail.interviewer.id)
        return render(request, 'user_login/interviewer_details.html',
                      {'interviewer_detail': interviewer_detail, 'company': company_name.company.username})


class UserMessage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages = Notification.objects.filter(receiver=request.user)
        return render(request, 'user_login/user_messages.html', {'messages': messages})


class InterviewerMessage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages = Notification.objects.filter(receiver=request.user)
        return render(request, 'user_login/interviewer_messages.html', {'messages': messages})


class CompanyMessage(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        messages = Notification.objects.filter(receiver=request.user)
        return render(request, 'user_login/company_messages.html', {'messages': messages})


class UserFeedbackView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        interviewer = InterviewerDetails.objects.get(id=kwargs['pk'])
        return render(request, 'user_login/user_feedback.html',
                      {'interviewer': interviewer.interviewer, 'user': request.user})

    def post(self, request, *args, **kwargs):
        interviewer = InterviewerDetails.objects.get(id=kwargs['pk'])
        feedback = request.POST['feedback']
        user = request.user
        interviewer_feedback = InterviewerFeedback.objects.create(applicant=user, interviewer=interviewer.interviewer,
                                                                  feedback=feedback)
        interviewer_feedback.save()
        message = 'One feedback is provided to you'
        notification_message = Notification.objects.create(sender=user, receiver=interviewer.interviewer,
                                                           message=message)
        notification_message.save()
        return redirect('user-job-apply')


class FeedbackOfInterviewer(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        application = UserInterview.objects.get(id=kwargs['pk'])
        form = UserFeedbackByInterviewer
        return render(request, 'user_login/post_interview.html',
                      {'form': form, 'interviewer': request.user, 'application': application})

    def post(self, request, *args, **kwargs):
        form = UserFeedbackByInterviewer(request.POST)
        print(request.POST)
        if form.is_valid():
            application_id = request.POST.get('application')
            application = UserInterview.objects.get(id=application_id)
            username = request.POST.get('user')
            user = CustomUser.objects.get(username=username)
            interviewer = request.user
            marks = form.data['marks']
            feedback = form.data['feedback']
            user_process = UserFeedback.objects.create(examiner=interviewer, user=user, feedback=feedback,
                                                       marks=marks, application=application)
            user_process.save()
            application = UserInterview.objects.get(id=kwargs['pk'])
            interviewer = InterviewerDetails.objects.get(interviewer=request.user)
            if interviewer.type_interviewer_id == 4:
                application.HR_round = request.POST.get('application_status')
                application.save()
            else:
                application.technical_round = request.POST.get('application_status')
                application.save()
            return redirect('post-interview-application')
        else:
            return redirect('post-interview')


class RescheduleRequest(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/reschedule_request.html',
                      {'user': request.user, 'application': kwargs['pk']})

    def post(self, request, *args, **kwargs):
        user = request.user
        application_id = kwargs['pk']
        application = UserInterview.objects.get(id=application_id)
        type = request.POST['reschedule_type']
        reason = request.POST['reschedule_reason']
        request_rescheduling = RescheduleRequests.objects.create(user=user, application=application,
                                                                 interview_type=type, reason=reason)
        request_rescheduling.save()
        return redirect('detail-schedule', pk=application.job_application_id)


class ShowRescheduleRequests(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        reschedule = RescheduleRequests.objects.filter(application__job_application__job__company=request.user)
        return render(request, 'user_login/show_reschedule_request.html', {'reschedule_requests': reschedule})


class PostInterviewProcess(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        interviewer = InterviewerDetails.objects.get(interviewer=request.user)
        if interviewer.type_interviewer_id == 4:
            interviews = Interview.objects.select_related('application').filter(
                interviewer__interviewer=request.user).exclude(application__HR_round='Scheduled')
        else:
            interviews = Interview.objects.select_related('application').filter(
                interviewer__interviewer=request.user).exclude(
                Q(application__technical_round='Scheduled') | Q(application__technical_round='Rejected'))
        return render(request, 'user_login/post_interview_applicants.html', {'interviews': interviews})


class DeactivateAccount(View):
    def get(self, request, *args, **kwargs):
        print(kwargs['pk'])
        CustomUser.objects.filter(id=kwargs['pk']).update(is_activated=False)
        logout(request)
        return redirect('login')


class ReactivateAccount(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/reactivate.html')

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        domain = request.build_absolute_uri('/')[:-1]
        url = f"{domain}/reactivate/user_info/"
        send_mail('Reactivate Your Account', url, from_email=os.getenv('EMAIL_HOST_USER'),recipient_list=[email], fail_silently=False, )
        return redirect('login')


class ReactivationUser(View):
    def get(self, request, *args, **kwargs):
        return render(request,'user_login/reactivation_page.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username , password=password)
        if user is not None:
            user_status = CustomUser.objects.get(id=user.id)
            user_status.is_activated = True
            user_status.save()
            return redirect('login')
        else:
            return redirect('')
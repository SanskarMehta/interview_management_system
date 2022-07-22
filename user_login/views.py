import os
from datetime import datetime
import json
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from user_login.custommixin import UserLoginRequiredMixin, InterviewerLoginRequiredMixin, CompanyLoginRequiredMixin
from user_login.forms import UpdateUserDetailForm, UpdateInterviewerDetailForm, UserEmailUpdateForm, UpdateJobOpenings, \
    ScheduleInterviews, UserFeedbackByInterviewer, RescheduleTime
from user_login.models import CustomUser, CompanyAcceptance, UserDetails, InterviewerCompany, JobOpenings, \
    InterviewerType, InterviewerDetails, UserJobApplied, UserInterview, Interview, Notification, InterviewerFeedback, \
    RescheduleRequests, UserFeedback


class HomeView(View):
    """
    This view is used for representing the welcome page of Interview Management System.
    This is the first page with which user interacts first.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/base.html')


@method_decorator(never_cache, name='dispatch')
class UserLogin(View):
    """
    This is used for login by the different type of users
    username -> str : It is a variable which is used to get the username from the html
    password -> str : It is a variable which is used to get the password from the html
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_interviewer:
                if request.user.is_first_time:
                    return redirect('interviewer-details-form')
                else:
                    return redirect('interviewer-home')
            elif request.user.is_company:
                return redirect('company-home')
            else:
                if request.user.is_first_time:
                    return redirect('user-details-form')
                else:
                    return redirect('user-home')
        return render(request, 'user_login/login.html')

    def post(self, request, *args, **kwargs):
        user = authenticate(
            username=request.POST['username'],
            password=request.POST['password'],
        )
        if user is not None:
            if not user.is_block:
                if user.is_activated:
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
                            return render(request, 'user_login/login.html')
                    else:
                        login(request, user)
                        if user.is_first_time:
                            return redirect('user-details-form')
                        else:
                            return redirect('user-home')
                else:
                    messages.info(request, 'Your account is deactivated. Please reactivate your account. ')
                    return render(request, 'user_login/login.html')
            else:
                messages.info(request, "Your account is blocked by admin. Please call on number : 129121####.")
                return render(request, 'user_login/login.html')
        else:
            messages.info(request, 'You unable to login because credentials are not matching')
            return render(request, 'user_login/login.html')


class UserRegister(View):
    """
    This view is used to register a new user to Interview Management System.
    username -> str : It holds the username which is retrieved from the html side.
    email -> str : It holds the email which is retrieved from the html side.
    password -> str : It holds the password which is retrieved from the html side.
    password2 -> str : It holds the confirm-password which is retrieved from the html side.
    """
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
                return render(request, 'user_login/register.html')
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email is already exist.')
                return render(request, 'user_login/register.html')
            else:
                user = CustomUser.objects.create_user(username=username, email=email, password=password)
                user.save()
                return redirect('login')
        else:
            messages.info(request, 'Your passwords are not matched.')
            return render(request, 'user_login/register.html')


class InterviewerHome(InterviewerLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/interviewer_home.html', {'interviewer': request.user})


class UserHome(UserLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/user_home.html', {'user': request.user})


class CompanyHome(CompanyLoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/company_home.html', {'company': request.user})


class CompanyRegister(View):
    """
    This view is used to register a new company.
    username -> str : It holds the username which is retrieved from the html side.
    email -> str : It holds the email which is retrieved from the html side.
    password -> str : It holds the password which is retrieved from the html side.
    password2 -> str : It holds the confirm-password which is retrieved from the html side.
    user -> object : It is an object which is created to save data in CustomUser Model
    company_acceptance -> object : It is an object which creates an entry in CompanyAcceptance table which is used by
                                   Admin to approve the company
    """
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
                notification_message = username + "is a new company and it has registered in our portal.It wants to "

                admins = CustomUser.objects.filter(is_superuser=True)
                for admin in admins:
                    admin_notification = Notification.objects.create(sender=user, receiver=admin,
                                                                     message=notification_message)
                    admin_notification.save()
                return redirect('login')
        else:
            messages.info(request,'Your passwords are not matched.')
            return render(request, 'user_login/company_register.html')


class UserDetailsForm(UserLoginRequiredMixin, View):
    """
    This is the view which is used to take data of user when he login for the very first time.
    user_phone -> str : It holds the data of mobile number which is entered on HTML by user
    user_technology -> str : It holds the data of technology which is entered on HTML by user
    user_10th_marks -> float : It holds the marks of 10th standard which is entered on HTML by user
    user_12th_marks -> float : It holds the marks of 12th standard which is entered on HTML by user
    user_CPI -> float : It holds the CPi of college which is entered on HTML by user
    user_CV -> FormField : It holds the CV of user which is uploaded by the user.
    """
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


class CompanyJobOpenings(CompanyLoginRequiredMixin, View):
    """
    This view is used by the company to create a new job opening in their company.
    job_location -> str : It holds the data of Location of Job which is submitted in the HTML.
    job_role -> str : It holds the role of Job which is submitted in the HTML.
    description -> str : It consists the description related to Job
    job_open -> object : It is an object which stores the all the data related to JobOpenings model.
    messages -> str : It is a variable which holds the data related to send notification to users.
    company -> str : It is a variable which holds the name of the current logged in company.
    """
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


class CompanyAddInterviewer(CompanyLoginRequiredMixin, View):
    """
    This view is used to add new Interviewer in the company.
    company -> str : It is a variable which holds the name of the current logged in company.
    username -> str : It holds the username which is retrieved from the html side.
    email -> str : It holds the email which is retrieved from the html side.
    password -> str : It holds the password which is retrieved from the html side.
    password2 -> str : It holds the confirm-password which is retrieved from the html side.
    interviewer -> object : It holds the value of interviewer and save the data in CustomUser model.
    email_message -> str : It holds the credentials of interviewer and used in send_email() to share with particular
                           user for login.
    """
    def get(self, request, *args, **kwargs):
        company = request.user.username
        return render(request, 'user_login/company_add_interviewer.html', {'company': company})

    def post(self, request, *args, **kwargs):
        company = request.user
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['confirm_password']
        company_name = request.user.username
        if password == password2:
            if CustomUser.objects.filter(username=username).exists():
                messages.info(request, 'Username is already is taken.')
                return render(request, 'user_login/company_add_interviewer.html', {'company': company_name})
            elif CustomUser.objects.filter(email=email).exists():
                messages.info(request, 'Email is already exist.')
                return render(request, 'user_login/company_add_interviewer.html', {'company': company_name})
            else:
                interviewer = CustomUser.objects.create_user(username=username, password=password, email=email,
                                                             is_interviewer=True)
                interviewer.save()
                interviewer_company = InterviewerCompany.objects.create(company=company, interviewer=interviewer)
                interviewer_company.save()
                email_message = 'Hiii \n I am sending your credentials of portal login and after login please fill your details and if you want then please change your password also.\nThank You.\n ID: ' + email + " Password: " + password + "."
                send_mail('Interviewer Credentials', email_message, request.user.email, [email],
                          fail_silently=False, )
                return redirect('show-interviewers')
        else:
            messages.info(request, "Your password's are not matching so you unable to create account.")
            return render(request, 'user_login/company_add_interviewer.html', {'company': company_name})


class InterviewerDetailsForm(InterviewerLoginRequiredMixin, View):
    """
    This view is used for collecting information of Interviewer , when they log in for very first time.
    InterviewerTypes -> objects : It is a collection of objects which are used to display a drop-down of
                        different types of Interviewer.
    phone_number -> str : It is a variable which holds the phone number which is retrieved from HTML.
    technology -> str : It is a variable which holds the technology which is retrieved from HTML.
    job_role -> str : It is a variable which holds the job_role which is retrieved from HTML.
    experience -> str : It is a variable which holds the experience which is retrieved from HTML.
    type_of_interviewer -> object :  It is an object which holds the interview type,which is retrieved from HTML.
    """
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


class JobLists(UserLoginRequiredMixin, View):
    """
    This is a view which is used to display all the posted jobs of different companies to the users.
    job_lists -> object : It is a collection of Jobs of JobOpening model.
    """
    def get(self, request, *args, **kwargs):
        job_lists = JobOpenings.objects.all()
        return render(request, 'user_login/job_lists.html', {'job_lists': job_lists})


class JobListsApply(UserLoginRequiredMixin, View):
    """
    This is a view which is used to display all the posted jobs of different companies to the users.
    job_lists -> object : It is a collection of Jobs of JobOpening model.
    id1 -> int : It is an id of JobOpenings, using which specific Job Post is identified.
    company -> object : It stores the specific job opening related to object.
    notification_message -> str : It is a variable which stores the message which is used to send as notification
                                  to other users.
    admin_ message -> object : It is used to store notification data in Notification model.
    """
    def get(self, request, *args, **kwargs):
        job_lists = JobOpenings.objects.all()
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


class UserChangePassword(UserLoginRequiredMixin, View):
    """
    This view is used to change the password of user.
    username -> str : It holds the name of the current user
    new_password -> str : It holds the new password of the user
    confirm_password -> str : It stores the re-entered new password of the user
    old_password -> str : It stores the old-password of user , which is used to authenticate.
    """
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


class CompanyChangePassword(CompanyLoginRequiredMixin, View):
    """
    This view is used to change the password of company.
    username -> str : It holds the name of the current logged in company.
    new_password -> str : It holds the new password of the company.
    confirm_password -> str : It stores the re-entered new password of the company.
    old_password -> str : It stores the old-password of company, which is used to authenticate.
    """
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


class InterviewerChangePassword(InterviewerLoginRequiredMixin, View):
    """
    This view is used to change the password of Interviewer.
    username -> str : It holds the name of the current logged in Interviewer.
    new_password -> str : It holds the new password of the Interviewer.
    confirm_password -> str : It stores the re-entered new password of the Interviewer.
    old_password -> str : It stores the old-password of Interviewer, which is used to authenticate.
    """
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


class CompanyCareer(CompanyLoginRequiredMixin, View):
    """
    This view is used to display the job openings of specific logged in company and also used to
    delete the particular job openings.
    jobs -> objects : it is a collection of job openings of particular logged in company.
    job_id -> int : It is a id of particular job which is used to delete particular job.
    """
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


class UserAppliedJobs(UserLoginRequiredMixin, View):
    """
    This view is used to show the status for users' application in different companies.
    jobs -> objects : It is a collection of objects which consist the data about particular user in which
                      different companies' user have applied for various posts.
    """
    def get(self, request, *args, **kwargs):
        jobs = UserJobApplied.objects.filter(user=request.user)
        return render(request, 'user_login/user_job_applied.html', {'jobs': jobs})


class UserProfile(UserLoginRequiredMixin, View):
    """
    This view is used to display the particular user's details
    user_details -> object : It consists the details of user which is rendered on HTML page.
    """
    def get(self, request, *args, **kwargs):
        user_details = UserDetails.objects.filter(user=request.user)
        return render(request, 'user_login/user_profile.html', {'user_details': user_details})


class InterviewerProfile(InterviewerLoginRequiredMixin, View):
    """
    This view is used to display the particular Interviewer's details
    company_name -> object : It stores the name of the company, from which interviewer belongs.
    interviewer_details -> object : It consists the details of interviewer which is rendered on HTML page.
    """
    def get(self, request, *args, **kwargs):
        company_name = InterviewerCompany.objects.get(interviewer=request.user)
        interviewer_details = InterviewerDetails.objects.filter(interviewer=request.user)
        print('herere')
        return render(request, 'user_login/interviewer_profile.html',
                      {'interviewer_details': interviewer_details, 'company': company_name.company.username})


@method_decorator(csrf_exempt, name='dispatch')
class ShowInterviewers(CompanyLoginRequiredMixin, View):
    """
    This view is used to show all those interviewers to company which belongs to them.
    Also, interviewers are managed from here.
    interviewers -> objects : It is a collection of Interviewers of specific company.
    interviewer_id -> int : It stores the id of interviewer which is used to remove the interviewer.
    """
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


class UpdateUserDetails(UserLoginRequiredMixin, View):
    """
    This view is used to update the details of User.
    form -> form : It is used to update the details of UsedDetails Model (For logged in user).
    form2 -> form : It is used to update the email of CustomUser Model (For logged-in user).
    """
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
                return redirect('user-profile')
            else:
                return redirect('user-profile')
        else:
            return redirect('user-update-profile')


class UpdateInterviewerDetails(InterviewerLoginRequiredMixin, View):
    """
    This view is used to update the details of User.
    form1 -> form : It is used to update the details of InterviewerDetails Model (For logged-in user).
    form2 -> form : It is used to update the email of CustomUser Model (For logged-in user).
    """
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
                return redirect('interviewer-profile')
            else:
                return redirect('interviewer-profile')
        else:
            return redirect('interviewer-update-profile')


class ShowAppliedUser(CompanyLoginRequiredMixin, View):
    """
    This view is used to display the applicants who have applied for jobs in loggd-in company.
    applicants -> objects : It is a collection of object of UserJobApplied model.
    applicant_details -> list : It is a list of dictionaries which consist the data of users who have applied for job in
                                logged-in company.
    notification_message -> str : It is a variable which stores the notification message.
    """
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
                pass
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


class JobOpeningUpdate(CompanyLoginRequiredMixin, View):
    """
    This view is used to update the posted job of the logged-in company.
    company -> object : It is an object which consist the information of particular job post
    form1 -> form : It is used to update the details of that particular job post.
    """
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


class ShowAcceptedInterviewers(CompanyLoginRequiredMixin, View):
    """
    This view is used to show all that applicants whose interviews are not scheduled.
    applicants -> objects : It is a collection of objects of UserInterview module.
    job_application__job__company -> str : It is used in ORM to filter the resultant queryset for specific
                                           logged-in company.
    """
    def get(self, request, *args, **kwargs):
        applicants = UserInterview.objects.filter(Q(technical_round='Pending') | Q(HR_round='Pending'),
                                                  job_application__job__company=request.user)
        return render(request, 'user_login/schedule_interviews.html', {'applicants': applicants})


class ScheduleApplicantInterview(CompanyLoginRequiredMixin, View):
    """
    This view is used for scheduling the interview of User.
    form1 -> form : This form is used to fill the details for Scheduling Interview of Applicant.
    pk -> int : This is used as a parameter which consist the ID of Applicant.
    time_interview -> str : It holds the time slot of interview.
    interview_type -> object : It is an object of type of interviewer.
    date_interview -> str : It holds the date in str format of interview.
    """
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
        message = Notification.objects.create(sender=request.user, receiver=application.job_application.user,
                                              message=notification_message)
        message.save()
        message = Notification.objects.create(sender=request.user, receiver=interviewer.interviewer,
                                              message=notification_message)
        message.save()
        user_email = application.job_application.user.email
        interviewer_email = interviewer.interviewer.email
        send_mail(email_subject, email_message, request.user.email, [user_email, interviewer_email],
                  fail_silently=False, )
        return redirect('show-accepted-applicants')


@method_decorator(csrf_exempt, name='dispatch')
class InterviewType(CompanyLoginRequiredMixin,View):
    """
    This is an extra view which is specially created for AJAX.
    type_interview_id -> int : It is an id of interviewer type using which available interviewer of specific type in
                               logged-in company are differentiated.
    """
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
                data = {'id': examiner.interviewer.id, 'username': examiner.interviewer.username}
                interviewers_list.append(data)
        return JsonResponse({"success": True, 'interviewers': interviewers_list})


@method_decorator(csrf_exempt, name='dispatch')
class GetTimeSlot(View):
    """
    This is an extra view which is specially created for AJAX using which available time slots are
    searched and returned to the html.
    interviewer -> object : It consists the object of interviewer.
    sch_date -> str : It consists the chose date of interview.
    applicant -> int : It consists the id of user.
    final_time_slot -> list : It is a list of available time slots for user.
    """
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
            timing_list.append(time1.interview_time)
        final_time_slot = list(set(time_slots) - set(timing_list))
        return JsonResponse({'final_time_slot': final_time_slot})


class ShowInterviewerScheduled(InterviewerLoginRequiredMixin, View):
    """
    This view is used by the interviewer to display the scheduled Interviews.
    interviewer -> object : It holds the object of logged-in Interviewer.
    interview_schedule -> objects : It is a collection of objects which consists the schedules of Interviewer.
    """
    def get(self, request, *args, **kwargs):
        interviewer = InterviewerDetails.objects.get(interviewer=request.user)
        interview_schedule = Interview.objects.filter(interviewer=interviewer)
        return render(request, 'user_login/interviewer_schedule.html', {'interview_schedule': interview_schedule})


class ApplicantDetails(InterviewerLoginRequiredMixin, View):
    """
    This view is used to See the Applicant Details and job details
    applicant_details -> object : It holds the object of UserInterview module.
    user_details -> object : It holds the all the details of User.
    job_application -> object : It holds the details about job post for which user have applied.
    """
    def get(self, request, *args, **kwargs):
        applicant_details = UserInterview.objects.get(id=kwargs['pk'])
        user_details = UserDetails.objects.select_related('user').get(user_id=applicant_details.job_application.user_id)
        job_application = JobOpenings.objects.get(id=applicant_details.job_application.job_id)
        return render(request, 'user_login/application_details.html',
                      {'user_detail': user_details, 'job_application': job_application})


class ShowDetailSchedule(UserLoginRequiredMixin, View):
    """
    This view is used to see the detail schedule of Application.
    user_interview -> object : It is an object of UserInterview module which consists the details of Interview.
    """
    def get(self, request, *args, **kwargs):
        user_interview = UserInterview.objects.get(job_application_id=kwargs['pk'])
        interviews = Interview.objects.filter(application=user_interview)
        return render(request, 'user_login/detail_interview_schedule.html', {'interviews': interviews})


class DetailsInterviewer(UserLoginRequiredMixin, View):
    """
    This view is used to see the details of Interviewer.
    interviewer_detail -> object : It is an object which holds the data about Interviewer.
    company_name -> object : It holds the data of Interviewer and Company relation.
    """
    def get(self, request, *args, **kwargs):
        interviewer_detail = InterviewerDetails.objects.get(id=kwargs['pk'])
        company_name = InterviewerCompany.objects.get(interviewer_id=interviewer_detail.interviewer.id)
        return render(request, 'user_login/interviewer_details.html',
                      {'interviewer_detail': interviewer_detail, 'company': company_name.company.username})


class UserMessage(UserLoginRequiredMixin, View):
    """
    This view is used to display the messages for logged-in user.
    messages -> objects : It is a collection of objects which consists the notifications.
    """
    def get(self, request, *args, **kwargs):
        messages = Notification.objects.filter(receiver=request.user)
        return render(request, 'user_login/user_messages.html', {'messages': messages})


class InterviewerMessage(InterviewerLoginRequiredMixin, View):
    """
    This view is used to display the messages for logged-in Interviewer.
    messages -> objects : It is a collection of objects which consists the notifications.
    """
    def get(self, request, *args, **kwargs):
        messages = Notification.objects.filter(receiver=request.user)
        return render(request, 'user_login/interviewer_messages.html', {'messages': messages})


class CompanyMessage(CompanyLoginRequiredMixin, View):
    """
    This view is used to display the messages for logged-in company.
    messages -> objects : It is a collection of objects which consists the notifications.
    """
    def get(self, request, *args, **kwargs):
        messages = Notification.objects.filter(receiver=request.user)
        return render(request, 'user_login/company_messages.html', {'messages': messages})


class UserFeedbackView(UserLoginRequiredMixin, View):
    """
    This view is used by the user to provide the feedback to the interviewer.
    interviewer_feedback -> object : It is an object which consists the data related to feedback of Interviewer.
    """
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


class FeedbackOfInterviewer(InterviewerLoginRequiredMixin, View):
    """
    This view is used by the interviewer to provide the feedback to the User.
    user_process -> object : It is an object which consists the data related to feedback of User.
    """
    def get(self, request, *args, **kwargs):
        application = UserInterview.objects.get(id=kwargs['pk'])
        form = UserFeedbackByInterviewer
        return render(request, 'user_login/post_interview.html',
                      {'form': form, 'interviewer': request.user, 'application': application})

    def post(self, request, *args, **kwargs):
        form = UserFeedbackByInterviewer(request.POST)
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


class RescheduleRequest(UserLoginRequiredMixin, View):
    """
    This view is used for creating request of Reschedule.
    request_rescheduling -> object : It is an object of reschedule request with reason.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/reschedule_request.html',
                      {'user': request.user, 'application': kwargs['pk']})

    def post(self, request, *args, **kwargs):
        user = request.user
        application_id = kwargs['pk']
        application = Interview.objects.get(id=application_id)
        reason = request.POST['reschedule_reason']
        request_rescheduling = RescheduleRequests.objects.create(user=user, interview_application=application,
                                                                 reason=reason)
        request_rescheduling.save()
        return redirect('detail-schedule', pk=application.application.job_application_id)


class ShowRescheduleRequests(CompanyLoginRequiredMixin, View):
    """
    This view is showing the request of the rescheduling to the company.
    reschedule -> objects : It is a collection of objects of RescheduleRequests model.
    """
    def get(self, request, *args, **kwargs):
        reschedule = RescheduleRequests.objects.filter(
            interview_application_id__application__job_application__job__company=request.user, is_rescheduled=False)
        return render(request, 'user_login/show_reschedule_request.html', {'reschedule_requests': reschedule})


class PostInterviewProcess(InterviewerLoginRequiredMixin, View):
    """
    This view is used by the Interviewer to submit the result of Applicant after Interview.
    interviewer -> object : It is an object of details of Interviewer.
    interviews -> objects : It is a collection of objects of applicants whose interview are
                            already scheduled.
    """
    def get(self, request, *args, **kwargs):
        interviewer = InterviewerDetails.objects.get(interviewer=request.user)
        if interviewer.type_interviewer_id == 4:
            interviews = Interview.objects.select_related('application').filter(
                interviewer__interviewer=request.user).exclude(
                Q(application__HR_round='Accepted') | Q(application__HR_round='Rejected'))
        else:
            interviews = Interview.objects.select_related('application').filter(
                interviewer__interviewer=request.user).exclude(
                Q(application__technical_round='Accepted') | Q(application__technical_round='Rejected'))
        return render(request, 'user_login/post_interview_applicants.html', {'interviews': interviews})


class DeactivateAccount(View):
    """
    This view is used to deactivate the account of User , Company or Interviewer whoever is logged-in.
    """
    def get(self, request, *args, **kwargs):
        CustomUser.objects.filter(id=kwargs['pk']).update(is_activated=False)
        logout(request)
        return redirect('login')


class ReactivateAccount(View):
    """
    This view is used to reactivate the account of the user, Interviewer or Company.
    email -> str : It holds the email for sending the url to reactivate the account.
    domain -> str : It holds the domain name which one is added to the url.
    url -> str : It is an url which is sent to the user for further process.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/reactivate.html')

    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        domain = request.build_absolute_uri('/')[:-1]
        url = f"{domain}/reactivate/user_info/"
        send_mail('Reactivate Your Account', url, from_email=os.getenv('EMAIL_HOST_USER'), recipient_list=[email],
                  fail_silently=False, )
        return redirect('login')


class ReactivationUser(View):
    """
    This view is used for verifying the user and authenticate that user before reactivating the account.
    username -> str : It holds the username of the User/Company/Interviewer.
    password -> str : It holds the password of the User/Company/Interviewer.
    user_status -> object : It holds the object of authenticated user.
    """
    def get(self, request, *args, **kwargs):
        return render(request, 'user_login/reactivation_page.html')

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            user_status = CustomUser.objects.get(id=user.id)
            user_status.is_activated = True
            user_status.save()
            return redirect('login')
        else:
            messages.info(request,'Your credentials are invalid please enter right credentials.')
            return render(request, 'user_login/reactivation_page.html')


class DetailInterviewScheduleShow(CompanyLoginRequiredMixin, View):
    """
    This view is used to check the schedule of Applicant's Interview.
    interview -> object : It is an object which consist the details of Interview.
    """
    def get(self, request, *args, **kwargs):
        interview = Interview.objects.get(id=kwargs['pk'])
        return render(request, 'user_login/interview_details_application.html', {'interview': interview})


class RescheduleUserInterview(CompanyLoginRequiredMixin, View):
    """
    This view show the all the details of the requested interview for reschedule.
    form -> form : This form is used to Reschedule the date and time.
    time_slot -> str : It holds the updated time of Interview.
    date_interview -> str : It holds the updated date of Interview.
    interview_application -> object : It holds the object of RescheduleRequest model which is used to update the status of is_rescheduled.
    interview_reschedule -> object : It holds the object of Interview Model which is used to update the time and date.
    interview_application.interview_application.id -> int : It is an int id using which exact object of Interview model is searched.
    """
    def get(self, request, *args, **kwargs):
        interview_application = RescheduleRequests.objects.get(id=kwargs['pk'])
        interviewer = Interview.objects.get(id=interview_application.interview_application.id)
        form = RescheduleTime
        return render(request, 'user_login/reschedule_user_interview.html', {'interviewer': interviewer, 'form': form})

    def post(self, request, *args, **kwargs):
        sch_date = request.POST.get('date')
        date_interview1 = datetime.strptime(sch_date, '%Y-%m-%d')
        date_interview = date_interview1.strftime('%Y-%m-%d')
        time_slot = request.POST.get('interview_time')
        interview_application = RescheduleRequests.objects.get(id=kwargs['pk'])
        interview_reschedule = Interview.objects.get(id=interview_application.interview_application.id)
        interview_reschedule.interview_time = time_slot
        interview_reschedule.interview_date = date_interview
        interview_reschedule.save()
        interview_application.is_rescheduled = True
        interview_application.save()

        notification_message = 'Your interview is Rescheduled. To know more about it please check your ' \
                               'application status. '
        message = Notification.objects.create(sender=request.user,
                                              receiver=interview_reschedule.application.job_application.user,
                                              message=notification_message)
        message.save()
        notification_message = 'Your interview is Rescheduled. To know more about it please check your ' \
                               'Interview Schedule. '
        message = Notification.objects.create(sender=request.user,
                                              receiver=interview_reschedule.interviewer.interviewer,
                                              message=notification_message)
        message.save()
        return redirect('show-request-reschedule')


@method_decorator(csrf_exempt, name='dispatch')
class RescheduleGetTimeSlot(CompanyLoginRequiredMixin, View):
    """
    This is an extra view which is specially created for AJAX using which available time slots are
    searched and returned to the html.
    interviewer_id -> str : It consists the id of interviewer(InterviewerDetails model).
    sch_date -> str : It consists the chose date of interview.
    applicant -> int : It consists the id of user.
    final_time_slot -> list : It is a list of available time slots for user.
    """
    def post(self, request, *args, **kwargs):
        time_slots = ['09:00–09:30', '10:00–10:30', '11:00–11:30', '12:00–12:30', '13:00–13:30',
                      '14:00–14:30', '15:00–15:30', '16:00–16:30', '17:00–17:30']
        request_data = request.read()
        form_data = json.loads(request_data.decode('utf-8'))
        interviewer_id = form_data.get("interviewer_id")
        sch_date = form_data.get("sch_date")
        applicant = form_data.get('applicant_id')
        date_interview1 = datetime.strptime(sch_date, '%Y-%m-%d')
        sch_date = date_interview1.strftime('%Y-%m-%d')
        interview_timings = Interview.objects.filter(
            Q(interview_date=sch_date, interviewer=interviewer_id) | Q(interview_date=sch_date,
                                                                       application_id=int(applicant)))
        timing_list = []
        for time1 in interview_timings:
            timing_list.append(time1.interview_time)
        final_time_slot = list(set(time_slots) - set(timing_list))
        return JsonResponse({'final_time_slot': final_time_slot})


class IsAcceptAsEmployee(CompanyLoginRequiredMixin, View):
    """
    This view is used by the company to update the Employment status.
    applicants -> objects : It is a collection of objects of UserInterview model where user's
                            technical_round and hr_round is accepted.
    """
    def get(self, request, *args, **kwargs):
        applicants = UserInterview.objects.filter(job_application__job__company=request.user, HR_round='Accepted',
                                                  technical_round='Accepted', selection_status='Pending')
        return render(request, 'user_login/show_all_applicants.html', {'applicants': applicants})


class ScheduledUsersInterviewsDisplay(CompanyLoginRequiredMixin, View):
    """
    This view is used by the Company to see the scheduled interviews.
    interviews -> objects : It is a collection of objects which holds the multiple Interview schedules with details.
    """
    def get(self, request, *args, **kwargs):
        interviews = Interview.objects.filter(application__job_application__job__company=request.user)
        return render(request, 'user_login/Show_scheduled_interviews.html', {'interviews': interviews})


@method_decorator(csrf_exempt, name='dispatch')
class CollectFinalStatus(CompanyLoginRequiredMixin, View):
    """
    This view is mainly used for AJAX related to updating the final employment status of Applicant.
    application_id -> str : It is used to update the status of specific application.
    data_value -> str : It is used for status whether user is selected as a employee or not.
                        (1 for Accepted | 0 for Rejected)
    notification_message -> str : It is a message which is used in mail to inform user the status of Employment.
    """
    def post(self, request, *args, **kwargs):
        request_data = request.read()
        form_data = json.loads(request_data.decode('utf-8'))
        application_id = form_data.get('application_id')
        data_value = form_data.get('data_value')
        if data_value == '1':
            user = UserInterview.objects.get(id=int(application_id))
            user.selection_status = 'Accepted'
            user.save()
            messages = 'You are Accepted'
        else:
            user = UserInterview.objects.get(id=int(application_id))
            user.selection_status = 'Rejected'
            user.save()
            messages = 'Sorry ! You are Rejected'
        notification_message = messages + ' in ' + str(request.user.username) + '.'
        message = Notification.objects.create(sender=request.user, receiver=user.job_application.user,
                                              message=notification_message)
        message.save()
        send_mail('Employment Status', notification_message, request.user.email, [user.job_application.user.email])
        return JsonResponse({'message': messages})


class ShowFeedBackInterviewer(InterviewerLoginRequiredMixin, View):
    """
    This view is used by the interviewer to see the feedback provided by the user.
    interviewer_feedback -> objects : It consists the details of feedback which are given to the
                                      current logged-in Interviewer.
    """
    def get(self, request, *args, **kwargs):
        interviewer_feedbacks = InterviewerFeedback.objects.filter(interviewer=request.user)
        return render(request, 'user_login/interviewer_feedbacks.html',
                      {'interviewer_feedbacks': interviewer_feedbacks})

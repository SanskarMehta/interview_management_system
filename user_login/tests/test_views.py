import os.path
import pytest
from django.core.files import File
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertRedirects, assertJSONEqual
from interview_management_system.settings import BASE_DIR


class TestHomeView:

    def test_can_page(self, client):
        response = client.get(reverse('home'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/base.html')


class TestUserLogin:

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_user(self, client, test_create_user):
        user = test_create_user
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/user_details_form/')

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_user_not_first_time(self, client, test_create_user):
        user = test_create_user
        user.is_first_time = False
        user.save()
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/user_home/')

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_user_blocked(self, client, test_create_user_blocked):
        user = test_create_user_blocked
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(
            messages[0]) == "Your account is blocked by admin. Please call on number : 129121####."

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_user_not_activated(self, client, test_create_user_not_activated):
        user = test_create_user_not_activated
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(
            messages[0]) == 'Your account is deactivated. Please reactivate your account. '

    @pytest.mark.django_db
    def test_can_page_with_wrong_credentials(self, client):
        response = client.post(reverse('login'), {'username': 'fake', 'password': 'test@1234'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == "You unable to login because credentials are not matching"

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_interviewer(self, client, test_create_interviewer):
        user = test_create_interviewer
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/interviewer_details_form/')

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_interviewer_not_first_time(self, client, test_create_interviewer):
        user = test_create_interviewer
        user.is_first_time = False
        user.save()
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/interviewer_home/')

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_company(self, client, test_create_company):
        user, company_accepted = test_create_company
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(
            messages[0]) == "Your company is not accepted from the admin side. You can login after accepted by admin."

    @pytest.mark.django_db
    def test_can_page_with_right_credentials_company_accepted(self, client, test_create_company):
        user, company_accepted = test_create_company
        company_accepted.is_accepted = True
        company_accepted.save()
        response = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/company_home/')

    @pytest.mark.django_db
    def test_can_get_login_interviewer(self, client, test_create_user):
        user = test_create_user
        user.is_interviewer = True
        user.save()
        response2 = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        response = client.get(reverse('login'), data={'user': user})
        assert response.status_code == 302
        assertRedirects(response, '/interviewer_details_form/')

    @pytest.mark.django_db
    def test_can_get_login_interviewer_not_first(self, client, test_create_user):
        user = test_create_user
        user.is_interviewer = True
        user.is_first_time = False
        user.save()
        response2 = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        response = client.get(reverse('login'), data={'user': user})
        assert response.status_code == 302
        assertRedirects(response, '/interviewer_home/')

    @pytest.mark.django_db
    def test_can_get_login_company(self, client, test_create_company):
        user, company_accepted = test_create_company
        company_accepted.is_accepted = True
        company_accepted.save()
        response2 = client.post(reverse('login'), data={'username': user.username, 'password': 'test@123'})
        response = client.get(reverse('login'), data={'user': user})
        assert response.status_code == 302
        assertRedirects(response, '/company_home/')


class TestUserRegister:

    def test_can_page_get(self, client):
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/register.html')

    @pytest.mark.django_db
    def test_can_page_post_register(self, client):
        response = client.post(reverse('register'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/login/')

    @pytest.mark.django_db
    def test_can_page_post_register_same_password(self, client):
        response = client.post(reverse('register'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@1234'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Your passwords are not matched.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_email(self, client, test_create_user):
        user = test_create_user
        response = client.post(reverse('register'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Email is already exist.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_name(self, client, test_create_user):
        user = test_create_user
        response = client.post(reverse('register'),
                               data={'username': 'Sanskar1234', 'email': 'sanskar36393@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Username is already is taken.'


class TestInterviewerHome:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('interviewer-home'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_home.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('interviewer-home'))
        assert response.status_code == 403


class TestUserHome:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('user-home'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_home.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('user-home'))
        assert response.status_code == 403


class TestCompanyHome:

    @pytest.mark.django_db
    def test_home_user_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('company-home'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_home_company_get(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('company-home'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_home.html')


class TestCompanyRegister:

    def test_can_page_get(self, client):
        response = client.get(reverse('company-register'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_register.html')

    @pytest.mark.django_db
    def test_can_page_post_register(self, client):
        response = client.post(reverse('company-register'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/login/')

    @pytest.mark.django_db
    def test_can_page_post_register_same_password(self, client):
        response = client.post(reverse('company-register'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@1234'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Your passwords are not matched.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_email(self, client, test_create_company):
        user = test_create_company
        response = client.post(reverse('register'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Email is already exist.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_name(self, client, test_create_company):
        user = test_create_company
        response = client.post(reverse('register'),
                               data={'username': 'Sanskar1234', 'email': 'sanskar36393@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Username is already is taken.'


class TestUserDetailsForm:

    @pytest.mark.django_db
    def test_user_details_form_get_user(self, client, test_user_loggedin):
        user = test_user_loggedin
        response = client.get(reverse('user-details-form'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_details_form.html')

    @pytest.mark.django_db
    def test_user_details_form_get_company(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.get(reverse('user-details-form'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_user_details_form_post_user(self, client, test_user_loggedin):
        user = test_user_loggedin
        cv_file = open(os.path.join(BASE_DIR, 'default.pdf'), 'rb')
        cv_file_obj = File(cv_file)
        response = client.post(reverse('user-details-form'),
                               data={'mobilenumber': '832-049-9836', 'technology': 'Python', 'marks_10th': 98.9,
                                     'marks_12th': 97.9, 'cpi': 8.89, 'cvfile': cv_file_obj})
        assert response.status_code == 302
        assertRedirects(response, '/user_home/')

    @pytest.mark.django_db
    def test_user_details_form_post_user_wrong_file(self, client, test_user_loggedin):
        user = test_user_loggedin
        cv_file = open(os.path.join(BASE_DIR, 'default.txt'), 'rb')
        cv_file_obj = File(cv_file)
        response = client.post(reverse('user-details-form'),
                               data={'mobilenumber': '832-049-9836', 'technology': 'Python', 'marks_10th': 98.9,
                                     'marks_12th': 97.9, 'cpi': 8.89, 'cvfile': cv_file_obj})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == "Please Upload .PDF or .DOC file"

    @pytest.mark.django_db
    def test_user_details_form_post_user_wrong_marks(self, client, test_user_loggedin):
        user = test_user_loggedin
        cv_file = open(os.path.join(BASE_DIR, 'default.txt'), 'rb')
        cv_file_obj = File(cv_file)
        response = client.post(reverse('user-details-form'),
                               data={'mobilenumber': '832-049-9836', 'technology': 'Python', 'marks_10th': 98.9,
                                     'marks_12th': 100.9, 'cpi': 8.89, 'cvfile': cv_file_obj})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == "Your result must be less than or equal to 100"


class TestCompanyJobOpenings:

    @pytest.mark.django_db
    def test_user_details_form_get_company(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.get(reverse('company-job-openings'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_job_opening.html')

    @pytest.mark.django_db
    def test_user_details_form_get_user(self, client, test_user_loggedin):
        user = test_user_loggedin
        response = client.get(reverse('company-job-openings'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_user_details_form_post_user(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.post(reverse('company-job-openings'),
                               data={'job_location': 'Remote', 'job_role': 'Sr. Python Developer',
                                     'description': 'We required a developer who have exp of min 3+ yrs.'})
        assert response.status_code == 302
        assertRedirects(response, '/career/')


class TestCompanyAddInterviewer:

    @pytest.mark.django_db
    def test_user_details_form_get_company(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.get(reverse('company-add-interviewer'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_add_interviewer.html')

    @pytest.mark.django_db
    def test_user_details_form_get_user(self, client, test_user_loggedin):
        user = test_user_loggedin
        response = client.get(reverse('company-add-interviewer'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_can_page_post_register_interviewer(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.post(reverse('company-add-interviewer'),
                               data={'username': 'sanskar123', 'email': 'sanskar36393@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/show_interviewers/')

    @pytest.mark.django_db
    def test_can_page_post_register_not_same_password_interviewer(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.post(reverse('company-add-interviewer'),
                               data={'username': 'sanskar123', 'email': 'sanskar36393@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@1234'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == "Your password's are not matching so you unable to create account."

    @pytest.mark.django_db
    def test_can_page_post_register_same_email_interviewer(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.post(reverse('company-add-interviewer'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Email is already exist.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_name_interviewer(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.post(reverse('company-add-interviewer'),
                               data={'username': 'Sanskar123456789', 'email': 'sanskar36393@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Username is already is taken.'


class TestInterviewerDetailsForm:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_interviewer_loggedin_without_details, client):
        user = test_interviewer_loggedin_without_details
        response = client.get(reverse('interviewer-details-form'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_details_form.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('interviewer-details-form'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_interviewer_details_form_post(self, test_interviewer_loggedin_without_details, test_interviewer_type,
                                           client):
        user = test_interviewer_loggedin_without_details
        interviewer_type = test_interviewer_type.type
        response = client.post(reverse('interviewer-details-form'),
                               data={'mobilenumber': '832-049-9836', 'technology': 'Python',
                                     'job_role': 'Python Developer', 'experience': '3+ yrs',
                                     'interviewer_type': interviewer_type})
        assert response.status_code == 302
        assertRedirects(response, '/interviewer_home/')


class TestJobLists:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('job-lists'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/job_lists.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('job-lists'))
        assert response.status_code == 403


class TestJobListsApply:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_user_loggedin, client, test_company_job_openings):
        user = test_user_loggedin
        job_id = test_company_job_openings.id
        response = client.get(reverse('job-apply', kwargs={'pk': job_id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/after_apply.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client, test_company_job_openings):
        user = test_interviewer_loggedin
        job_id = test_company_job_openings.id
        response = client.get(reverse('job-apply', kwargs={'pk': job_id}))
        print(response)
        assert response.status_code == 403


class TestUserChangePassword:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('user-change-password'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_change_password.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('user-change-password'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_user_password_change(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.post(reverse('user-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@111', 'old_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/user_password_changed/')

    @pytest.mark.django_db
    def test_user_password_change_not_same_password(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.post(reverse('user-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@1112', 'old_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Your passwords are not matching so.'

    @pytest.mark.django_db
    def test_user_password_change_invalid_password(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.post(reverse('user-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@111',
                                     'old_password': 'test@12345677'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Please enter the valid credentials'


class TestCompanyChangePassword:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('company-change-password'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_change_password.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('company-change-password'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_company_password_change(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.post(reverse('company-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@111', 'old_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/company_password_changed/')

    @pytest.mark.django_db
    def test_company_password_change_not_same_password(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.post(reverse('company-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@1112', 'old_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Your passwords are not matching so.'

    @pytest.mark.django_db
    def test_company_password_change_invalid_password(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.post(reverse('company-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@111',
                                     'old_password': 'test@12345677'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Please enter the valid credentials'


class TestInterviewerChangePassword:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('interviewer-change-password'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_change_password.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('interviewer-change-password'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_interviewer_password_change(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.post(reverse('interviewer-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@111', 'old_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/interviewer_password_changed/')

    @pytest.mark.django_db
    def test_interviewer_password_change_not_same_password(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.post(reverse('interviewer-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@1112', 'old_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Your passwords are not matching so.'

    @pytest.mark.django_db
    def test_interviewer_password_change_invalid_password(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.post(reverse('interviewer-change-password'),
                               data={'new_password': 'test@111', 'password2': 'test@111',
                                     'old_password': 'test@12345677'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Please enter the valid credentials'


class TestCompanyCareer:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('company-career'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_career.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('company-career'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_company_career(self, test_company_loggedin, test_delete_company_job_opening,client):
        user = test_company_loggedin
        job_id = test_delete_company_job_opening
        response = client.delete(reverse('company-career'),data={'job_id':job_id},content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


class TestUserAppliedJobs:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('user-job-apply'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_job_applied.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('user-job-apply'))
        assert response.status_code == 403


class TestUserProfile:

    @pytest.mark.django_db
    def test_user_details_form_get_user(self, client, test_user_loggedin):
        user = test_user_loggedin
        response = client.get(reverse('user-profile'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_profile.html')

    @pytest.mark.django_db
    def test_user_details_form_get_company(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.get(reverse('user-profile'))
        assert response.status_code == 403


class TestInterviewerProfile:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_interviewer_company_details_loggedin, client):
        user = test_interviewer_company_details_loggedin
        response = client.get(reverse('interviewer-profile'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_profile.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('interviewer-profile'))
        assert response.status_code == 403


class TestShowInterviewers:
    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('show-interviewers'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/show_interviewers.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('show-interviewers'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_company_interviewer(self, test_company_loggedin, test_delete_interviewer, client):
        user = test_company_loggedin
        interviewer_id = test_delete_interviewer
        response = client.delete(reverse('show-interviewers'), data={'interviewer_id': interviewer_id}, content_type='application/json',
                                 HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


class TestUpdateUserDetails:

    @pytest.mark.django_db
    def test_user_details_form_get_user(self, client, test_user_with_details_loggedin):
        user = test_user_with_details_loggedin
        response = client.get(reverse('user-update-profile'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_update_profile.html')

    @pytest.mark.django_db
    def test_user_details_form_get_company(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.get(reverse('user-update-profile'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_user_update_details_post(self, client, test_user_with_details_loggedin):
        user = test_user_with_details_loggedin
        response = client.post(reverse('user-update-profile'), data={'user_12th_marks': 98, 'user_10th_marks': 76})
        assert response.status_code == 302
        assertRedirects(response, '/user_update_profile/')


class TestUpdateInterviewerDetails:

    @pytest.mark.django_db
    def test_interviewer_details_form_get_user(self, client, test_interviewer_with_details_loggedin):
        user = test_interviewer_with_details_loggedin
        response = client.get(reverse('interviewer-update-profile'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_update_profile.html')

    @pytest.mark.django_db
    def test_interviewer_details_form_get_company(self, client, test_company_loggedin):
        user = test_company_loggedin
        response = client.get(reverse('interviewer-update-profile'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_interviewer_update_details_post(self, client, test_interviewer_with_details_loggedin):
        user = test_interviewer_with_details_loggedin
        response = client.post(reverse('interviewer-update-profile'), data={'interviewer_technology': 'Python'})
        assert response.status_code == 302
        assertRedirects(response, '/interviewer_update_profile/')


class TestShowAppliedUser:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('company-applicants'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/show_applied_user.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('company-applicants'))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_show_applied_user_with_accepted(self, test_user_job_applied, client):
        user, job_id = test_user_job_applied
        response = client.post(reverse('company-applicants'), data={'user_applied_job_id': job_id, 'data_status': '0'})
        assert response.status_code == 200
        assertJSONEqual(str(response.content, encoding='utf8'),
                        expected_data={'success': True, 'message': 'Interviewer Deleted Successfully'})

    @pytest.mark.django_db
    def test_show_applied_user_with_rejected(self, test_user_job_applied, client):
        user, job_id = test_user_job_applied
        response = client.post(reverse('company-applicants'), data={'user_applied_job_id': job_id, 'data_status': '1'})
        assert response.status_code == 200
        assertJSONEqual(str(response.content, encoding='utf8'),
                        expected_data={'success': True, 'message': 'Interviewer Deleted Successfully'})


class TestJobOpeningUpdate:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_company_loggedin, test_company_job_openings, client):
        user = test_company_loggedin
        job_id = test_company_job_openings.id
        response = client.get(reverse('update-job', kwargs={'pk': job_id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_job_openings_update.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, test_company_job_openings, client):
        user = test_interviewer_loggedin
        job_id = test_company_job_openings.id
        response = client.get(reverse('update-job', kwargs={'pk': job_id}))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_home_update_job_post(self, test_company_loggedin, test_company_job_openings, client):
        user = test_company_loggedin
        job_id = test_company_job_openings.id
        response = client.post(reverse('update-job', kwargs={'pk': job_id}), data={'job_location': 'Ahmedabad',
                                                                                   'description': 'We required a experience developer who have min exp 3+ yrs',
                                                                                   'job_role': 'Python Developer'})
        assert response.status_code == 302
        assertRedirects(response, '/career/')

    @pytest.mark.django_db
    def test_home_update_job_invalid(self, test_company_loggedin, test_company_job_openings, client):
        user = test_company_loggedin
        job_id = test_company_job_openings.id
        response = client.post(reverse('update-job', kwargs={'pk': job_id}),
                               data={'job_location': 'Ahmedabad', 'job_role': 'Python Developer'})
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_job_openings_update.html')


class TestShowAcceptedInterviewers:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_company_loggedin, test_company_job_openings, client):
        user = test_company_loggedin
        response = client.get(reverse('show-accepted-applicants'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/schedule_interviews.html')

    @pytest.mark.django_db
    def test_home_user_get(self, test_interviewer_loggedin, test_company_job_openings, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('show-accepted-applicants'))
        assert response.status_code == 403


class TestScheduleApplicantInterview:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_use_interview_company, client):
        user_interview, company = test_use_interview_company
        response = client.get(reverse('technical-interview', kwargs={'pk': user_interview.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/technical_interview_form.html')

    @pytest.mark.django_db
    def test_home_interviewer_home(self, test_user_loggedin, client):
        company = test_user_loggedin
        response = client.get(reverse('technical-interview', kwargs={'pk': 1}))
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_home_interviewer_schedule_post(self, test_use_interview_company, test_interviewer_details, client):
        user_interview, company = test_use_interview_company
        interviewer = test_interviewer_details
        response = client.post(reverse('technical-interview', kwargs={'pk': user_interview.id}),
                               data={'type_interview': interviewer.type_interviewer.id, 'interview_date': '10/11/2022',
                                     'interviewer': interviewer.interviewer_id, 'interview_time': '9:30-10:30'})
        assert response.status_code == 302
        assertRedirects(response, '/show_accepted_applicants/')


class TestInterviewType:

    @pytest.mark.django_db
    def test_interviewer_type_ajax_post(self, client, test_company_loggedin, test_interviewer_type):
        user = test_company_loggedin
        interviewer_type = test_interviewer_type
        response = client.post(reverse('get-interviewer'), data={'type_interview_id': interviewer_type.id},
                               content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


class TestGetTimeSlot:

    @pytest.mark.django_db
    def test_interviewer_type_ajax_post(self, client, test_company_loggedin, test_interview_get_time_slot):
        user = test_company_loggedin
        application_id, interviewer_id = test_interview_get_time_slot
        response = client.post(reverse('get-time-slot'),
                               data={'interviewer_id': interviewer_id, 'sch_date': '10/11/2022',
                                     'applicant_id': application_id}, content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


class TestShowInterviewerScheduled:

    @pytest.mark.django_db
    def test_home_show_interviewer_schedule(self, client, test_interviewer_details):
        user = test_interviewer_details
        response2 = client.login(username=user.interviewer.username, password='test@123')
        response = client.get(reverse('show-interviewer-scheduled'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_schedule.html')


class TestApplicantDetails:

    @pytest.mark.django_db
    def test_home_show_interviewer_schedule(self, client, test_interviewer_loggedin, test_interview_get_time_slot):
        user = test_interviewer_loggedin
        user_interview_id, interviewer_id = test_interview_get_time_slot
        response = client.get(reverse('applicant_details', kwargs={'pk': user_interview_id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/application_details.html')


class TestShowDetailSchedule:

    @pytest.mark.django_db
    def test_home_show_detail_schedule_get(self, test_use_interview_company, test_user_loggedin, client):
        user = test_user_loggedin
        application_id, company = test_use_interview_company
        response = client.get(reverse('detail-schedule', kwargs={'pk': application_id.job_application_id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/detail_interview_schedule.html')


class TestDetailsInterviewer:

    @pytest.mark.django_db
    def test_home_details_interviewer(self, test_user_loggedin, test_interviewer_details, client):
        interviewer = test_interviewer_details
        user = test_user_loggedin
        response = client.get(reverse('interviewer-details', kwargs={'pk': interviewer.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_details.html')


class TestUserMessage:

    @pytest.mark.django_db
    def test_home_details_interviewer(self, test_user_loggedin, client):
        user = test_user_loggedin
        response = client.get(reverse('user-messages'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_messages.html')


class TestInterviewerMessage:

    @pytest.mark.django_db
    def test_home_details_interviewer(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('interviewer-messages'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/interviewer_messages.html')


class TestCompanyMessage:

    @pytest.mark.django_db
    def test_company_message_get(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('company-messages'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/company_messages.html')


class TestUserFeedbackView:

    @pytest.mark.django_db
    def test_home_details_interviewer_feedback_get(self, test_user_loggedin, test_interviewer_details, client):
        interviewer = test_interviewer_details
        user = test_user_loggedin
        response = client.get(reverse('user-feedback', kwargs={'pk': interviewer.id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/user_feedback.html')

    @pytest.mark.django_db
    def test_home_details_interviewer_feedback_user_post(self, test_user_loggedin, test_interviewer_details, client):
        interviewer = test_interviewer_details
        user = test_user_loggedin
        response = client.post(reverse('user-feedback', kwargs={'pk': interviewer.id}),
                               data={'feedback': "You need to improve alot."})
        assert response.status_code == 302
        assertRedirects(response, '/job_applied/')


class TestFeedbackOfInterviewer:

    @pytest.mark.django_db
    def test_home_interviewer_user_feedback_get(self, client, test_interviewer_loggedin, test_interview_get_time_slot):
        user = test_interviewer_loggedin
        user_interview_id, interviewer_id = test_interview_get_time_slot
        response = client.get(reverse('post-interview', kwargs={'pk': user_interview_id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/post_interview.html')

    @pytest.mark.django_db
    def test_home_interviewer_user_feedback_post(self, client, test_interviewer_loggedin, test_interview_get_time_slot):
        user = test_interviewer_loggedin
        user_interview_id, interviewer_id = test_interview_get_time_slot
        response = client.post(reverse('post-interview', kwargs={'pk': user_interview_id}),
                               data={'application': user_interview_id, 'user': 'Sanskar12345667', 'marks': 9,
                                     'feedback': 'He is very nice developer', 'application_status': 'Accepted'})
        assert response.status_code == 302
        assertRedirects(response, '/post_interview_applications/')


class TestRescheduleRequest:

    @pytest.mark.django_db
    def test_interview_reschedule_get(self, test_interview_reschedule_request, client, test_user_loggedin):
        user = test_user_loggedin
        application_id = test_interview_reschedule_request
        response = client.get(reverse('reschedule-request', kwargs={'pk': application_id}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/reschedule_request.html')

    @pytest.mark.django_db
    def test_interview_reschedule_post(self, test_interview_reschedule_request, client, test_user_loggedin):
        user = test_user_loggedin
        application_id = test_interview_reschedule_request
        response = client.post(reverse('reschedule-request', kwargs={'pk': application_id}),
                               data={'reschedule_reason': 'ABCDEFEFEFCFC'})
        assert response.status_code == 302


class TestShowRescheduleRequests:

    @pytest.mark.django_db
    def test_home_company_show_requests_get(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('show-request-reschedule'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/show_reschedule_request.html')


class TestPostInterviewProcess:

    @pytest.mark.django_db
    def test_post_interview_process_get(self, client, test_interviewer_loggedin):
        user = test_interviewer_loggedin
        response = client.get(reverse('post-interview-application'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/post_interview_applicants.html')


class TestDeactivateAccount:

    @pytest.mark.django_db
    def test_home_interviewer_get(self, test_create_user, client):
        user = test_create_user
        response = client.get(reverse('deactivate', kwargs={'pk': user.id}))
        assert response.status_code == 302
        assertRedirects(response, '/login/')


class TestReactivateAccount:

    @pytest.mark.django_db
    def test_reactivate_account_get(self, client):
        response = client.get(reverse('reactivate'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/reactivate.html')

    @pytest.mark.django_db
    def test_reactivate_account_post(self, client):
        response = client.post(reverse('reactivate'), data={'email': ''})
        assert response.status_code == 302
        assertRedirects(response, '/login/')


class TestReactivationUser:

    @pytest.mark.django_db
    def test_reactivate_account_get(self, client):
        response = client.get(reverse('reactivation'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'user_login/reactivation_page.html')

    @pytest.mark.django_db
    def test_reactivate_account_post(self, test_create_user, client):
        user = test_create_user
        response = client.post(reverse('reactivation'), data={'username': user.username, 'password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/login/')

    @pytest.mark.django_db
    def test_reactivate_account_post_invalid(self, test_create_user, client):
        user = test_create_user
        response = client.post(reverse('reactivation'), data={'username': user.username, 'password': 'test@1234'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Your credentials are invalid please enter right credentials.'


class TestDetailInterviewScheduleShow:

    @pytest.mark.django_db
    def test_get_detail_interview_schedule_show(self, client, test_interview_reschedule_request, test_company_loggedin):
        user = test_company_loggedin
        interview_id = test_interview_reschedule_request
        response = client.get(reverse('detail-interview-show',kwargs={'pk':interview_id}))
        assert response.status_code == 200
        assertTemplateUsed(response,'user_login/interview_details_application.html')


class TestRescheduleUserInterview:

    @pytest.mark.django_db
    def test_reschedule_user_interview_get(self, test_company_loggedin, test_reschedule_request, client):
        user = test_company_loggedin
        reschedule_request = test_reschedule_request
        response = client.get(reverse('reschedule-interview',kwargs={'pk':reschedule_request.id}))
        assert response.status_code == 200
        assertTemplateUsed(response,'user_login/reschedule_user_interview.html')


    @pytest.mark.django_db
    def test_reschedule_user_interview_post(self, test_company_loggedin, test_reschedule_request, client):
        user = test_company_loggedin
        reschedule_request = test_reschedule_request
        response = client.post(reverse('reschedule-interview',kwargs={'pk':reschedule_request.id}),data={'date':'2022-10-11','interview_time':'09:00–09:30'})
        assert response.status_code == 302
        assertRedirects(response,'/show_requests_reschedule/')


class TestRescheduleGetTimeSlot:

    @pytest.mark.django_db
    def test_reschedule_get_time_slot_post(self, client, test_company_loggedin, test_interview_get_time_slot):
        user = test_company_loggedin
        application_id, interviewer_id = test_interview_get_time_slot
        response = client.post(reverse('get-reschedule-time-slot'),
                               data={'interviewer_id': interviewer_id, 'sch_date': '2022-10-11',
                                     'applicant_id': application_id}, content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


class TestIsAcceptAsEmployee:

    @pytest.mark.django_db
    def test_is_accept_as_employee(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('accept-reject-applicant'))
        assert response.status_code == 200
        assertTemplateUsed(response,'user_login/show_all_applicants.html')


class TestScheduledUsersInterviewsDisplay:

    @pytest.mark.django_db
    def test_is_accept_as_employee(self, test_company_loggedin, client):
        user = test_company_loggedin
        response = client.get(reverse('show-scheduled-interviews'))
        assert response.status_code == 200
        assertTemplateUsed(response,'user_login/Show_scheduled_interviews.html')


class TestCollectFinalStatus:

    @pytest.mark.django_db
    def test_collect_final_status_rejected(self, client, test_use_interview_company):
        application_id,user = test_use_interview_company
        response = client.post(reverse('collect-final-status'),data={'application_id':application_id.id,'data_value':'0'},content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_collect_final_status_accepted(self, client, test_use_interview_company):
        application_id, user = test_use_interview_company
        response = client.post(reverse('collect-final-status'),
                               data={'application_id': application_id.id, 'data_value': '1'},
                               content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


class TestShowFeedBackInterviewer:

    @pytest.mark.django_db
    def test_show_feedback_interviewer_get(self, test_interviewer_loggedin, client):
        user = test_interviewer_loggedin
        response = client.get(reverse('feedback-of-interviewer'))
        assert response.status_code == 200
        assertTemplateUsed(response,'user_login/interviewer_feedbacks.html')
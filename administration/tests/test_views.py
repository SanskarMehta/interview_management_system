import os

import pytest
from django.core.files import File
from django.urls import reverse
from pytest_django.asserts import assertTemplateUsed, assertRedirects, assertJSONEqual

from interview_management_system.settings import BASE_DIR
from user_login.models import UserDetails


class TestHome:

    def test_home_get(self, client):
        response = client.get(reverse('admin-home'))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/base.html')


class TestAdminLogin:

    def test_admin_login_get(self, client):
        response = client.get(reverse('admin-login'))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/login.html')

    @pytest.mark.django_db
    def test_admin_login_post(self, test_create_administrator, client):
        administartor = test_create_administrator
        response = client.post(reverse('admin-login'),data={'username':administartor.username,'password':'test@123'})
        assert response.status_code == 302
        assertRedirects(response,'/administration/admin_after_login/')

    @pytest.mark.django_db
    def test_admin_login_post_with_wrong_credentials(self, test_create_administrator, client):
        administartor = test_create_administrator
        response = client.post(reverse('admin-login'),data={'username':administartor.username,'password':'test@1234'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(
            messages[0]) == 'You unable to access this site because your credentials are wrong.'

    @pytest.mark.django_db
    def test_admin_login_post_without_superuser(self, test_create_user, client):
        administartor = test_create_user
        response = client.post(reverse('admin-login'),
                               data={'username': administartor.username, 'password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(
            messages[0]) == 'You unable to access this site.'


class TestAdminAfterLogin:

    @pytest.mark.django_db
    def test_admin_after_login(self, test_admin_loggedin, client):
        user = test_admin_loggedin
        response = client.get(reverse('admin-after-login'))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/admin_home.html')


class TestShowInterviewersAdmin:

    @pytest.mark.django_db
    def test_show_interviewers_admin(self, test_admin_loggedin, client):
        admin = test_admin_loggedin
        response =client.get(reverse('show-interviewers-admin'))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/ShowInterviewers.html')


class TestShowUser:

    @pytest.mark.django_db
    def test_show_user(self, test_admin_loggedin, client):
        admin = test_admin_loggedin
        response = client.get(reverse('show-users'))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/ShowUsers.html')


class TestShowCompany:

    @pytest.mark.django_db
    def test_show_company(self, test_admin_loggedin, client):
        admin = test_admin_loggedin
        response = client.get(reverse('show-companies'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'administration/ShowCompanies.html')


class TestDetailsOfUser:

    @pytest.mark.django_db
    def test_show_company(self, test_admin_loggedin, test_create_user_details, client):
        admin = test_admin_loggedin
        user = test_create_user_details
        response = client.get(reverse('admin-user-details', kwargs={'pk':user.user.id}))
        print(response)
        assert response.status_code == 200
        assertTemplateUsed(response, 'administration/DetailsUser.html')

    @pytest.mark.django_db
    def test_show_company_wrong(self, test_admin_loggedin, client):
        admin = test_admin_loggedin
        response = client.get(reverse('admin-user-details', kwargs={'pk':2}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'administration/errors/403.html')


class TestDetailsOfInterviewer:

    @pytest.mark.django_db
    def test_details_of_interviewer_get(self, client, test_admin_loggedin, test_interviewer_details_admin):
        admin = test_admin_loggedin
        interviewer_company, interviewer_details = test_interviewer_details_admin
        response = client.get(reverse('admin-interviewer-details',kwargs={'pk':interviewer_details.id}))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/DetailsInterviewer.html')

    @pytest.mark.django_db
    def test_details_of_interviewer_wrong_id(self, client, test_admin_loggedin, test_interviewer_details_admin):
        admin = test_admin_loggedin
        interviewer_company, interviewer_details = test_interviewer_details_admin
        response = client.get(reverse('admin-interviewer-details', kwargs={'pk':10}))
        assert response.status_code == 200
        assertTemplateUsed(response, 'administration/errors/403.html')


class TestCompanyRegisterByAdmin:

    @pytest.mark.django_db
    def test_can_page_get(self, client, test_admin_loggedin):
        user = test_admin_loggedin
        response = client.get(reverse('company-register-admin'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'administration/user_register.html')

    @pytest.mark.django_db
    def test_can_page_post_register(self, client, test_admin_loggedin):
        user = test_admin_loggedin
        response = client.post(reverse('company-register-admin'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response,'/administration/company_acceptance/')

    @pytest.mark.django_db
    def test_can_page_post_register_same_password(self, client, test_admin_loggedin):
        user = test_admin_loggedin
        response = client.post(reverse('company-register-admin'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@1234'})
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_can_page_post_register_same_email(self, client, test_create_company, test_admin_loggedin):
        admin = test_admin_loggedin
        user = test_create_company
        response = client.post(reverse('company-register-admin'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Email is already exist.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_name(self, client, test_create_company, test_admin_loggedin):
        admin = test_admin_loggedin
        user = test_create_company
        response = client.post(reverse('company-register-admin'),
                               data={'username': 'Sanskar1234', 'email': 'sanskar36393@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Username is already is taken.'


class TestUserRegisterByAdmin:

    @pytest.mark.django_db
    def test_can_page_get(self, client, test_admin_loggedin):
        user = test_admin_loggedin
        response = client.get(reverse('user-register-admin'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'administration/user_register.html')

    @pytest.mark.django_db
    def test_can_page_post_register(self, client, test_admin_loggedin):
        user = test_admin_loggedin
        response = client.post(reverse('user-register-admin'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@123'})
        assert response.status_code == 302
        assertRedirects(response, '/administration/show_users/')

    @pytest.mark.django_db
    def test_can_page_post_register_same_password(self, client, test_admin_loggedin):
        admin = test_admin_loggedin
        response = client.post(reverse('user-register-admin'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com', 'password': 'test@123',
                                     'confirm_password': 'test@1234'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Your passwords are not matched.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_email(self, client, test_create_user, test_admin_loggedin):
        admin = test_admin_loggedin
        user = test_create_user
        response = client.post(reverse('user-register-admin'),
                               data={'username': 'sanskar123', 'email': 'sanskar3639@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Email is already exist.'

    @pytest.mark.django_db
    def test_can_page_post_register_same_name(self, client, test_create_user, test_admin_loggedin):
        admin = test_admin_loggedin
        user = test_create_user
        response = client.post(reverse('user-register-admin'),
                               data={'username': 'Sanskar1234', 'email': 'sanskar36393@gmail.com',
                                     'password': 'test@123', 'confirm_password': 'test@123'})
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert str(messages[0]) == 'Username is already is taken.'


class TestAdminUpdateUserDetails:

    @pytest.mark.django_db
    def test_admin_update_user_details_get(self, client, test_admin_loggedin, test_create_administrator):
        user = test_create_administrator
        admin = test_admin_loggedin
        response = client.get(reverse('admin-update-profile',kwargs={'pk':user.id}))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/errors/403.html')

    @pytest.mark.django_db
    def test_admin_update_user_details_get_write(self, client, test_admin_loggedin_with_details):
        admin, user = test_admin_loggedin_with_details
        response = client.get(reverse('admin-update-profile',kwargs={'pk':user}))
        assert response.status_code == 200
        assertTemplateUsed(response,'administration/admin_update_profile.html')

    @pytest.mark.django_db
    def test_admin_update_user_details_get_write_update(self, client, test_admin_loggedin_with_details):
        admin, user = test_admin_loggedin_with_details
        cv_file = open(os.path.join(BASE_DIR, 'default.pdf'), 'rb')
        cv_file_obj = File(cv_file)
        response = client.post(reverse('admin-update-profile',kwargs={'pk':user}), data={'user_12th_marks':20,'user_10th_marks':30,'user_CPI':8,'user_phone':'832-049-8936','user_technology':'Python','user_CV':cv_file_obj,'email':'adbyhv@gmail.com'})
        assert response.status_code == 302

    @pytest.mark.django_db
    def test_admin_update_user_details_get_write_update_without_email(self, client, test_admin_loggedin_with_details):
        admin, user = test_admin_loggedin_with_details
        cv_file = open(os.path.join(BASE_DIR, 'default.pdf'), 'rb')
        cv_file_obj = File(cv_file)
        response = client.post(reverse('admin-update-profile', kwargs={'pk': user}),
                               data={'user_12th_marks': 20, 'user_10th_marks': 30, 'user_CPI': 8,
                                     'user_phone': '832-049-8936', 'user_technology': 'Python', 'user_CV': cv_file_obj})
        assert response.status_code == 302


class TestBlockUnblock:

    @pytest.mark.django_db
    def test_collect_final_status_rejected(self, client, test_admin_loggedin, test_create_user):
        user1 = test_create_user
        user = test_admin_loggedin
        response = client.post(reverse('block-unblock'),
                               data={'user_id': user1.id, 'data_value': '0'},
                               content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_collect_final_status_accepted(self, client, test_admin_loggedin, test_create_user):
        user1 = test_create_user
        user = test_admin_loggedin
        response = client.post(reverse('block-unblock'),
                               data={'user_id': user1.id, 'data_status': '1','message':'adbncdhcbv'},
                               content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200


class TestCompanyAcceptReject:

    @pytest.mark.django_db
    def test_collect_final_status_rejected(self, client, test_admin_loggedin, test_company_acceptance_admin):
        user1 = test_company_acceptance_admin
        user = test_admin_loggedin
        response = client.post(reverse('company_accept_reject'),
                               data={'company_id': user1, 'acceptance_status': '0'},
                               content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_collect_final_status_accepted(self, client, test_admin_loggedin, test_company_acceptance_admin):
        user1 = test_company_acceptance_admin
        user = test_admin_loggedin
        response = client.post(reverse('company_accept_reject'),
                               data={'company_id': user1, 'acceptance_status': '1'},
                               content_type='application/json',
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        assert response.status_code == 200
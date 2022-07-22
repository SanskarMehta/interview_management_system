import pytest
from django.urls import reverse

from user_login.models import CustomUser, CompanyAcceptance, InterviewerType, JobOpenings, InterviewerCompany, \
    UserDetails, InterviewerDetails, UserJobApplied, UserInterview, Interview, RescheduleRequests


@pytest.fixture
def test_create_user(db):
    user = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com",password="test@123")
    user.set_password(user.password)
    user.save()
    return user


@pytest.fixture
def test_create_interviewer(db):
    interviewer = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com",password="test@123",is_interviewer=True)
    interviewer.set_password(interviewer.password)
    interviewer.save()
    return interviewer


@pytest.fixture
def test_create_company(db):
    company = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com",password="test@123",is_company=True)
    company.set_password(company.password)
    company.save()
    company_accepted = CompanyAcceptance.objects.create(company=company)
    company_accepted = CompanyAcceptance.objects.filter(company=company).get()
    return company,company_accepted


@pytest.fixture
def test_create_user_blocked(db):
    user = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com",password="test@123",is_block=True)
    user.set_password(user.password)
    user.save()
    return user


@pytest.fixture
def test_create_user_not_activated(db):
    user = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com",password="test@123",is_activated=False)
    user.set_password(user.password)
    user.save()
    return user


@pytest.fixture
def test_user_loggedin(db,client):
    user = CustomUser.objects.create(username="Sanskar12345", email="sanskar3639@gmail.com",password="test@123")
    user.set_password(user.password)
    user.save()
    u_login = client.login(username=user.username,password='test@123')
    assert u_login
    return u_login


@pytest.fixture
def test_interviewer_loggedin(db,client):
    user = CustomUser.objects.create(username="Sanskar12345", email="sanskar3639@gmail.com",password="test@123",is_interviewer=True)
    user.set_password(user.password)
    user.save()
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    interviewer_details = InterviewerDetails.objects.create(interviewer=user, type_interviewer=interviewer_type,
                                                            interviewer_phone='832-049-8866',
                                                            interviewer_technology='Python',
                                                            job_role='Python Developer', Experience='3+ yrs')
    u_login = client.login(username=user.username,password='test@123')
    assert u_login
    return u_login


@pytest.fixture
def test_company_loggedin(db,client):
    company = CustomUser.objects.create(username="Sanskar123456789", email="sanskar3639@gmail.com",password="test@123",is_company=True)
    company.set_password(company.password)
    company.save()
    company_accepted = CompanyAcceptance.objects.create(company=company,is_accepted=True)
    u_login = client.login(username=company.username, password='test@123')
    assert u_login
    return u_login


@pytest.fixture
def test_interviewer_type(db):
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    return interviewer_type


@pytest.fixture
def test_company_job_openings(db):
    company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    return jobopenings


@pytest.fixture
def test_interviewer_company_details_loggedin(db,client):
    company = CustomUser.objects.create(username='Sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    company.set_password(company.password)
    company.save()
    interviewer = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',is_interviewer=True)
    interviewer.set_password(interviewer.password)
    interviewer.save()
    interviewer_company = InterviewerCompany.objects.create(company=company, interviewer=interviewer)
    u_login = client.login(username=interviewer.username, password='test@123')
    print(u_login)
    return u_login


@pytest.fixture
def test_user_with_details_loggedin(db,client):
    user = CustomUser.objects.create(username="Sanskar12345", email="sanskar3639@gmail.com",password="test@123")
    user.set_password(user.password)
    user.save()
    user_details = UserDetails.objects.create(user=user, user_phone='832-049-8866', user_technology='python , dbms',
                                                 user_12th_marks=98.9, user_10th_marks=96, user_CPI=8.87)
    u_login = client.login(username=user.username,password='test@123')
    return u_login


@pytest.fixture
def test_interviewer_with_details_loggedin(db, client):
    user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                     is_interviewer=True)
    user.set_password(user.password)
    user.save()
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    interviewer_details = InterviewerDetails.objects.create(interviewer=user, type_interviewer=interviewer_type,
                                                            interviewer_phone='832-049-8866',
                                                            interviewer_technology='Python',
                                                            job_role='Python Developer', Experience='3+ yrs')
    u_login = client.login(username='Sanskar1234', password='test@123')
    return u_login


@pytest.fixture
def test_user_job_applied(db,client):
    user = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com", password="test@123")
    user.set_password(user.password)
    user.save()
    company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    company.set_password(company.password)
    company.save()
    jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
    u_login = client.login(username=company.username, password='test@123')
    job_id = job_apply.id
    return u_login,job_id


@pytest.fixture
def test_use_interview_company(db,client):
    user = CustomUser.objects.create(username='Sanskar123467', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
    user.set_password(user.password)
    user.save()
    company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    company.set_password(company.password)
    company.save()
    jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
    user_interview = UserInterview.objects.create(job_application=job_apply)
    user_login = client.login(username=company.username , password='test@123')
    return user_interview,user_login


@pytest.fixture
def test_interviewer_details(db,client):
    user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                     is_interviewer=True)
    user.set_password(user.password)
    user.save()
    company = CustomUser.objects.create(username='Sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    interviewer_company = InterviewerCompany.objects.create(company=company, interviewer=user)
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    interviewer_details = InterviewerDetails.objects.create(interviewer=user, type_interviewer=interviewer_type,
                                                            interviewer_phone='832-049-8866',
                                                            interviewer_technology='Python',
                                                            job_role='Python Developer', Experience='3+ yrs')
    return interviewer_details


@pytest.fixture
def test_interview_get_time_slot(db):
    user = CustomUser.objects.create(username='Sanskar12345667', email='sanskar3639@gmail.com', password='test@123',
                                     is_interviewer=True)
    userdetails = UserDetails.objects.create(user=user, user_phone='832-049-8866', user_technology='python , dbms',
                                             user_12th_marks=98.9, user_10th_marks=96, user_CPI=8.87)
    company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
    user_interview = UserInterview.objects.create(job_application=job_apply)
    interviewer = CustomUser.objects.create(username='Sanskar124', email='sanskar3639@gmail.com', password='test@123',
                                            is_interviewer=True)
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    interviewer_details = InterviewerDetails.objects.create(interviewer=interviewer, type_interviewer=interviewer_type,
                                                            interviewer_phone='832-049-8866',
                                                            interviewer_technology='Python',
                                                            job_role='Python Developer', Experience='3+ yrs')
    return user_interview.id,interviewer_details.interviewer.id

@pytest.fixture
def test_interview_reschedule_request(db):
    user = CustomUser.objects.create(username='Sanskar12345667', email='sanskar3639@gmail.com', password='test@123',
                                     is_interviewer=True)
    userdetails = UserDetails.objects.create(user=user, user_phone='832-049-8866', user_technology='python , dbms',
                                             user_12th_marks=98.9, user_10th_marks=96, user_CPI=8.87)
    company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
    user_interview = UserInterview.objects.create(job_application=job_apply)
    interviewer = CustomUser.objects.create(username='Sanskar124', email='sanskar3639@gmail.com', password='test@123',
                                            is_interviewer=True)
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    interviewer_details = InterviewerDetails.objects.create(interviewer=interviewer, type_interviewer=interviewer_type,
                                                            interviewer_phone='832-049-8866',
                                                            interviewer_technology='Python',
                                                            job_role='Python Developer', Experience='3+ yrs')
    interview = Interview.objects.create(application=user_interview, type_interview=interviewer_type,
                                         interviewer=interviewer_details, interview_date='2022-11-11',
                                         interview_time='09:00–09:30')
    return interview.id


@pytest.fixture
def test_interviewer_loggedin_without_details(db,client):
    user = CustomUser.objects.create(username="Sanskar12345", email="sanskar3639@gmail.com",password="test@123",is_interviewer=True)
    user.set_password(user.password)
    user.save()
    u_login = client.login(username=user.username, password='test@123')
    assert u_login
    return u_login


@pytest.fixture
def test_reschedule_request(db, client):
    user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123')
    company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
    user_interview = UserInterview.objects.create(job_application=job_apply)
    interviewer = CustomUser.objects.create(username='Sanskar124', email='sanskar3639@gmail.com',
                                            password='test@123',
                                            is_interviewer=True)
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    interviewer_details = InterviewerDetails.objects.create(interviewer=interviewer,
                                                            type_interviewer=interviewer_type,
                                                            interviewer_phone='832-049-8866',
                                                            interviewer_technology='Python',
                                                            job_role='Python Developer', Experience='3+ yrs')
    interview = Interview.objects.create(application=user_interview, type_interview=interviewer_type,
                                         interviewer=interviewer_details, interview_date='2022-11-11',
                                         interview_time='09:00–09:30')
    reschedule_request = RescheduleRequests.objects.create(interview_application=interview, user=user,
                                                           reason="I unable to give interview on that day.")
    return reschedule_request


@pytest.fixture
def test_delete_company_job_opening(db):
    user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                     is_company=True)
    jobopenings = JobOpenings.objects.create(company=user, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    return jobopenings.id


@pytest.fixture
def test_delete_interviewer(db):
    user = CustomUser.objects.create(username='Interviewer_1', email='int@gmail.com', password='test@123', is_interviewer=True)
    return user.id


@pytest.fixture
def test_admin_login_post(db):
    user = CustomUser.objects.create(username='admin', email='int@gmail.com', password='test@123', is_superuser=True)
    user.set_password(user.password)
    user.save()
    return user


@pytest.fixture
def test_admin_loggedin(db, client):
    user = CustomUser.objects.create(username='admin', email='int@gmail.com', password='test@123', is_superuser=True)
    user.set_password(user.password)
    user.save()
    u_login = client.login(username=user.username, password='test@123')
    return u_login


@pytest.fixture
def test_create_user_details(db):
    user = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com",password="test@123")
    user.set_password(user.password)
    user.save()
    userdetails = UserDetails.objects.create(user=user, user_phone='832-049-8866', user_technology='python , dbms',
                               user_12th_marks=98.9, user_10th_marks=96, user_CPI=8.87)
    return userdetails


@pytest.fixture
def test_create_administrator(db):
    user = CustomUser.objects.create(username='admin1',password='test@123',email='admin@gmail.com',is_superuser=True)
    user.set_password(user.password)
    user.save()
    return user


@pytest.fixture
def test_interviewer_details_admin(db):
    user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                     is_interviewer=True)
    interviewer_type = InterviewerType.objects.create(type='Data Scientist')
    interviewer_details = InterviewerDetails.objects.create(interviewer=user, type_interviewer=interviewer_type,
                                                            interviewer_phone='832-049-8866',
                                                            interviewer_technology='Python',
                                                            job_role='Python Developer', Experience='3+ yrs')
    company = CustomUser.objects.create(username='Sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    interviewer_company = InterviewerCompany.objects.create(company=company, interviewer=user)
    return interviewer_company,interviewer_details


@pytest.fixture
def test_admin_loggedin_with_details(db, client):
    user = CustomUser.objects.create(username='admin', email='int@gmail.com', password='test@123', is_superuser=True)
    user.set_password(user.password)
    user.save()
    user_details = UserDetails.objects.create(user=user, user_phone='832-049-8866', user_technology='python , dbms',
                               user_12th_marks=98.9, user_10th_marks=96, user_CPI=8.87)
    u_login = client.login(username=user.username, password='test@123')
    return u_login,user.id


@pytest.fixture
def test_company_acceptance_admin(db):
    user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                     is_company=True)
    company = CompanyAcceptance.objects.create(company=user)
    return company.id


@pytest.fixture
def test_user_job_applied_with_interview(db,client):
    user = CustomUser.objects.create(username="Sanskar1234", email="sanskar3639@gmail.com", password="test@123")
    user.set_password(user.password)
    user.save()
    company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                        password='test@123',
                                        is_company=True)
    company.set_password(company.password)
    company.save()
    jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                             description='We required a experience developer who have min exp of '
                                                         '3+ yrs')
    job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
    user_interview = UserInterview.objects.create(job_application=job_apply,technical_round='Accepted',HR_round='Accepted')
    u_login = client.login(username=company.username, password='test@123')
    job_id = job_apply.id
    return u_login,job_id

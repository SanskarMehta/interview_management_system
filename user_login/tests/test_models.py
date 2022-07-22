import pytest
from user_login.models import CustomUser, CompanyAcceptance, UserDetails, JobOpenings, InterviewerCompany, \
    InterviewerType, InterviewerDetails, UserJobApplied, UserInterview, Interview, Notification, InterviewerFeedback, \
    UserFeedback, BlockUser, RescheduleRequests


class TestCustomUser(object):
    """Test for CustomUser Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123')
        user_obj = CustomUser.objects.all()
        assert user.email == "sanskar3639@gmail.com"

    @pytest.mark.django_db
    def test_str_name(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123')
        user_obj = CustomUser.objects.all()
        assert str(user) == "Sanskar1234"


class TestCompanyAcceptance(object):
    """Test for CompanyAcceptance Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_company=True)
        company = CompanyAcceptance.objects.create(company=user)
        company_obj = CompanyAcceptance.objects.all()
        assert company.is_accepted == False
        assert company.company.username == 'Sanskar1234'


class TestUserDetails(object):
    """Test for UserDetails Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_company=True)
        userdetails = UserDetails.objects.create(user=user, user_phone='832-049-8866', user_technology='python , dbms',
                                                 user_12th_marks=98.9, user_10th_marks=96, user_CPI=8.87)
        userdetails_obj = UserDetails.objects.all()
        assert userdetails.user_phone == '832-049-8866'
        assert userdetails.user_12th_marks == 98.9
        assert userdetails.user.username == 'Sanskar1234'


class TestJobOpenings(object):
    """Test for JobOpenings Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_company=True)
        jobopenings = JobOpenings.objects.create(company=user, job_location='Remote', job_role='Python Developer',
                                                 description='We required a experience developer who have min exp of '
                                                             '3+ yrs')
        jobopenings_obj = JobOpenings.objects.all()
        assert jobopenings.job_location == 'Remote'
        assert jobopenings.company.username == 'Sanskar1234'


class TestInterviewerCompany(object):
    """Test for InterviewerCompany Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        company = CustomUser.objects.create(username='Sanskar_company', email='sanskar3639@gmail.com',
                                            password='test@123',
                                            is_company=True)
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123')
        interviewer_company = InterviewerCompany.objects.create(company=company, interviewer=user)
        interviewer_company_obj = InterviewerCompany.objects.all()
        assert interviewer_company.interviewer.username == 'Sanskar1234'
        assert interviewer_company.company.username == 'Sanskar_company'


class TestInterviewerType(object):
    """Test for InterviewerType Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        interviewer_type = InterviewerType.objects.create(type='Data Scientist')
        interviewer_type_obj = InterviewerType.objects.all()
        assert interviewer_type.type == 'Data Scientist'

    @pytest.mark.django_db
    def test_str_name(self):
        interviewer_type = InterviewerType.objects.create(type='Data Scientist')
        interviewer_type_obj = InterviewerType.objects.all()
        assert str(interviewer_type) == "Data Scientist"


class TestInterviewerDetails(object):
    """Test for InterviewerDetails Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        interviewer_type = InterviewerType.objects.create(type='Data Scientist')
        interviewer_details = InterviewerDetails.objects.create(interviewer=user, type_interviewer=interviewer_type,
                                                                interviewer_phone='832-049-8866',
                                                                interviewer_technology='Python',
                                                                job_role='Python Developer', Experience='3+ yrs')
        interviewer_details_obj = InterviewerDetails.objects.all()
        assert interviewer_details.type_interviewer.type == 'Data Scientist'
        assert interviewer_details.interviewer_phone == '832-049-8866'
        assert interviewer_details.interviewer.email == 'sanskar3639@gmail.com'

    @pytest.mark.django_db
    def test_str_name(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        interviewer_type = InterviewerType.objects.create(type='Data Scientist')
        interviewer_details = InterviewerDetails.objects.create(interviewer=user, type_interviewer=interviewer_type,
                                                                interviewer_phone='832-049-8866',
                                                                interviewer_technology='Python',
                                                                job_role='Python Developer', Experience='3+ yrs')
        interviewer_details_obj = InterviewerDetails.objects.all()
        assert str(interviewer_details) == user.username


class TestUserJobApplied(object):
    """Test for UserJobApplied Model"""

    @pytest.mark.django_db
    def test_field_value(self, test_create_user, test_company_job_openings):
        user = test_create_user
        jobopenings = test_company_job_openings
        job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
        job_apply_obj = UserJobApplied.objects.all()
        assert job_apply.user.username == 'Sanskar1234'
        assert job_apply.job == jobopenings


class TestUserInterview(object):
    """Test for UserInterview Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                            password='test@123',
                                            is_company=True)
        jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                                 description='We required a experience developer who have min exp of '
                                                             '3+ yrs')
        job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
        user_interview = UserInterview.objects.create(job_application=job_apply)
        user_interview_obj = UserInterview.objects.all()
        assert user_interview.job_application == job_apply
        assert user_interview.technical_round == 'Pending'
        assert user_interview.selection_status == 'Pending'


class TestInterview(object):
    """Test for Interview Model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
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
        interview = Interview.objects.create(application=user_interview,type_interview=interviewer_type,interviewer=interviewer_details,interview_date='2022-11-11',interview_time='09:00–09:30')
        interview_obj = Interview.objects.all()
        assert interview.application == user_interview
        assert interview.interviewer == interviewer_details
        assert interview.interview_date == '2022-11-11'
        assert interview.type_interview == interviewer_type


class TestNotification(object):
    """Test for Notification model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        interviewer = CustomUser.objects.create(username='Sanskar124', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        notification = Notification.objects.create(sender=user,receiver=interviewer,message='Hello EveryOne')
        notification_obj = Notification.objects.all()
        assert notification.sender == user
        assert notification.message == 'Hello EveryOne'


class TestInterviewerFeedback(object):
    """Test for InterviewerFeedback model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        interviewer = CustomUser.objects.create(username='Sanskar124', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        interviewer_feedback = InterviewerFeedback.objects.create(applicant=user,interviewer=interviewer,feedback='You need to improve your behaviour')
        interviewer_feedback_obj = InterviewerFeedback.objects.all()
        assert interviewer_feedback.applicant == user
        assert interviewer_feedback.feedback == 'You need to improve your behaviour'


class TestUserFeedback(object):
    """Test for UserFeedback model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123')
        interviewer = CustomUser.objects.create(username='Sanskar124', email='sanskar3639@gmail.com', password='test@123',
                                         is_interviewer=True)
        company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
                                            password='test@123',
                                            is_company=True)
        jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
                                                 description='We required a experience developer who have min exp of '
                                                             '3+ yrs')
        job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
        user_interview = UserInterview.objects.create(job_application=job_apply)
        user_feedback = UserFeedback.objects.create(user=user,examiner=interviewer,feedback='You need to improve your behaviour',marks=5,application=user_interview)
        user_feedback_obj = UserFeedback.objects.all()
        assert user_feedback.user == user
        assert user_feedback.feedback == 'You need to improve your behaviour'
        assert user_feedback.application == user_interview


class TestRescheduleRequests(object):
    """Test for RescheduleRequests model"""

    @pytest.mark.django_db
    def test_field_value(self,test_reschedule_request):
        # user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123')
        # company = CustomUser.objects.create(username='sanskar_company', email='sanskar3639@gmail.com',
        #                                     password='test@123',
        #                                     is_company=True)
        # jobopenings = JobOpenings.objects.create(company=company, job_location='Remote', job_role='Python Developer',
        #                                          description='We required a experience developer who have min exp of '
        #                                                      '3+ yrs')
        # job_apply = UserJobApplied.objects.create(user=user, job=jobopenings)
        # user_interview = UserInterview.objects.create(job_application=job_apply)
        # interviewer = CustomUser.objects.create(username='Sanskar124', email='sanskar3639@gmail.com',
        #                                         password='test@123',
        #                                         is_interviewer=True)
        # interviewer_type = InterviewerType.objects.create(type='Data Scientist')
        # interviewer_details = InterviewerDetails.objects.create(interviewer=interviewer,
        #                                                         type_interviewer=interviewer_type,
        #                                                         interviewer_phone='832-049-8866',
        #                                                         interviewer_technology='Python',
        #                                                         job_role='Python Developer', Experience='3+ yrs')
        # interview = Interview.objects.create(application=user_interview, type_interview=interviewer_type,
        #                                      interviewer=interviewer_details, interview_date='2022-11-11',
        #                                      interview_time='09:00–09:30')
        # reschedule_request = RescheduleRequests.objects.create(interview_application=interview,user=user,reason="I unable to give interview on that day.")
        reschedule_request = test_reschedule_request
        reschedule_request_obj = RescheduleRequests.objects.all()
        assert reschedule_request.reason == "I unable to give interview on that day."
        assert reschedule_request.is_rescheduled == False


class TestBlockUser(object):
    """Test for BlockUser model"""

    @pytest.mark.django_db
    def test_field_value(self):
        user = CustomUser.objects.create(username='Sanskar1234', email='sanskar3639@gmail.com', password='test@123')
        block_user = BlockUser.objects.create(user=user,reason='You are using in a very bad manner')
        block_user_obj = BlockUser.objects.all()
        assert block_user.user == user
        assert block_user.reason == 'You are using in a very bad manner'
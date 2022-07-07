from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    is_interviewer = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_first_time = models.BooleanField(default=True)
    is_block = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class CompanyAcceptance(models.Model):
    company = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)


class UserDetails(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    user_phone = models.CharField(max_length=12)
    user_technology = models.CharField(max_length=30)
    user_12th_marks = models.FloatField()
    user_10th_marks = models.FloatField()
    user_CPI = models.FloatField()
    user_CV = models.FileField(upload_to='CV/', validators=[FileExtensionValidator(['pdf', 'doc', 'docx'])])
    accepted_status = models.BooleanField(default=False)


class JobOpenings(models.Model):
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job_location = models.CharField(max_length=50)
    job_role = models.CharField(max_length=50)
    description = models.CharField(max_length=300)


class InterviewerCompany(models.Model):
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="company")
    interviewer = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="interview")


class InterviewerType(models.Model):
    type = models.CharField(max_length=30)

    def __str__(self):
        return self.type


class InterviewerDetails(models.Model):
    interviewer = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    type_interviewer = models.ForeignKey(InterviewerType, on_delete=models.CASCADE)
    interviewer_phone = models.CharField(max_length=12)
    interviewer_technology = models.CharField(max_length=30)
    job_role = models.CharField(max_length=30)
    Experience = models.CharField(max_length=30)

    def __str__(self):
        return self.interviewer.username


class UserJobApplied(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_job')
    job = models.ForeignKey(JobOpenings, on_delete=models.CASCADE, related_name="job")
    application_choices = (
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Pending', 'Pending'),
    )
    application_status = models.CharField(max_length=40, choices=application_choices, default='Pending')


class UserInterview(models.Model):
    job_application = models.OneToOneField(UserJobApplied, on_delete=models.CASCADE)
    round_choices = (
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Pending', 'Pending'),
        ('Scheduled', 'Scheduled'),
    )
    technical_round = models.CharField(max_length=15, choices=round_choices, default='Pending')
    HR_round = models.CharField(max_length=15, choices=round_choices, default='Pending')


class Interview(models.Model):
    application = models.ForeignKey(UserInterview, on_delete=models.CASCADE)
    type_interview = models.ForeignKey(InterviewerType, on_delete=models.CASCADE)
    interviewer = models.ForeignKey(InterviewerDetails, on_delete=models.CASCADE)
    TIMESLOT_LIST = (
        ('09:00–09:30', '09:00–09:30'),
        ('10:00–10:30', '10:00–10:30'),
        ('11:00–11:30', '11:00–11:30'),
        ('12:00–12:30', '12:00–12:30'),
        ('13:00–13:30', '13:00–13:30'),
        ('14:00–14:30', '14:00–14:30'),
        ('15:00–15:30', '15:00–15:30'),
        ('16:00–16:30', '16:00–16:30'),
        ('17:00–17:30', '17:00-17:30'),
    )
    interview_date = models.DateField()
    interview_time = models.CharField(max_length=20, choices=TIMESLOT_LIST)


class Notification(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Sender')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Receiver')
    message = models.CharField(max_length=300)


class InterviewerFeedback(models.Model):
    applicant = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Applicant')
    interviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Interviewer')
    feedback = models.CharField(max_length=300, null=False)


class UserFeedback(models.Model):
    examiner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='Examiner', default=1)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='User', default=1)
    feedback = models.CharField(max_length=300, null=False, default='You are good enough but you need little bit '
                                                                    'improvement')
    marks = models.FloatField(default=0)
    application = models.ForeignKey(UserInterview, on_delete=models.CASCADE, default=1)


class RescheduleRequests(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user')
    interview_application = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='Interview_Id',
                                              default=1)
    reason = models.CharField(max_length=300)
    is_rescheduled = models.BooleanField(default=False)

class BlockUser(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = models.CharField(max_length=300)

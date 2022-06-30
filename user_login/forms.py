from datetime import date, datetime
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.contrib.auth.forms import UserCreationForm, forms
from django.core.exceptions import ValidationError

from .models import CustomUser, UserDetails, InterviewerDetails, JobOpenings, Interview, UserFeedback


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = '__all__'


class userDetails(forms.ModelForm):
    class Meta:
        model = UserDetails
        fields = '__all__'


class UpdateUserDetailForm(forms.ModelForm):
    user_CPI = forms.FloatField(max_value=10.0, min_value=0.0)
    user_12th_marks = forms.FloatField(max_value=100.0, min_value=0.0)
    user_10th_marks = forms.FloatField(max_value=100.0, min_value=0.0)

    class Meta:
        model = UserDetails
        fields = ['user_12th_marks', 'user_10th_marks', 'user_CPI', 'user_phone', 'user_technology', 'user_CV']


class UpdateInterviewerDetailForm(forms.ModelForm):
    class Meta:
        model = InterviewerDetails
        fields = ['type_interviewer', 'interviewer_phone', 'interviewer_technology', 'job_role', 'Experience']


class UserEmailUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email']


class UpdateJobOpenings(forms.ModelForm):
    class Meta:
        model = JobOpenings
        fields = ['job_location', 'job_role', 'description']


class DateInput(forms.DateInput):
    input_type = 'date'


class ScheduleInterviews(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['type_interview', 'interviewer', 'interview_date', 'interview_time']
        now = datetime.now()
        widgets = {
            'interview_date': DatePickerInput(options={'minDate': now.strftime("%Y/%m/%d")})
        }


class UserFeedbackByInterviewer(forms.ModelForm):
    marks = forms.FloatField(min_value=0.0 , max_value=10.0)

    class Meta:
        model = UserFeedback
        fields = ['marks', 'feedback']

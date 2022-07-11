from django.contrib.auth.mixins import LoginRequiredMixin


class UserLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.is_company or request.user.is_interviewer:
            return self.handle_no_permission()
        else:
            return super().dispatch(request, *args, **kwargs)


class CompanyLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_company:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


class InterviewerLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_interviewer:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


class AdminLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            return self.handle_no_permission()


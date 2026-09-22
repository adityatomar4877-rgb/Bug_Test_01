from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email


class LoginForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None and '@' in username:
                try:
                    matched = User.objects.get(email__iexact=username)
                    self.user_cache = authenticate(
                        self.request, username=matched.username, password=password
                    )
                    if self.user_cache is None:
                        self.user_cache = matched
                except User.DoesNotExist:
                    pass
            if self.user_cache is None:
                raise self.get_invalid_login_error()
        return self.cleaned_data

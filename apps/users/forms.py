# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False, help_text='手机号码（可选）')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')

class UserLoginForm(forms.Form):
    username = forms.CharField(label='用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput)

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'phone']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'phone': forms.TextInput(attrs={'placeholder': '请输入手机号码'})
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')

class LoginForm(forms.Form):
    username = forms.CharField(label='用户名')
    password = forms.CharField(label='密码', widget=forms.PasswordInput)
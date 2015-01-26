from django.contrib.auth.forms import UserCreationForm
from django import forms
from os import path
from ask.models import *

class AskForm(forms.Form):
	title = forms.CharField(required=True, max_length=50,
		error_messages={'required': 'Question needs a title', 
		'max_length': 'This title is too long'})
	text = forms.CharField(required=True,
		error_messages={'required': 'Question needs some text'})
	tags = forms.CharField(required=False)


class AnswerForm(forms.Form):
	text = forms.CharField(required=True, 
		error_messages={'required': 'Answers can\'t be empty!'})


class LoginForm(forms.Form):
    login = forms.CharField(required=True, max_length=20)
    password = forms.CharField(required=True)


class SignUpForm(UserCreationForm):
	username = forms.CharField(required=True, max_length=20,
		error_messages={'required': 'Please enter your login', 
		'max_length': 'Login is 20 chars max'})
	email = forms.EmailField(required=True,
		error_messages={'required': 'Please enter your email'})
	nickname = forms.CharField(required=True, max_length=20,
		error_messages={'required': 'Please enter your nickname', 
		'max_length': 'Nickname is 20 chars max'})
	password1 = forms.CharField(required=True,
		error_messages={'required': 'Password is required'})
	password2 = forms.CharField(required=True,
		error_messages={'required': 'Please confirm your password'})

	def clean_nickname(self):
		nickname = self.cleaned_data['nickname']
		if User.objects.filter(first_name = nickname).exists():
			raise forms.ValidationError("Nickname already exists")
		return nickname

	def clean_email(self):
		email = self.cleaned_data['email']
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError("Email already exists")
		return email

	def clean_password2(self):
		password1 = self.cleaned_data['password1']
		password2 = self.cleaned_data['password2']

		if password1 and password2:
			if password1 != password2:
				raise forms.ValidationError("Passwords should match")
		return password2


class SettingsForm(forms.Form):
	login = forms.CharField(required=True, max_length=20,
		error_messages={'required': 'Please enter your login', 
		'max_length': 'Login is 20 chars max'})
	email = forms.EmailField(required=True,
		error_messages={'required': 'Please enter your email'})
	nickname = forms.CharField(required=True, max_length=20,
		error_messages={'required': 'Please enter your nickname', 
		'max_length': 'Nickname is 20 chars max'})
	avatar = forms.ImageField(required=False, max_length=100)

	def clean(self):
		cleaned_data = super(SettingsForm, self).clean()
		avatar = self.cleaned_data.get('avatar')
		login = self.cleaned_data.get('login')

		if avatar and login:
			try:
				name, ext = path.splitext(avatar.name)
				avatar.name = str(User.objects.get(username=login).id) + ext
			except:
				pass

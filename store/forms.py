from django import forms
from django.contrib.auth.models import User
from .models import Address, Profile


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'line1', 'line2', 'city', 'state', 'postal_code', 'country']


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'avatar']


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

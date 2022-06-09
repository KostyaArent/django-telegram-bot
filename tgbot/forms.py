from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User, Vacancy, EmployeeValues, ProfileStatusHistory

from django.forms import (
    TextInput, IntegerField, ModelForm, Select, ClearableFileInput,
    Textarea, ModelChoiceField, FileField, CheckboxInput
    )


class BroadcastForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    broadcast_text = forms.CharField(widget=forms.Textarea)


class CustomAuthForm(AuthenticationForm):

    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(CustomAuthForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget = TextInput(attrs={
            'id': 'floatingInput',
            'class': 'form-control',
            'name': 'username',
            'placeholder': 'login'})
        self.fields['password'].widget = TextInput(attrs={
            'type': 'password',
            'id': 'floatingPassword',
            'class': 'form-control',
            'name': 'password',
            'placeholder': 'Password'})


class VacancyForm(ModelForm):

    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'is_active']

    def __init__(self, *args, **kwargs):
        super(VacancyForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget = TextInput(
            attrs={
                'id': 'floatingInput',
                'class': 'form-control'
            })
        self.fields['description'].widget = Textarea(
            attrs={
                'id': "floatingTextarea",   
                'class': 'form-control'
            })
        self.fields['is_active'].widget = CheckboxInput(
            attrs={
                'id': "exampleCheck1",   
                'class': 'form-check-input'
            })


class EmployeeValuesForm(ModelForm):

    class Meta:
        model = EmployeeValues
        fields = ['title', 'is_base']

    def __init__(self, *args, **kwargs):
        super(EmployeeValuesForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget = TextInput(
            attrs={
                'id': 'floatingInput',
                'class': 'form-control'
            })
        self.fields['is_base'].widget = CheckboxInput(
            attrs={
                'id': "exampleCheck1",   
                'class': 'form-check-input'
            })



class ProfileStatusHistoryForm(ModelForm):
    class Meta:
        model = ProfileStatusHistory
        fields = '__all__'
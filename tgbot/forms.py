from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User

from django.forms import (
    TextInput, IntegerField, ModelForm, Select, ClearableFileInput,
    Textarea, ModelChoiceField, FileField
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
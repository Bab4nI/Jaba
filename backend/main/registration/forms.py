from django import forms


class RegistrationEmailForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    group = forms.CharField(max_length=100)

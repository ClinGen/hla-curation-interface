from django import forms


class PHIForm(forms.Form):
    agree = forms.CheckboxInput()

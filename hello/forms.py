from django import forms

class PatentForm(forms.Form):
    file = forms.FileField() # for creating file input

from django import forms

class PatentForm(forms.Form):
    url = forms.CharField(label="Enter file url or upload file",max_length=50)
    file = forms.FileField() # for creating file input

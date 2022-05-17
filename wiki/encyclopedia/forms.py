from django import forms

class NewEntryForm(forms.Form):
    title = forms.CharField(label="New entry title", widget=forms.TextInput(attrs={"class" : "field_text"}))
    text = forms.CharField(widget=forms.Textarea(attrs={"class" : "field_area"}))
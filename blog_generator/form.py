# forms.py
from django import forms
from .models import AIModel

class AIModelForm(forms.Form):
    model = forms.ModelChoiceField(queryset=AIModel.objects.all(), label='Select AI Model', empty_label=None)

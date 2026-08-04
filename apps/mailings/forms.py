from django import forms
from .models import Mailing
from apps.email_messages.models import Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ['start_datetime', 'end_datetime', 'message', 'recipients']
        widgets = {
            'start_datetime': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'end_datetime': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 5}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_datetime')
        end = cleaned_data.get('end_datetime')

        if start and end and start >= end:
            raise forms.ValidationError(
                'Дата и время окончания должны быть позже даты и времени начала'
            )
        return cleaned_data

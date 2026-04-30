from django import forms
from .models import WorkingHours


class WorkingHoursForm(forms.ModelForm):
    is_closed = forms.BooleanField(
        required=False,
        label='Closed this day',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = WorkingHours
        fields = ['opening_time', 'closing_time', 'is_closed']
        widgets = {
            'opening_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
            'closing_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control'
            }),
        }


class WorkingHoursFormSet(forms.BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                continue
            if not form.cleaned_data.get('is_closed'):
                opening_time = form.cleaned_data.get('opening_time')
                closing_time = form.cleaned_data.get('closing_time')
                if opening_time and closing_time and opening_time >= closing_time:
                    raise forms.ValidationError('Opening time must be before closing time.')

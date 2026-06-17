from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Recognition, Redemption


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(
            attrs={
                'autofocus': True,
                'autocomplete': 'email',
                'placeholder': 'name@adani.example',
            }
        ),
    )

    error_messages = {
        'invalid_login': 'Please enter a correct email and password.',
        'inactive': 'This account is inactive.',
    }


class RecognitionForm(forms.ModelForm):
    class Meta:
        model = Recognition
        fields = ['receiver', 'tokens', 'category', 'message']
        widgets = {
            'tokens': forms.NumberInput(attrs={'min': 1, 'placeholder': '25'}),
            'message': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Share the impact this colleague created...',
                }
            ),
        }

    def __init__(self, *args, sender=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.sender = sender
        if sender:
            self.fields['receiver'].queryset = (
                self.fields['receiver'].queryset.exclude(pk=sender.pk)
            )
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_tokens(self):
        tokens = self.cleaned_data['tokens']
        if self.sender:
            self.sender.reset_monthly_budget_if_needed()
            if tokens > self.sender.tokens_remaining:
                raise forms.ValidationError(
                    f'You have {self.sender.tokens_remaining} tokens remaining this month.'
                )
        return tokens


class RedemptionForm(forms.ModelForm):
    class Meta:
        model = Redemption
        fields = ['reward']

    def __init__(self, *args, employee=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.employee = employee
        self.fields['reward'].queryset = (
            self.fields['reward']
            .queryset.filter(is_active=True, stock__gt=0)
            .order_by('points_required', 'name')
        )
        self.fields['reward'].widget.attrs.setdefault('class', 'form-control')

    def clean_reward(self):
        reward = self.cleaned_data['reward']
        if self.employee and reward.points_required > self.employee.redeemable_points:
            raise forms.ValidationError(
                f'You have {self.employee.redeemable_points} points available.'
            )
        return reward

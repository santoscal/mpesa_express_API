from django import forms

class PaymentForm(forms.Form):
    phone = forms.CharField(max_length=10, label='Phone Number')
    amount = forms.DecimalField(max_digits=100, decimal_places=2, label='Amount')

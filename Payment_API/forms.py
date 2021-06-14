from django import forms
from Payment_API.models import BillingAddress

class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ['address', 'zip_code', 'city', 'country']

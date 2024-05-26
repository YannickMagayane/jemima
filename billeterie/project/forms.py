from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, Destination, Ticket, Payment

class LoginForm(forms.Form):
    phone_number = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300",
                "placeholder": "Numéro de téléphone",
                "title": "Numéro de téléphone"
            }
        )
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300",
                "placeholder": "Mot de passe",
                "title": "Mot de passe"
            }
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        phone_number = cleaned_data.get('phone_number')
        password = cleaned_data.get('password')

        if phone_number and password:
            user = authenticate(phone_number=phone_number, password=password)
            if not user:
                raise forms.ValidationError("Numéro de téléphone ou mot de passe incorrect.")
        return cleaned_data

# Form for User Registration
class RegisterForm(UserCreationForm):
    phone_number = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300",
                "placeholder": "Numéro de téléphone",
                "title": "Numéro de téléphone"
            }
        )
    )


    name = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300",
                "placeholder": "Prénom",
                "title": "Prénom"
            }
        )
    )
    last_name = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300",
                "placeholder": "Nom de famille",
                "title": "Nom de famille"
            }
        )
    )

    password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300",
                "placeholder": "Mot de passe",
                "title": "Mot de passe"
            }
        )
    )
    password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300",
                "placeholder": "Confirmer le mot de passe",
                "title": "Confirmer le mot de passe"
            }
        )
    )

    class Meta:
        model = User
        fields = ('name', 'last_name', 'phone_number', 'password1', 'password2')


# Form for Destination
class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ('name', 'photo', 'montant')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300'}),
            'photo': forms.FileInput(attrs={'class': 'form-input'}),
            'montant': forms.NumberInput(attrs={'class': 'border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300'}),
        }

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['departure_date', 'departure_time', 'amount_paid']
        widgets = {
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time'}),
            'amount_paid': forms.NumberInput(attrs={'min': 0}),
        }

# Form for Payment
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('ticket', 'transaction_id')
        widgets = {
            'ticket': forms.Select(attrs={'class': 'border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300'}),
            'transaction_id': forms.TextInput(attrs={'class': 'border rounded-md px-3 py-2 placeholder-gray-400 focus:outline-none focus:ring focus:border-blue-300'}),
        }

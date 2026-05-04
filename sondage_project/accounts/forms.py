from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur


class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmer le mot de passe'}),
    )

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Nom d'utilisateur"}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'username': "Nom d'utilisateur",
            'email': 'Adresse email',
            'role': 'Rôle',
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class ConnexionForm(AuthenticationForm):
    username = forms.EmailField(
        label='Adresse email',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Adresse email', 'autofocus': True}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
    )


class ProfilForm(forms.ModelForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'role', 'bio', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

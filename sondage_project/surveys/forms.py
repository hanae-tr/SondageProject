from django import forms
from .models import Sondage, Question, Choix, ModèleSondage


class SondageForm(forms.ModelForm):
    class Meta:
        model = Sondage
        fields = [
            'titre', 'description', 'est_actif', 'est_prive',
            'mode_passe', 'date_debut', 'date_fin', 'une_seule_reponse'
        ]
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du sondage'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description (optionnel)'}),
            'est_actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_prive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'mode_passe': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Laisser vide = aucun mot de passe'}, render_value=True),
            'date_debut': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'une_seule_reponse': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titre': 'Titre',
            'description': 'Description',
            'est_actif': 'Sondage actif',
            'est_prive': 'Sondage privé (lien direct uniquement)',
            'mode_passe': 'Mot de passe de protection',
            'date_debut': 'Date de début',
            'date_fin': 'Date de fin (optionnel)',
            'une_seule_reponse': 'Une seule réponse par participant',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_debut'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['date_fin'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['date_fin'].required = False


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['texte', 'type_question', 'ordre', 'est_obligatoire']
        widgets = {
            'texte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Texte de la question'}),
            'type_question': forms.Select(attrs={'class': 'form-select question-type-select'}),
            'ordre': forms.NumberInput(attrs={'class': 'form-control'}),
            'est_obligatoire': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ChoixForm(forms.ModelForm):
    class Meta:
        model = Choix
        fields = ['texte', 'ordre']
        widgets = {
            'texte': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option de réponse'}),
            'ordre': forms.NumberInput(attrs={'class': 'form-control', 'style': 'width:80px'}),
        }


class MotDePasseSondageForm(forms.Form):
    """Formulaire de vérification du mot de passe d'un sondage privé"""
    mot_de_passe = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le mot de passe'}),
    )

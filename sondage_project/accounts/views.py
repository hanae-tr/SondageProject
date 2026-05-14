from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm, ProfilForm
from responses.models import Reponse


def inscription(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Compte créé avec succès.")
            return redirect('dashboard')
    else:
        form = InscriptionForm()
    return render(request, 'accounts/inscription.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bienvenue, {user.username} !")
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, "Email ou mot de passe incorrect.")
    else:
        form = ConnexionForm()
    return render(request, 'accounts/connexion.html', {'form': form})


def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('home')


@login_required
def profil(request):
    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect('profil')
    else:
        form = ProfilForm(instance=request.user)

    ctx = {
        'form': form,
        'sondages_crees': request.user.sondages_crees.all().order_by('-date_creation')[:5],
        'reponses_donnees': Reponse.objects.filter(participant__utilisateur=request.user).order_by('-date_envoi')[:5],
    }
    return render(request, 'accounts/profil.html', ctx)
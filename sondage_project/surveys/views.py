from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Sondage, Question, Choix, ModèleSondage
from .forms import SondageForm, QuestionForm, ChoixForm, MotDePasseSondageForm


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    sondages = request.user.sondages_crees.all().order_by('-date_creation')
    stats = {
        'total':         sondages.count(),
        'actifs':        sondages.filter(est_actif=True).count(),
        'total_reponses': sum(s.reponse_set.count() for s in sondages),
    }
    return render(request, 'surveys/dashboard.html', {
        'sondages': sondages,
        'stats': stats,
    })


# ── Créer un sondage ──────────────────────────────────────────────────────────

@login_required
def creer_sondage(request):
    if request.method == 'POST':
        form = SondageForm(request.POST)
        if form.is_valid():
            sondage = form.save(commit=False)
            sondage.createur = request.user
            sondage.save()
            messages.success(request, "Sondage créé ! Ajoutez maintenant vos questions.")
            return redirect('editer_questions', slug=sondage.slug)
    else:
        form = SondageForm()
    return render(request, 'surveys/creer_sondage.html', {'form': form})


# ── Modifier un sondage ───────────────────────────────────────────────────────

@login_required
def modifier_sondage(request, slug):
    sondage = get_object_or_404(Sondage, slug=slug, createur=request.user)
    if request.method == 'POST':
        form = SondageForm(request.POST, instance=sondage)
        if form.is_valid():
            form.save()
            messages.success(request, "Sondage mis à jour.")
            return redirect('dashboard')
    else:
        form = SondageForm(instance=sondage)
    return render(request, 'surveys/modifier_sondage.html', {'form': form, 'sondage': sondage})


# ── Supprimer un sondage ──────────────────────────────────────────────────────

@login_required
def supprimer_sondage(request, slug):
    sondage = get_object_or_404(Sondage, slug=slug, createur=request.user)
    if request.method == 'POST':
        sondage.delete()
        messages.success(request, "Sondage supprimé.")
        return redirect('dashboard')
    return render(request, 'surveys/confirmer_suppression.html', {'sondage': sondage})


# ── Dupliquer un sondage ──────────────────────────────────────────────────────

@login_required
def dupliquer_sondage(request, slug):
    sondage = get_object_or_404(Sondage, slug=slug, createur=request.user)
    copie = sondage.dupliquer(request.user)
    messages.success(request, f"Sondage dupliqué : '{copie.titre}'")
    return redirect('modifier_sondage', slug=copie.slug)


# ── Éditeur de questions ──────────────────────────────────────────────────────

@login_required
def editer_questions(request, slug):
    sondage   = get_object_or_404(Sondage, slug=slug, createur=request.user)
    questions = sondage.question_set.prefetch_related('choix_set').order_by('ordre')
    return render(request, 'surveys/editer_questions.html', {
        'sondage':   sondage,
        'questions': questions,
    })


@login_required
def ajouter_question(request, slug):
    sondage = get_object_or_404(Sondage, slug=slug, createur=request.user)
    if request.method == 'POST':
        texte          = request.POST.get('texte', '').strip()
        type_question  = request.POST.get('type_question', 'choix_unique')
        ordre          = request.POST.get('ordre', sondage.question_set.count() + 1)
        est_obligatoire = request.POST.get('est_obligatoire') == 'on'

        if texte:
            question = Question.objects.create(
                sondage=sondage,
                texte=texte,
                type_question=type_question,
                ordre=int(ordre),
                est_obligatoire=est_obligatoire,
            )
            # Sauvegarder les choix envoyés
            choix_textes = request.POST.getlist('choix[]')
            for i, ct in enumerate(choix_textes):
                if ct.strip():
                    Choix.objects.create(question=question, texte=ct.strip(), ordre=i)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'question_id': question.id})
            messages.success(request, "Question ajoutée.")

    return redirect('editer_questions', slug=slug)


@login_required
def supprimer_question(request, question_id):
    question = get_object_or_404(Question, id=question_id, sondage__createur=request.user)
    slug = question.sondage.slug
    question.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    messages.success(request, "Question supprimée.")
    return redirect('editer_questions', slug=slug)


# ── Vue publique d'un sondage ─────────────────────────────────────────────────

def detail_sondage(request, slug):
    sondage = get_object_or_404(Sondage, slug=slug)

    # Vérification mot de passe
    if sondage.mode_passe:
        session_key = f'sondage_acces_{sondage.slug}'
        if not request.session.get(session_key):
            if request.method == 'POST':
                form = MotDePasseSondageForm(request.POST)
                if form.is_valid():
                    if form.cleaned_data['mot_de_passe'] == sondage.mode_passe:
                        request.session[session_key] = True
                    else:
                        messages.error(request, "Mot de passe incorrect.")
                        return render(request, 'surveys/mot_de_passe.html', {'form': form, 'sondage': sondage})
            else:
                form = MotDePasseSondageForm()
                return render(request, 'surveys/mot_de_passe.html', {'form': form, 'sondage': sondage})

    if not sondage.est_ouvert():
        return render(request, 'surveys/sondage_ferme.html', {'sondage': sondage})

    questions = sondage.question_set.prefetch_related('choix_set').order_by('ordre')
    return render(request, 'surveys/detail_sondage.html', {
        'sondage':   sondage,
        'questions': questions,
    })


def liste_sondages_publics(request):
    sondages = Sondage.objects.filter(est_actif=True, est_prive=False).order_by('-date_creation')
    return render(request, 'surveys/liste_publique.html', {'sondages': sondages})

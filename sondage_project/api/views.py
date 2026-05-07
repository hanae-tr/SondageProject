from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Count

from surveys.models import Sondage, Question, Choix
from responses.models import Reponse, ReponseDetail
from accounts.models import Utilisateur, Anonyme, Participant
from .serializers import (
    SondageListSerializer, SondageDetailSerializer, SondageCreateSerializer,
    QuestionSerializer, ChoixSerializer,
    ReponseSerializer, StatsQuestionSerializer, UtilisateurSerializer,
)


# ── Permissions personnalisées ─────────────────────────────────────────────────

class EstCreateur(permissions.BasePermission):
    """Seul le créateur du sondage peut modifier/supprimer"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.createur == request.user


# ── Sondages ──────────────────────────────────────────────────────────────────

class SondageListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/sondages/        → liste des sondages publics
    POST /api/sondages/        → créer un sondage (auth requise)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SondageCreateSerializer
        return SondageListSerializer

    def get_queryset(self):
        qs = Sondage.objects.filter(est_actif=True, est_prive=False)
        # Filtres optionnels via query params
        createur = self.request.query_params.get('createur')
        if createur:
            qs = qs.filter(createur__username=createur)
        return qs.order_by('-date_creation')

    def get_serializer_context(self):
        return {'request': self.request}


class MesSondagesView(generics.ListAPIView):
    """
    GET /api/sondages/mes-sondages/  → sondages du créateur connecté
    """
    serializer_class   = SondageListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.sondages_crees.all().order_by('-date_creation')

    def get_serializer_context(self):
        return {'request': self.request}


class SondageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/sondages/<slug>/  → détail + questions
    PUT    /api/sondages/<slug>/  → modifier (créateur seulement)
    DELETE /api/sondages/<slug>/  → supprimer (créateur seulement)
    """
    queryset           = Sondage.objects.all()
    lookup_field       = 'slug'
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, EstCreateur]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SondageCreateSerializer
        return SondageDetailSerializer

    def get_serializer_context(self):
        return {'request': self.request}


# ── Questions ─────────────────────────────────────────────────────────────────

class QuestionListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/sondages/<slug>/questions/  → liste des questions
    POST /api/sondages/<slug>/questions/  → ajouter une question
    """
    serializer_class   = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        sondage = get_object_or_404(Sondage, slug=self.kwargs['slug'])
        return sondage.question_set.prefetch_related('choix_set').order_by('ordre')

    def perform_create(self, serializer):
        sondage = get_object_or_404(Sondage, slug=self.kwargs['slug'])
        if sondage.createur != self.request.user:
            raise permissions.PermissionDenied("Vous n'êtes pas le créateur de ce sondage.")
        serializer.save(sondage=sondage)


class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/questions/<id>/  → détail question
    PUT    /api/questions/<id>/  → modifier
    DELETE /api/questions/<id>/  → supprimer
    """
    queryset           = Question.objects.all()
    serializer_class   = QuestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def check_object_permissions(self, request, obj):
        if request.method not in permissions.SAFE_METHODS:
            if obj.sondage.createur != request.user:
                raise permissions.PermissionDenied()
        super().check_object_permissions(request, obj)


# ── Statistiques (données pour Chart.js) ──────────────────────────────────────

class StatsView(APIView):
    """
    GET /api/sondages/<slug>/stats/
    Retourne toutes les stats du sondage formatées pour Chart.js
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, slug):
        sondage   = get_object_or_404(Sondage, slug=slug)
        questions = sondage.question_set.prefetch_related('choix_set').order_by('ordre')
        total_reponses = sondage.reponse_set.filter(est_complete=True).count()

        stats_questions = []

        for question in questions:
            stat = {
                'question_id':    question.id,
                'question_texte': question.texte,
                'type_question':  question.type_question,
                'total':          0,
                'donnees':        [],
            }

            if question.type_question in ['choix_unique', 'choix_multiple']:
                donnees = []
                for choix in question.obtenir_choix():
                    count = choix.compter_reponses()
                    donnees.append({'label': choix.texte, 'count': count})
                total = sum(d['count'] for d in donnees)
                for d in donnees:
                    d['pourcentage'] = round((d['count'] / total * 100) if total else 0, 1)
                stat['donnees'] = donnees
                stat['total']   = total

                # Format Chart.js
                stat['chartjs'] = {
                    'labels':   [d['label'] for d in donnees],
                    'datasets': [{
                        'data': [d['count'] for d in donnees],
                        'backgroundColor': [
                            '#4F46E5','#0EA5E9','#10B981',
                            '#F59E0B','#EF4444','#8B5CF6',
                        ],
                    }]
                }

            elif question.type_question == 'echelle':
                details = ReponseDetail.objects.filter(
                    question=question, reponse__est_complete=True
                ).exclude(valeur_texte='')
                valeurs = [int(d.valeur_texte) for d in details if d.valeur_texte.isdigit()]
                distribution = [valeurs.count(i) for i in range(1, 6)]
                stat['moyenne']       = round(sum(valeurs) / len(valeurs), 2) if valeurs else 0
                stat['distribution']  = distribution
                stat['total']         = len(valeurs)
                stat['chartjs'] = {
                    'labels': ['1 ★', '2 ★★', '3 ★★★', '4 ★★★★', '5 ★★★★★'],
                    'datasets': [{
                        'label': 'Votes',
                        'data':  distribution,
                        'backgroundColor': [
                            '#EF4444','#F97316','#F59E0B','#84CC16','#10B981'
                        ],
                    }]
                }

            elif question.type_question == 'texte':
                details = ReponseDetail.objects.filter(
                    question=question, reponse__est_complete=True
                ).exclude(valeur_texte='')
                stat['reponses_texte'] = [d.valeur_texte for d in details]
                stat['total']          = details.count()

            stats_questions.append(stat)

        return Response({
            'sondage':         sondage.titre,
            'slug':            str(sondage.slug),
            'total_reponses':  total_reponses,
            'stats_questions': stats_questions,
        })


class StatsQuestionView(APIView):
    """
    GET /api/questions/<id>/stats/
    Stats d'une seule question — pour refresh temps réel
    """
    def get(self, request, pk):
        question = get_object_or_404(Question, pk=pk)
        data = {
            'question_id':    question.id,
            'question_texte': question.texte,
            'type':           question.type_question,
            'labels':         [],
            'values':         [],
        }

        if question.type_question in ['choix_unique', 'choix_multiple']:
            for choix in question.obtenir_choix():
                data['labels'].append(choix.texte)
                data['values'].append(choix.compter_reponses())

        elif question.type_question == 'echelle':
            data['labels'] = ['1', '2', '3', '4', '5']
            details = ReponseDetail.objects.filter(
                question=question, reponse__est_complete=True
            )
            for i in range(1, 6):
                data['values'].append(details.filter(valeur_texte=str(i)).count())

        return Response(data)


# ── Réponses ──────────────────────────────────────────────────────────────────

class ReponseListView(generics.ListAPIView):
    """
    GET /api/sondages/<slug>/reponses/  → toutes les réponses (créateur seulement)
    """
    serializer_class   = ReponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        sondage = get_object_or_404(Sondage, slug=self.kwargs['slug'])
        if sondage.createur != self.request.user:
            raise permissions.PermissionDenied("Accès réservé au créateur.")
        return sondage.reponse_set.filter(est_complete=True).order_by('-date_envoi')


# ── Profil utilisateur ─────────────────────────────────────────────────────────

class ProfilView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/profil/  → mon profil
    PUT  /api/profil/  → modifier mon profil
    """
    serializer_class   = UtilisateurSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# ── Endpoint de santé ─────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_status(request):
    """GET /api/  → infos générales de l'API"""
    return Response({
        'status':    'ok',
        'version':   'v1',
        'endpoints': {
            'sondages':        '/api/sondages/',
            'mes_sondages':    '/api/sondages/mes-sondages/',
            'detail_sondage':  '/api/sondages/<slug>/',
            'questions':       '/api/sondages/<slug>/questions/',
            'stats_sondage':   '/api/sondages/<slug>/stats/',
            'stats_question':  '/api/questions/<id>/stats/',
            'reponses':        '/api/sondages/<slug>/reponses/',
            'profil':          '/api/profil/',
        }
    })

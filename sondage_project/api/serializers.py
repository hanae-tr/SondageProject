from rest_framework import serializers
from surveys.models import Sondage, Question, Choix, ModèleSondage
from responses.models import Reponse, ReponseDetail
from accounts.models import Utilisateur


# ── Choix ─────────────────────────────────────────────────────────────────────

class ChoixSerializer(serializers.ModelSerializer):
    nb_reponses = serializers.SerializerMethodField()

    class Meta:
        model  = Choix
        fields = ['id', 'texte', 'ordre', 'nb_reponses']

    def get_nb_reponses(self, obj):
        return obj.compter_reponses()


# ── Question ──────────────────────────────────────────────────────────────────

class QuestionSerializer(serializers.ModelSerializer):
    choix = ChoixSerializer(many=True, read_only=True, source='choix_set')

    class Meta:
        model  = Question
        fields = [
            'id', 'texte', 'type_question', 'ordre',
            'est_obligatoire', 'choix',
            'condition_question', 'condition_choix',
        ]


# ── Sondage (liste) ───────────────────────────────────────────────────────────

class SondageListSerializer(serializers.ModelSerializer):
    createur        = serializers.StringRelatedField()
    nb_questions    = serializers.SerializerMethodField()
    nb_reponses     = serializers.SerializerMethodField()
    est_ouvert      = serializers.SerializerMethodField()
    lien_partage    = serializers.SerializerMethodField()

    class Meta:
        model  = Sondage
        fields = [
            'id', 'titre', 'description', 'slug',
            'createur', 'est_actif', 'est_prive',
            'date_debut', 'date_fin', 'date_creation',
            'nb_questions', 'nb_reponses', 'est_ouvert', 'lien_partage',
        ]

    def get_nb_questions(self, obj):
        return obj.question_set.count()

    def get_nb_reponses(self, obj):
        return obj.reponse_set.filter(est_complete=True).count()

    def get_est_ouvert(self, obj):
        return obj.est_ouvert()

    def get_lien_partage(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/reponses/{obj.slug}/repondre/')
        return f'/reponses/{obj.slug}/repondre/'


# ── Sondage (détail avec questions) ──────────────────────────────────────────

class SondageDetailSerializer(SondageListSerializer):
    questions    = QuestionSerializer(many=True, read_only=True, source='question_set')
    statistiques = serializers.SerializerMethodField()

    class Meta(SondageListSerializer.Meta):
        fields = SondageListSerializer.Meta.fields + ['questions', 'statistiques']

    def get_statistiques(self, obj):
        return obj.obtenir_statistiques()


# ── Sondage (création/modification) ──────────────────────────────────────────

class SondageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Sondage
        fields = [
            'titre', 'description', 'est_actif', 'est_prive',
            'mode_passe', 'date_debut', 'date_fin', 'une_seule_reponse',
        ]

    def create(self, validated_data):
        validated_data['createur'] = self.context['request'].user
        return super().create(validated_data)


# ── Réponse ───────────────────────────────────────────────────────────────────

class ReponseDetailSerializer(serializers.ModelSerializer):
    question_texte = serializers.CharField(source='question.texte', read_only=True)
    affichage      = serializers.SerializerMethodField()

    class Meta:
        model  = ReponseDetail
        fields = ['id', 'question', 'question_texte', 'valeur_texte', 'affichage']

    def get_affichage(self, obj):
        return obj.obtenir_affichage()


class ReponseSerializer(serializers.ModelSerializer):
    participant  = serializers.SerializerMethodField()
    details      = ReponseDetailSerializer(many=True, read_only=True, source='reponsedetail_set')

    class Meta:
        model  = Reponse
        fields = ['id', 'sondage', 'participant', 'date_envoi', 'est_complete', 'details']

    def get_participant(self, obj):
        return obj.get_participant_display()


# ── Statistiques par question ─────────────────────────────────────────────────

class StatsQuestionSerializer(serializers.Serializer):
    question_id   = serializers.IntegerField()
    question_texte = serializers.CharField()
    type_question = serializers.CharField()
    total         = serializers.IntegerField()
    donnees       = serializers.ListField()
    moyenne       = serializers.FloatField(required=False)


# ── Utilisateur (profil public) ───────────────────────────────────────────────

class UtilisateurSerializer(serializers.ModelSerializer):
    nb_sondages = serializers.SerializerMethodField()

    class Meta:
        model  = Utilisateur
        fields = ['id', 'username', 'email', 'role', 'date_inscription', 'nb_sondages']
        extra_kwargs = {'email': {'read_only': True}}

    def get_nb_sondages(self, obj):
        return obj.sondages_crees.count()

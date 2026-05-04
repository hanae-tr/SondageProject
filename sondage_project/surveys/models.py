from django.db import models
from django.utils import timezone
import uuid


class ModèleSondage(models.Model):
    """
    Modèle réutilisable de sondage — permet de dupliquer des structures de sondages.
    """
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modèle de sondage"
        verbose_name_plural = "Modèles de sondage"

    def cloner(self):
        """Clone ce modèle et retourne un nouveau Sondage basé dessus"""
        from surveys.models import Sondage
        sondage = Sondage.objects.create(
            titre=f"Copie de {self.nom}",
            description=self.description,
        )
        return sondage

    def __str__(self):
        return self.nom


class Sondage(models.Model):
    """
    Sondage principal — créé par un Utilisateur authentifié.
    Peut être public ou privé, avec ou sans protection par mot de passe.
    """
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    slug = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    createur = models.ForeignKey(
        'accounts.Utilisateur',
        on_delete=models.CASCADE,
        related_name='sondages_crees'
    )
    modele = models.ForeignKey(
        ModèleSondage,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='sondages'
    )

    est_actif = models.BooleanField(default=True)
    est_prive = models.BooleanField(default=False)
    mode_passe = models.CharField(max_length=100, blank=True)

    date_debut = models.DateTimeField(default=timezone.now)
    date_fin = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    # Restrictions de participation
    une_seule_reponse = models.BooleanField(
        default=True,
        help_text="Empêcher un même participant de répondre plusieurs fois"
    )

    class Meta:
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"
        ordering = ['-date_creation']

    def est_ouvert(self):
        """Vérifie si le sondage accepte encore des réponses"""
        maintenant = timezone.now()
        if not self.est_actif:
            return False
        if maintenant < self.date_debut:
            return False
        if self.date_fin and maintenant > self.date_fin:
            return False
        return True

    def obtenir_statistiques(self):
        """Retourne les statistiques globales du sondage"""
        total_reponses = self.reponse_set.filter(est_complete=True).count()
        return {
            'total_reponses': total_reponses,
            'questions': self.question_set.count(),
            'est_ouvert': self.est_ouvert(),
        }

    def dupliquer(self, nouveau_createur):
        """Duplique le sondage avec toutes ses questions et choix"""
        nouveau = Sondage.objects.create(
            titre=f"Copie de {self.titre}",
            description=self.description,
            createur=nouveau_createur,
            est_actif=False,
        )
        for question in self.question_set.all():
            question.dupliquer_vers(nouveau)
        return nouveau

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sondage_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.titre


class Question(models.Model):
    """
    Question appartenant à un sondage.
    Supporte 4 types : choix unique, choix multiple, échelle, texte libre.
    """
    TYPE_CHOIX_UNIQUE = 'choix_unique'
    TYPE_CHOIX_MULTIPLE = 'choix_multiple'
    TYPE_ECHELLE = 'echelle'
    TYPE_TEXTE = 'texte'

    TYPE_CHOICES = [
        (TYPE_CHOIX_UNIQUE, 'Choix unique'),
        (TYPE_CHOIX_MULTIPLE, 'Choix multiple'),
        (TYPE_ECHELLE, 'Échelle (1-5)'),
        (TYPE_TEXTE, 'Texte libre'),
    ]

    sondage = models.ForeignKey(Sondage, on_delete=models.CASCADE)
    texte = models.CharField(max_length=500)
    type_question = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_CHOIX_UNIQUE)
    ordre = models.IntegerField(default=0)
    est_obligatoire = models.BooleanField(default=True)

    # Logique conditionnelle : cette question n'apparaît que si...
    condition_question = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='questions_conditionnelles',
        help_text="Question dont la réponse conditionne l'affichage de cette question"
    )
    condition_choix = models.ForeignKey(
        'Choix',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='+',
        help_text="Le choix qui doit être sélectionné pour afficher cette question"
    )

    class Meta:
        verbose_name = "Question"
        verbose_name_plural = "Questions"
        ordering = ['ordre']

    def obtenir_choix(self):
        return self.choix_set.order_by('ordre')

    def dupliquer_vers(self, nouveau_sondage):
        """Copie la question vers un nouveau sondage"""
        nouvelle_q = Question.objects.create(
            sondage=nouveau_sondage,
            texte=self.texte,
            type_question=self.type_question,
            ordre=self.ordre,
            est_obligatoire=self.est_obligatoire,
        )
        for choix in self.choix_set.all():
            Choix.objects.create(question=nouvelle_q, texte=choix.texte, ordre=choix.ordre)
        return nouvelle_q

    def __str__(self):
        return f"[{self.get_type_question_display()}] {self.texte[:60]}"


class Choix(models.Model):
    """
    Option de réponse pour une question à choix unique ou multiple.
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    texte = models.CharField(max_length=200)
    ordre = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Choix"
        verbose_name_plural = "Choix"
        ordering = ['ordre']

    def compter_reponses(self):
        """Compte combien de fois ce choix a été sélectionné"""
        return self.reponsedetail_set.count()

    def __str__(self):
        return self.texte

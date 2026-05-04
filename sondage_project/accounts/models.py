from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Participant(models.Model):
    """
    Classe abstraite représentant tout acteur pouvant répondre à un sondage.
    Spécialisée en Utilisateur (authentifié) et Anonyme (identifié par IP).
    Implémentation Django : héritage multi-table (une table par sous-classe).
    """
    class Meta:
        verbose_name = "Participant"
        verbose_name_plural = "Participants"

    def __str__(self):
        return f"Participant #{self.pk}"

    def get_type(self):
        """Retourne le type réel du participant"""
        if hasattr(self, 'utilisateur'):
            return 'utilisateur'
        if hasattr(self, 'anonyme'):
            return 'anonyme'
        return 'inconnu'


class Utilisateur(AbstractUser, Participant):
    """
    Utilisateur authentifié — hérite à la fois de AbstractUser (auth Django)
    et de Participant (logique métier sondages).
    Héritage multi-table : table accounts_utilisateur liée à accounts_participant.
    """
    ROLE_CHOICES = [
        ('createur', 'Créateur de sondages'),
        ('participant', 'Participant'),
        ('les_deux', 'Créateur et Participant'),
    ]

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='les_deux')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def est_createur(self):
        return self.role in ['createur', 'les_deux']

    def est_participant(self):
        return self.role in ['participant', 'les_deux']

    def se_connecter(self):
        """Méthode métier — la vraie authentification est gérée par Django"""
        return self.is_authenticated

    def se_deconnecter(self):
        """Méthode métier — utiliser logout() de Django dans la vue"""
        pass

    def modifier_profil(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.save()

    def get_sondages_crees(self):
        return self.sondages_crees.all()

    def get_reponses_donnees(self):
        return self.reponse_set.all()

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Anonyme(Participant):
    """
    Participant non authentifié — identifié par son adresse IP + token de session.
    Héritage multi-table : table accounts_anonyme liée à accounts_participant.
    """
    adresse_ip = models.GenericIPAddressField()
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    date_premiere_reponse = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Participant Anonyme"
        verbose_name_plural = "Participants Anonymes"

    def identifier(self):
        """Retourne un identifiant lisible pour l'anonyme"""
        return f"Anonyme-{str(self.token)[:8]}"

    def __str__(self):
        return self.identifier()

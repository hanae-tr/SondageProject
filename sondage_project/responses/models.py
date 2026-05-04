from django.db import models


class Reponse(models.Model):
    """
    Représente une session de réponse complète à un sondage.
    Liée à un Participant (Utilisateur OU Anonyme) via FK vers Participant.
    Un participant = exactement un enregistrement Participant (jamais NULL).
    """
    sondage = models.ForeignKey('surveys.Sondage', on_delete=models.CASCADE)

    # FK vers Participant (classe mère) — couvre Utilisateur ET Anonyme
    participant = models.ForeignKey(
        'accounts.Participant',
        on_delete=models.CASCADE,
        help_text="Participant identifié ou anonyme ayant soumis cette réponse"
    )

    date_envoi = models.DateTimeField(auto_now_add=True)
    est_complete = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        ordering = ['-date_envoi']

    def est_complete_check(self):
        """Vérifie que toutes les questions obligatoires ont une réponse"""
        questions_obligatoires = self.sondage.question_set.filter(est_obligatoire=True)
        questions_repondues = self.reponsedetail_set.values_list('question_id', flat=True)
        return all(q.id in questions_repondues for q in questions_obligatoires)

    def get_participant_display(self):
        """Retourne le nom d'affichage du participant"""
        participant = self.participant
        if hasattr(participant, 'utilisateur'):
            return str(participant.utilisateur)
        if hasattr(participant, 'anonyme'):
            return participant.anonyme.identifier()
        return "Inconnu"

    def __str__(self):
        return f"Réponse de {self.get_participant_display()} au sondage '{self.sondage}'"


class ReponseDetail(models.Model):
    """
    Détail d'une réponse pour une question spécifique.
    Contient la valeur texte et/ou le(s) choix sélectionné(s).
    """
    reponse = models.ForeignKey(Reponse, on_delete=models.CASCADE)
    question = models.ForeignKey('surveys.Question', on_delete=models.CASCADE)
    valeur_texte = models.TextField(blank=True)
    choix_selectionnes = models.ManyToManyField(
        'surveys.Choix',
        blank=True,
        help_text="Choix sélectionnés (pour choix unique ou multiple)"
    )

    class Meta:
        verbose_name = "Détail de réponse"
        verbose_name_plural = "Détails de réponses"
        unique_together = [('reponse', 'question')]

    def obtenir_affichage(self):
        """Retourne une représentation lisible de la réponse"""
        q_type = self.question.type_question
        if q_type in ['choix_unique', 'choix_multiple']:
            choix = self.choix_selectionnes.all()
            return ', '.join([c.texte for c in choix]) if choix else '—'
        elif q_type == 'echelle':
            return f"Note : {self.valeur_texte}/5" if self.valeur_texte else '—'
        else:
            return self.valeur_texte or '—'

    def __str__(self):
        return f"Réponse à '{self.question.texte[:40]}' : {self.obtenir_affichage()}"

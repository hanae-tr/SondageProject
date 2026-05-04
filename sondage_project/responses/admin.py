from django.contrib import admin
from .models import Reponse, ReponseDetail


class ReponseDetailInline(admin.TabularInline):
    model   = ReponseDetail
    extra   = 0
    readonly_fields = ['question', 'valeur_texte', 'obtenir_affichage_display']

    @admin.display(description='Affichage')
    def obtenir_affichage_display(self, obj):
        return obj.obtenir_affichage()


@admin.register(Reponse)
class ReponseAdmin(admin.ModelAdmin):
    list_display   = ['sondage', 'get_participant_display', 'date_envoi', 'est_complete']
    list_filter    = ['est_complete', 'date_envoi', 'sondage']
    search_fields  = ['sondage__titre']
    readonly_fields = ['sondage', 'participant', 'date_envoi']
    inlines        = [ReponseDetailInline]

    @admin.display(description='Participant')
    def get_participant_display(self, obj):
        return obj.get_participant_display()


@admin.register(ReponseDetail)
class ReponseDetailAdmin(admin.ModelAdmin):
    list_display  = ['reponse', 'question', 'obtenir_affichage']
    search_fields = ['question__texte']

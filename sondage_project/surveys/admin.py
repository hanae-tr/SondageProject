from django.contrib import admin
from .models import ModèleSondage, Sondage, Question, Choix


class QuestionInline(admin.TabularInline):
    model  = Question
    extra  = 1
    fields = ['texte', 'type_question', 'ordre', 'est_obligatoire']


class ChoixInline(admin.TabularInline):
    model  = Choix
    extra  = 2
    fields = ['texte', 'ordre']


@admin.register(Sondage)
class SondageAdmin(admin.ModelAdmin):
    list_display   = ['titre', 'createur', 'est_actif', 'est_prive', 'est_ouvert', 'date_creation', 'nb_reponses']
    list_filter    = ['est_actif', 'est_prive', 'date_creation']
    search_fields  = ['titre', 'createur__username']
    readonly_fields = ['slug', 'date_creation', 'date_modification']
    inlines        = [QuestionInline]

    @admin.display(boolean=True, description='Ouvert ?')
    def est_ouvert(self, obj):
        return obj.est_ouvert()

    @admin.display(description='Réponses')
    def nb_reponses(self, obj):
        return obj.reponse_set.filter(est_complete=True).count()


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display  = ['texte', 'sondage', 'type_question', 'ordre', 'est_obligatoire']
    list_filter   = ['type_question', 'est_obligatoire']
    search_fields = ['texte', 'sondage__titre']
    inlines       = [ChoixInline]


@admin.register(Choix)
class ChoixAdmin(admin.ModelAdmin):
    list_display  = ['texte', 'question', 'ordre', 'compter_reponses']
    search_fields = ['texte']

    @admin.display(description='Nb réponses')
    def compter_reponses(self, obj):
        return obj.compter_reponses()


@admin.register(ModèleSondage)
class ModèleSondageAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'description']
    search_fields = ['nom']

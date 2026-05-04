from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_sondages_publics, name='liste_publique'),
    path('<uuid:slug>/', views.detail_sondage, name='sondage_detail'),
    path('creer/', views.creer_sondage, name='creer_sondage'),
    path('<uuid:slug>/modifier/', views.modifier_sondage, name='modifier_sondage'),
    path('<uuid:slug>/supprimer/', views.supprimer_sondage, name='supprimer_sondage'),
    path('<uuid:slug>/dupliquer/', views.dupliquer_sondage, name='dupliquer_sondage'),
    path('<uuid:slug>/questions/', views.editer_questions, name='editer_questions'),
    path('<uuid:slug>/questions/ajouter/', views.ajouter_question, name='ajouter_question'),
    path('questions/<int:question_id>/supprimer/', views.supprimer_question, name='supprimer_question'),
]

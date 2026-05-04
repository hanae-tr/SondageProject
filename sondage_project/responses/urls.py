from django.urls import path
from . import views

urlpatterns = [
    path('<uuid:slug>/repondre/', views.repondre_sondage, name='repondre_sondage'),
    path('<uuid:slug>/merci/', views.remerciement, name='remerciement'),
    path('<uuid:slug>/resultats/', views.resultats_sondage, name='resultats_sondage'),
    path('<uuid:slug>/export/csv/', views.export_csv, name='export_csv'),
    path('<uuid:slug>/export/excel/', views.export_excel, name='export_excel'),
    path('api/question/<int:question_id>/stats/', views.api_stats_question, name='api_stats_question'),
]

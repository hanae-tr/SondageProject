from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.api_status, name='api_status'),

  
    path('sondages/',                      views.SondageListCreateView.as_view(), name='api_sondages'),
    path('sondages/mes-sondages/',         views.MesSondagesView.as_view(),       name='api_mes_sondages'),
    path('sondages/<uuid:slug>/',          views.SondageDetailView.as_view(),     name='api_sondage_detail'),

   
    path('sondages/<uuid:slug>/questions/', views.QuestionListCreateView.as_view(), name='api_questions'),

 
    path('sondages/<uuid:slug>/stats/',    views.StatsView.as_view(),             name='api_stats'),
    path('sondages/<uuid:slug>/reponses/', views.ReponseListView.as_view(),       name='api_reponses'),

  
    path('questions/<int:pk>/',            views.QuestionDetailView.as_view(),    name='api_question_detail'),
    path('questions/<int:pk>/stats/',      views.StatsQuestionView.as_view(),     name='api_question_stats'),

    
    path('profil/',                        views.ProfilView.as_view(),            name='api_profil'),
]

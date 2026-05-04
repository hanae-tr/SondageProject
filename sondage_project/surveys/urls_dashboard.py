from django.urls import path
from surveys.views import dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
]

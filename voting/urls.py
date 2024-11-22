# voting/urls.py

from django.urls import path
from . import views

app_name = 'voting'

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('election/<int:election_id>/vote/', views.vote, name='vote'),
    path('election/<int:election_id>/results/', views.results, name='results'),
    path('election/create/', views.create_election, name='create_election'),
    path('election/<int:election_id>/manage/', views.manage_election, name='manage_election'),
    path('register/', views.register, name='register'),  # Маршрут регистрации
]

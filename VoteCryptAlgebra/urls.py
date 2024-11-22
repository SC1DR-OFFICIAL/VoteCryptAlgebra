# VoteCryptAlgebra/urls.py

from django.contrib import admin
from django.urls import path, include  # Убедитесь, что include импортирован

urlpatterns = [
    path('admin/', admin.site.urls),
    path('voting/', include('voting.urls', namespace='voting')),
]

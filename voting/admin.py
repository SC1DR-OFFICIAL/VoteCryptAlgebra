# voting/admin.py

from django.contrib import admin
from .models import Election, Candidate, Vote

@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    search_fields = ('name',)

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'election')
    search_fields = ('name',)
    list_filter = ('election',)

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('election', 'voter', 'candidate')
    search_fields = ('voter__username', 'candidate__name')
    list_filter = ('election', 'candidate')

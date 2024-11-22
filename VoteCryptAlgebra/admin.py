from django.contrib import admin
from .models import Election, Candidate, Vote


class CandidateInline(admin.TabularInline):
    model = Candidate
    extra = 1
    verbose_name = "Кандидат"
    verbose_name_plural = "Кандидаты"


class ElectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    inlines = [CandidateInline]


class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate', 'election', 'encrypted_vote')
    list_filter = ('election', 'candidate')
    search_fields = ('voter__username', 'candidate__name')


admin.site.register(Election, ElectionAdmin)
admin.site.register(Vote, VoteAdmin)

# voting/forms.py

from django import forms
from .models import Election, Candidate


class VoteForm(forms.Form):
    election = forms.ModelChoiceField(
        queryset=Election.objects.all(),
        widget=forms.HiddenInput(),
        required=True
    )
    candidate = forms.ModelChoiceField(
        queryset=Candidate.objects.none(),
        widget=forms.RadioSelect,
        required=True,
        label="Выберите кандидата"
    )

    def __init__(self, *args, **kwargs):
        election = kwargs.pop('election', None)
        super(VoteForm, self).__init__(*args, **kwargs)
        if election:
            self.fields['candidate'].queryset = election.candidates.all()
            self.fields['election'].initial = election


class ElectionForm(forms.ModelForm):
    class Meta:
        model = Election
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'description']

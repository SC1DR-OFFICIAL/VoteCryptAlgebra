# voting/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Election, Candidate, Vote
from .forms import VoteForm, ElectionForm, CandidateForm
from .crypto import HomomorphicEncryption
from django.utils import timezone

# Инициализация модуля гомоморфного шифрования
HE = HomomorphicEncryption()

def is_admin(user):
    """Функция проверки, является ли пользователь администратором."""
    return user.is_staff

@login_required
def vote(request, election_id):
    """Представление для голосования."""
    election = get_object_or_404(Election, id=election_id)

    # Проверка, начались ли выборы
    if timezone.now() < election.start_date:
        return render(request, 'voting/voting_not_started.html', {'election': election})

    # Проверка, завершились ли выборы
    if timezone.now() > election.end_date:
        return render(request, 'voting/voting_ended.html', {'election': election})

    if request.method == 'POST':
        form = VoteForm(request.POST, election=election)
        if form.is_valid():
            candidate = form.cleaned_data['candidate']
            # Проверка, голосовал ли пользователь ранее
            if Vote.objects.filter(election=election, voter=request.user).exists():
                return render(request, 'voting/already_voted.html', {'election': election})
            # Шифрование голоса
            encrypted_vote = HE.encrypt_vote(candidate.id)
            # Сохранение зашифрованного голоса
            Vote.objects.create(
                election=election,
                voter=request.user,
                candidate=candidate,
                encrypted_vote=encrypted_vote
            )
            return render(request, 'voting/vote_success.html', {'election': election})
    else:
        form = VoteForm(election=election)

    return render(request, 'voting/vote.html', {'form': form, 'election': election})

@login_required
@user_passes_test(is_admin)
def create_election(request):
    """Представление для создания новых выборов (доступно только администраторам)."""
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save()
            return redirect('voting:manage_election', election_id=election.id)
    else:
        form = ElectionForm()
    return render(request, 'voting/create_election.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def manage_election(request, election_id):
    """Представление для управления выборами и добавления кандидатов (доступно только администраторам)."""
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.all()

    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.election = election
            candidate.save()
            return redirect('voting:manage_election', election_id=election.id)
    else:
        form = CandidateForm()

    return render(request, 'voting/manage_election.html', {
        'election': election,
        'candidates': candidates,
        'form': form
    })

@login_required
@user_passes_test(is_admin)
def results(request, election_id):
    """Представление для отображения результатов голосования (доступно только администраторам)."""
    election = get_object_or_404(Election, id=election_id)

    # Проверка, что голосование завершилось
    if timezone.now() < election.end_date:
        return render(request, 'voting/results_not_available.html', {'election': election})

    # Получение всех зашифрованных голосов
    votes = Vote.objects.filter(election=election)

    # Создание словаря для хранения количества голосов по каждому кандидату
    decrypted_results = {}
    for candidate in election.candidates.all():
        decrypted_sum = votes.filter(candidate=candidate).count()
        decrypted_results[candidate.name] = decrypted_sum

    return render(request, 'voting/results.html', {'election': election, 'total_votes': decrypted_results})

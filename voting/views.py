# voting/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .models import Election, Candidate, Vote
from .forms import VoteForm, ElectionForm, CandidateForm
from .crypto import HomomorphicEncryption
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm  # Импорт формы регистрации
import logging

logger = logging.getLogger(__name__)


def is_admin(user):
    """Проверка, является ли пользователь администратором."""
    return user.is_staff


@login_required
def home(request):
    """Главная страница с отображением всех голосований."""
    elections = Election.objects.all().order_by('-end_date')  # Все голосования, сортировка по дате завершения
    return render(request, 'voting/home.html', {'elections': elections})


@login_required
def vote(request, election_id):
    """Представление для голосования."""
    election = get_object_or_404(Election, id=election_id)

    # Проверка статуса голосования
    if timezone.now() < election.start_date:
        messages.error(request, 'Голосование ещё не началось.')
        return redirect('voting:home')

    if election.has_ended():
        messages.error(request, 'Голосование уже завершено. Посмотрите результаты.')
        return redirect('voting:home')

    if Vote.objects.filter(election=election, voter=request.user).exists():
        messages.warning(request, 'Вы уже голосовали в этом голосовании.')
        return redirect('voting:home')

    if request.method == 'POST':
        form = VoteForm(request.POST, election=election)
        if form.is_valid():
            candidate = form.cleaned_data['candidate']
            HE = HomomorphicEncryption()  # Инициализация внутри функции
            try:
                encrypted_vote = HE.encrypt_vote(candidate.id)
                serialized_vote = encrypted_vote.serialize()
            except Exception as e:
                logger.error(f'Ошибка при шифровании голоса: {e}')
                messages.error(request, f'Ошибка при шифровании голоса: {e}')
                return redirect('voting:vote', election_id=election.id)

            # Сохранение зашифрованного голоса
            Vote.objects.create(
                election=election,
                voter=request.user,
                candidate=candidate,
                encrypted_vote=serialized_vote
            )
            messages.success(request, 'Ваш голос успешно отдан!')
            return redirect('voting:home')
        else:
            messages.error(request, 'Произошла ошибка при отправке формы. Пожалуйста, попробуйте снова.')
    else:
        form = VoteForm(election=election)

    return render(request, 'voting/vote.html', {'form': form, 'election': election})


@login_required
@user_passes_test(is_admin)
def create_election(request):
    """Создание нового голосования (только для администраторов)."""
    if request.method == 'POST':
        form = ElectionForm(request.POST)
        if form.is_valid():
            election = form.save()
            messages.success(request, f'Голосование "{election.name}" успешно создано.')
            return redirect('voting:manage_election', election_id=election.id)
        else:
            messages.error(request, 'Произошла ошибка при создании голосования. Пожалуйста, попробуйте снова.')
    else:
        form = ElectionForm()
    return render(request, 'voting/create_election.html', {'form': form})


@login_required
@user_passes_test(is_admin)
def manage_election(request, election_id):
    """Управление голосованием и добавление кандидатов (только для администраторов)."""
    election = get_object_or_404(Election, id=election_id)
    candidates = election.candidates.all()

    if request.method == 'POST':
        form = CandidateForm(request.POST)
        if form.is_valid():
            candidate = form.save(commit=False)
            candidate.election = election
            candidate.save()
            messages.success(request, f'Кандидат "{candidate.name}" успешно добавлен.')
            return redirect('voting:manage_election', election_id=election.id)
        else:
            messages.error(request, 'Произошла ошибка при добавлении кандидата. Пожалуйста, попробуйте снова.')
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
    """Отображение результатов голосования (только для администраторов)."""
    election = get_object_or_404(Election, id=election_id)

    if not election.has_ended():
        messages.error(request, 'Голосование ещё не завершено.')
        return redirect('voting:home')

    votes = Vote.objects.filter(election=election)
    HE = HomomorphicEncryption()

    decrypted_results = {}
    for candidate in election.candidates.all():
        candidate_votes = votes.filter(candidate=candidate)
        total_votes = 0
        for vote in candidate_votes:
            try:
                decrypted_vote = HE.decrypt_vote(vote.encrypted_vote)
                total_votes += decrypted_vote
            except Exception as e:
                logger.error(f'Ошибка при дешифровании голоса для кандидата {candidate.name}: {e}')
                messages.error(request, f'Ошибка при дешифровании голоса: {e}')
        decrypted_results[candidate.name] = total_votes

    return render(request, 'voting/results.html', {'election': election, 'total_votes': decrypted_results})


def register(request):
    """Регистрация нового пользователя."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Вы успешно зарегистрировались и вошли в систему.')
                return redirect('voting:home')
            else:
                messages.error(request, 'Не удалось войти в систему после регистрации.')
        else:
            messages.error(request, 'Произошла ошибка при регистрации. Пожалуйста, попробуйте снова.')
    else:
        form = UserCreationForm()
    return render(request, 'voting/register.html', {'form': form})

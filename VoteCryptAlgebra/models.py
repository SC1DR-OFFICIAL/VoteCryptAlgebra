from django.db import models
from django.contrib.auth.models import User


class Election(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название выборов")
    description = models.TextField(verbose_name="Описание выборов")
    start_date = models.DateTimeField(verbose_name="Дата начала")
    end_date = models.DateTimeField(verbose_name="Дата окончания")

    def __str__(self):
        return self.name


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, related_name='candidates', verbose_name="Выборы")
    name = models.CharField(max_length=255, verbose_name="Имя кандидата")
    description = models.TextField(blank=True, null=True, verbose_name="Описание кандидата")

    def __str__(self):
        return self.name


class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE, verbose_name="Выборы")
    voter = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Избиратель")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, verbose_name="Кандидат")
    encrypted_vote = models.BinaryField(verbose_name="Зашифрованный голос")

    def __str__(self):
        return f"Голос {self.voter.username} за {self.candidate.name} на выборах {self.election.name}"

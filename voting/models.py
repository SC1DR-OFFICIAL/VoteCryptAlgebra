# voting/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Election(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    def __str__(self):
        return self.name

    def is_active(self):
        """Проверяет, активно ли голосование."""
        now = timezone.now()
        return self.start_date <= now <= self.end_date

    def has_ended(self):
        """Проверяет, завершилось ли голосование."""
        now = timezone.now()
        return now > self.end_date


class Candidate(models.Model):
    election = models.ForeignKey(Election, related_name='candidates', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    election = models.ForeignKey(Election, related_name='votes', on_delete=models.CASCADE)
    voter = models.ForeignKey(User, related_name='votes', on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, related_name='votes', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.voter} voted for {self.candidate} in {self.election}"


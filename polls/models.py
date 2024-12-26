import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/')
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='question_images/', blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)

    def was_published_recently(self):
        return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

    def is_expired(self):
        if self.expiration_date:
            return timezone.now() > self.expiration_date
        return False

    def __str__(self):
        return self.question_text


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    voters = models.ManyToManyField(User, related_name='voted_choices')

    def __str__(self):
        return self.choice_text

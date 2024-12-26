from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Question, Choice, UserProfile
from django.template import loader
from django.urls import reverse
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, QuestionForm, ChoiceForm

#Классы для отображения списка вопросов, делатей вопроса и результатов
class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        return Question.objects.filter(Q(expiration_date__gt=timezone.now()) | Q(expiration_date__isnull=True)).order_by('-pub_date')

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'

class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# Представление для голосования
@login_required
def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': 'вы не сделали выбор'
        })
    else:
        if request.user in selected_choice.voters.all():
            return render(request, 'polls/detail.html', {
                'question': question,
                'error_message': 'вы уже голосовали за этот вопрос'
            })
        selected_choice.votes += 1
        selected_choice.voters.add(request.user)
        selected_choice.save()
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

# Представление для регистрации пользователя
def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(user=user)  # Создаем профиль для пользователя
            login(request, user)  # Автоматическая авторизация после регистрации
            return redirect('polls:index')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'polls/register.html', {'user_form': user_form})

# Представление для авторизации пользователя
def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('polls:index')
    else:
        form = UserLoginForm()
    return render(request, 'polls/login.html', {'form': form})

# Предстваление для редактирования профиля пользователя
@login_required
def edit_profile(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('polls:index')
    else:
        profile_form = UserProfileForm(instance=user_profile)

    return render(request, 'polls/edit_profile.html', {'profile_form': profile_form})

# Представление для удаления профиля пользователя
def delete_profile(request):
    user = request.user
    user.delete()
    return redirect('polls:index')

# Представление для выхода пользователя
def user_logout(request):
    logout(request)
    return redirect('polls:index')


@login_required
def create_question(request):
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, request.FILES)
        choice_forms = [ChoiceForm(request.POST, prefix=str(x)) for x in range(0, 3)]
        if question_form.is_valid() and all(cf.is_valid() for cf in choice_forms):
            question = question_form.save(commit=False)
            question.user = request.user
            question.pub_date = timezone.now()
            question.save()
            for cf in choice_forms:
                choice = cf.save(commit=False)
                choice.question = question
                choice.save()
            return redirect('polls:index')
    else:
        question_form = QuestionForm()
        choice_forms = [ChoiceForm(prefix=str(x)) for x in range(0, 3)]

    return render(request, 'polls/create_question.html', {
        'question_form': question_form,
        'choice_forms': choice_forms
    })

import json
import logging
from django.views import View
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404

from dtb.settings import DEBUG
from tgbot.dispatcher import process_telegram_event, TELEGRAM_BOT_USERNAME

from .forms import CustomAuthForm
from .models import Profile, User, Experience, Vacancy, EmployeeValues

logger = logging.getLogger(__name__)


def index(request):
    return JsonResponse({"error": "sup hacker"})


class TelegramBotWebhookView(View):
    # WARNING: if fail - Telegram webhook will be delivered again.
    # Can be fixed with async celery task execution
    def post(self, request, *args, **kwargs):
        if DEBUG:
            process_telegram_event(json.loads(request.body))
        else:
            # Process Telegram event in Celery worker (async)
            # Don't forget to run it and & Redis (message broker for Celery)!
            # Read Procfile for details
            # You can run all of these services via docker-compose.yml
            process_telegram_event.delay(json.loads(request.body))

        # TODO: there is a great trick to send action in webhook response
        # e.g. remove buttons, typing event
        return JsonResponse({"ok": "POST request processed"})

    def get(self, request, *args, **kwargs):  # for debug
        return JsonResponse({"ok": "Get request received! But nothing done"})


class Cabinet(TemplateView):
    template_name = 'tgbot/cabinet.html'

    def get(self, request):
        return render(request, 'tgbot/cabinet.html', {'context': self.get_context_data()})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profiles'] = Profile.objects.all()
        return context


class SignInView(View):
    def get(self, request):
        return render(request, 'tgbot/signin.html', {'form':CustomAuthForm()})

    def post(self, request):
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'tgbot/signin.html', {'form':CustomAuthForm(), 'error':'Account didn\'t found!'})
        else:
            login(request, user)
            return redirect('cabinet')


class ProfilelListView(ListView):
    template_name = 'tgbot/profile_list.html'
    queryset = Profile.objects.all()
    context_object_name = 'profiles'
    model = Profile
    paginate_by = 12

    def get_ordering(self):
        ordering = self.request.GET.get('orderby')
        print(ordering)
        return ordering


class ProfileDetailView(DetailView):
    template_name = 'tgbot/profile_detail.html'
    context_object_name = 'profile'
    model = Profile
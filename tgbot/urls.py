from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [  
    # Just empty index for check
    path('', views.index, name="index"),

    # BOT CABINET
    path('cabinet/', views.Cabinet.as_view(), name='cabinet'),
    path('profile_list/', views.ProfilelListView.as_view(), name='profile_list'),
    path('profiles/<int:pk>/', views.ProfileDetailView.as_view(),  name='profile_detail'),

    # AUTH
    path('signin/', views.SignInView.as_view(), name='signin'),


    # TODO: make webhook more secure
    path('super_secter_webhook/', csrf_exempt(views.TelegramBotWebhookView.as_view())),
]
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt


from . import views


app_name = 'tgbot'

urlpatterns = [  
    # Just empty index for check
    path('', views.index, name="index"),

    # BOT CABINET
    path('cabinet/', views.Cabinet.as_view(), name='cabinet'),
    path('profile_list/', views.ProfilelListView.as_view(), name='profile_list'),
    path('profiles/<int:pk>/', views.ProfileDetailView.as_view(),  name='profile_detail'),
    path('profiles/action/<int:pk>/', views.ProfileActionView.as_view(), name='profile_action'),
    path('profiles/<int:pk>/comment/add', views.ProfileCommentAdd.as_view(), name='profile_add_comment'),

    path('emp_values_list/', views.EmployeeValuesListView.as_view(), name='employee_values_list'),
    path('emp_values/create', views.EmployeeValuesCreateView.as_view(), name='employee_values_create'),
    path('emp_values/<int:pk>/update', views.EmployeeValuesUpdateView.as_view(), name='employee_values_update'),

    path('vacancy_list/', views.VacancyListView.as_view(), name='vacancy_list'),
    path('vacancy/create', views.VacancyCreateView.as_view(), name='vacancy_create'),
    path('vacancy/<int:pk>/update', views.VacancyUpdateView.as_view(), name='vacancy_update'),
    path('vacancy/<int:pk>/', views.VacancyDetailView.as_view(),  name='vacancy_detail'),

    path('stage/<int:pk>/comment/add', views.StageCommentAdd.as_view(), name='stage_add_comment'),

    # Profs export
    path('profiles/export', views.export_profiles_to_xlsx, name='profile_export'),

    # AUTH
    path('signin/', views.SignInView.as_view(), name='signin'),
    path('logout/', views.LogoutView.as_view(), name='logout'),


    # TODO: make webhook more secure
    path('super_secter_webhook/', csrf_exempt(views.TelegramBotWebhookView.as_view())),
]


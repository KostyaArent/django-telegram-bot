from __future__ import annotations

from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
from django.urls import reverse
from django.contrib.auth.models import User as StUser

from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

from dtb.settings import DEBUG
from tgbot.handlers.utils.info import extract_user_data_from_update
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(primary_key=True)  # telegram_id
    username = models.CharField(max_length=32, **nb)
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, **nb)
    language_code = models.CharField(max_length=8, help_text="Telegram client's lang", **nb)
    deep_link = models.CharField(max_length=64, **nb)
    is_blocked_bot = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()

    def __str__(self):
        return f'@{self.username}' if self.username is not None else f'{self.user_id}'

    @classmethod
    def get_user_and_created(cls, update: Update, context: CallbackContext) -> Tuple[User, bool]:
        """ python-telegram-bot's Update, Context --> User instance """
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)

        if created:
            # Save deep_link to User model
            if context is not None and context.args is not None and len(context.args) > 0:
                payload = context.args[0]
                if str(payload).strip() != str(data["user_id"]).strip():  # you can't invite yourself
                    u.deep_link = payload
                    u.save()

        return u, created

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext) -> User:
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]) -> Optional[User]:
        """ Search user in DB, return User or None if not found """
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self) -> QuerySet[User]:
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f'@{self.username}'
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"


class Location(CreateTracker):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    latitude = models.FloatField()
    longitude = models.FloatField()
    objects = GetOrNoneManager()

    def __str__(self):
        return f"user: {self.user}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"

    def save(self, *args, **kwargs):
        super(Location, self).save(*args, **kwargs)
        # Parse location with arcgis
        from arcgis.tasks import save_data_from_arcgis
        if DEBUG:
            save_data_from_arcgis(latitude=self.latitude, longitude=self.longitude, location_id=self.pk)
        else:
            save_data_from_arcgis.delay(latitude=self.latitude, longitude=self.longitude, location_id=self.pk)


class Vacancy(models.Model):
    title = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Название',
    )
    is_active = models.BooleanField(default=False, verbose_name='Активна')
    description = models.TextField(default="Нет описания", verbose_name='Описание')

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

    def get_absolute_url(self):
        return reverse('tgbot:vacancy_detail', kwargs={'pk':self.pk})

    def __str__(self):
        return self.title


class Experience(models.Model):
    CHOICES = (
        ('1', 'Меньше 6 мес'),
        ('2', 'От 6 мес до 1 года'),
        ('3', 'От 1 года до 3 лет'),
        ('4', 'Больше 5 лет'),
    )
    vacancy = models.ForeignKey(
        Vacancy,
        verbose_name='Должность',
        on_delete=models.CASCADE,
        )
    standing = models.CharField(max_length=300, choices = CHOICES, null=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True
    )
    def __str__(self):
        return self.vacancy.title

    class Meta:
        verbose_name = 'Опыт'
        verbose_name_plural = 'Опыт'


class EmployeeValues(models.Model):
    title = models.TextField(max_length=200, verbose_name='Название')
    is_base = models.BooleanField(default=False, verbose_name='Выводится всем')
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Ценность'
        verbose_name_plural = 'Ценности'


class ProfileStatuses(models.Model):
    title = models.CharField(
        verbose_name='Название этапа',
        max_length=20,
        unique=True
        )
    description = models.TextField(
        verbose_name='Описание этапа',
        blank=True,
        null=True
    )
    next_statuses = models.ManyToManyField(
        'self',
        null=True,
        blank=True,
        symmetrical=False,
        verbose_name='Следующие этапы'
    )
    priority = models.IntegerField(
        verbose_name='Приоритет',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Этап'
        verbose_name_plural = 'Этапы'

    def __str__(self):
        return f'{self.pk} {self.title}'


class Profile(models.Model):
    STATUSES = (
        ('0', 'Не обработано'),
        ('1', 'Недозвон'),
        ('2', 'Первичное собеседование'),
        ('3', 'Пробный день'),
        ('4', 'Итоговое собеседование'),
        ('5', 'Оформление'),
        ('6', 'Самоотказ'),
        ('7', 'Отказ от рекрутера'),
        ('8', 'Резерв'),
        ('9', 'Незавершенная'),
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='Пользователь'
    )
    name_family = models.TextField(
        verbose_name='Имя Фамилия',
        blank=True,
    )
    phone = models.CharField(
        max_length=13,
        verbose_name='Номер телефона',
        blank=True,
    )
    working = models.TextField(
        verbose_name='Статус занятости',
        blank=True,
    )
    salary_await = models.TextField(
        verbose_name='Зарплатные ожидания',
        blank=True,
    )
    status = models.CharField(
        verbose_name='Статус анкеты',
        blank=True, 
        null=True,
        max_length=300, 
        choices = STATUSES,
        default='9'
    )
    hr_comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True
    )
    stage = models.ForeignKey(
        ProfileStatuses,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Тру статус'
    )

    class Meta:
        verbose_name = 'Профайл'
        verbose_name_plural = 'Профайлы'
        ordering = ['status']

    def get_absolute_url(self):
        return reverse('tgbot:profile_detail', kwargs={'pk':self.pk})

    def __str__(self):
        return str(self.user.username)

    @property
    def emp_values(self):
        vals = [ith.title for ith in EmployeeValues.objects.filter(users__pk=self.user.user_id)]
        return ", \n".join(vals)

    @property
    def exp(self):
        """Returned html list"""
        exps = Experience.objects.filter(user__pk=self.user.user_id)
        experience = "".join(
            [f'<li>{exp.vacancy}: {[ith[1] for ith in Experience.CHOICES if ith[0]==exp.standing][0]}\
            </li>' if exp.standing is not None else f'<li>{exp.vacancy}: Без опыта</li>' for exp in exps]
            ) if exps is not None else "Без опыта"
        return experience

    @property
    def get_exp_query(self):
        exps = Experience.objects.filter(user__pk=self.user.user_id)
        return exps

    def change_status(self, status, current_stage=None, user=None):
        #print(current_stage.performer)
        print(user)
        if current_stage and user:
            current_stage.performer = user
            current_stage.save()
            print(current_stage.performer)
            print('User set on current_stage')
        stage = ProfileStatuses.objects.filter(pk=int(status)).first()
        self.stage = stage
        print('self status chanched')
        self.save()
        print('self status saved')
        prof_hist, created = ProfileStatusHistory.objects.get_or_create(
            profile=self, 
            stage=stage
            )
        if not created:
            prof_hist.return_date = datetime.now()
            prof_hist.save()

        print('Func status is OK')

    def get_statuses_history_set(self):
        history_set = ProfileStatusHistory.objects.filter(profile=self).order_by('date')
        return history_set

    def get_current_stage(self):
        current_stage = ProfileStatusHistory.objects.get(stage=self.stage)#.order_by('-date')[:1][0]
        return current_stage


class ProfileStatusHistory(models.Model):

    profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE,
        verbose_name='Профайл'
    )
    status = models.CharField(
        verbose_name='Статус анкеты',
        blank=True, 
        null=True,
        max_length=300, 
        choices = Profile.STATUSES
    )
    comment = models.TextField(
        verbose_name='Комментарий',
        blank=True,
        null=True
    )
    date = models.DateTimeField(
        verbose_name='Дата',
        auto_now_add=True, 
        blank=True
    )
    return_date = models.DateTimeField(
        verbose_name='Дата возврата',
        blank=True,
        null=True
    )
    stage = models.ForeignKey(
        ProfileStatuses,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Тру статус'
    )
    performer = models.ForeignKey(
        StUser,
        models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Исполнитель'
        )

    def __str__(self):
        return f'{self.stage} {self.profile} {self.performer} {self.date}'

    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'Истории'
        ordering = ['profile', 'date']



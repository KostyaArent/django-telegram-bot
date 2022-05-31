from __future__ import annotations

from typing import Union, Optional, Tuple

from django.db import models
from django.db.models import QuerySet, Manager
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
        verbose_name='Vacancy',
    )
    is_active = models.BooleanField(default=False)
    description = models.TextField(default="Нет описания")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"

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
    title = models.TextField(max_length=200)
    is_base = models.BooleanField(default=False)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Ценность'
        verbose_name_plural = 'Ценности'



class Profile(models.Model):
    STATUCES = (
        ('0', 'Новая'),
        ('1', 'В работе'),
        ('2', 'На собеседовании'),
        ('3', 'В архиве'),
        ('9', 'Незавершенная'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
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
    experience = models.ForeignKey(
        Experience,
        verbose_name='Опыт',
        on_delete=models.PROTECT,
        null = True,
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
        choices = STATUCES,
        default='9'
    )

    def __str__(self):
        return self.user.username

    @property
    def emp_values(self):
        vals = [ith.title for ith in EmployeeValues.objects.filter(users__pk=self.user.user_id)]
        return ", \n".join(vals)

    @property
    def exp(self):
        """Returned html list"""
        exps = Experience.objects.filter(user__pk=self.user.user_id)
        experience = "".join([f'<li>{exp.vacancy}: {[ith[1] for ith in Experience.CHOICES if ith[0]==exp.standing][0]}</li>' if exp.standing is not None else f'<li>{exp.vacancy}: Без опыта</li>' for exp in exps]) if exps is not None else "Без опыта"
        print(experience)
        return experience

    class Meta:
        verbose_name = 'Профайл'
        verbose_name_plural = 'Профайлы'
        ordering = ['status']
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.db import models

from map.models import Region, District


class Organization(models.Model):
    name = models.CharField(max_length=200, verbose_name='Наименование')
    district = models.ForeignKey(District,
                                 null=True,
                                 blank=True,
                                 verbose_name='Округ')
    region = models.ForeignKey(Region,
                               null=True,
                               blank=True,
                               verbose_name='Район')

    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'

    def __str__(self):
        return self.name


class RatingsUserManager(BaseUserManager):
    def create_blank_user(self, email):
        if not email:
            raise ValueError('У пользователя должен быть email адрес')
        user = self.model(
            email=self.normalize_email(email),
        )
        return user

    def create_user(self, email):
        user = self.create_blank_user(email)
        user.set_password(None)
        user.save(using=self._db, force_insert=True)
        return user

    def create_superuser(self, email, password):
        user = self.create_blank_user(email)
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class RatingsUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )
    # TODO after email backend
    # is_email_confirmed = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=False,
    #                                 verbose_name='Активный')
    is_active = models.BooleanField(default=True,
                                    verbose_name='Активный')
    is_admin = models.BooleanField(default=False,
                                   verbose_name='Админ')

    objects = RatingsUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Employee(models.Model):
    user = models.OneToOneField(RatingsUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100,
                                  verbose_name='Имя')
    last_name = models.CharField(max_length=100,
                                 verbose_name='Фамилия')
    patronymic = models.CharField(max_length=100,
                                  null=True,
                                  blank=True,
                                  verbose_name='Отчество')
    organization = models.ForeignKey(Organization,
                                     null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '{} | {}'.format(self.short_name, self.user.email)

    @property
    def full_name(self):
        return '{} {} {}'.format(
            self.last_name,
            self.first_name,
            self.patronymic if self.patronymic else ''
        )

    @property
    def short_name(self):
        return '{} {}{}'.format(
            self.last_name,
            self.first_name[0] + '.',
            self.patronymic[0] + '.' if self.patronymic else ''
        )


class RegionEmployee(Employee):
    region = models.ForeignKey(Region,
                               null=True,
                               on_delete=models.SET_NULL,)

    class Meta:
        verbose_name = 'Сотрудник района'
        verbose_name_plural = 'Сотрудники района'
        ordering = ('region', 'last_name')


class PrefectureEmployee(Employee):
    district = models.ForeignKey(District,
                                 null=True,
                                 on_delete=models.SET_NULL,)
    can_approve_rating = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Сотрудник префектуры'
        verbose_name_plural = 'Сотрудники префектуры'
        ordering = ('district', 'last_name')

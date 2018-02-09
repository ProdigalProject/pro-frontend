# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=50)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DemoChat(models.Model):
    id = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    message = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'demo_chat'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    name = models.CharField(max_length=100)
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Links(models.Model):
    movieid = models.IntegerField(db_column='movieId', primary_key=True)  # Field name made lowercase.
    imdbid = models.IntegerField(db_column='imdbId')  # Field name made lowercase.
    tmdbid = models.IntegerField(db_column='tmdbId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'links'


class Movies(models.Model):
    movieid = models.IntegerField(db_column='movieId', primary_key=True)  # Field name made lowercase.
    title = models.CharField(max_length=158)
    genres = models.CharField(max_length=77)

    class Meta:
        managed = False
        db_table = 'movies'


class Ratings(models.Model):
    userid = models.IntegerField(db_column='userId', primary_key=True)  # Field name made lowercase.
    movieid = models.IntegerField(db_column='movieId')  # Field name made lowercase.
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    timestamp = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'ratings'
        unique_together = (('userid', 'movieid'),)


class Tags(models.Model):
    userid = models.IntegerField(db_column='userId', primary_key=True)  # Field name made lowercase.
    movieid = models.IntegerField(db_column='movieId')  # Field name made lowercase.
    tag = models.CharField(max_length=50)
    timestamp = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tags'
        unique_together = (('userid', 'movieid', 'tag'),)


class Users(models.Model):
    userid = models.AutoField(db_column='userId', primary_key=True)  # Field name made lowercase.
    fullname = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=20, blank=True, null=True)
    username = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'users'

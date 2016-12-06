# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pinax_notifications', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('message', models.TextField(verbose_name='message')),
                ('medium', models.CharField(max_length=100, verbose_name='medium', choices=[('email', 'email')])),
                ('added', models.DateTimeField(default=django.utils.timezone.now, verbose_name='added', db_index=True)),
                ('unseen', models.BooleanField(default=True, db_index=True, verbose_name='unseen')),
                ('archived', models.BooleanField(default=False, verbose_name='archived')),
                ('on_site', models.BooleanField(default=False, verbose_name='on site')),
                ('notice_type', models.ForeignKey(verbose_name='notice type', to='pinax_notifications.NoticeType')),
                ('recipient', models.ForeignKey(related_name='received_notices', verbose_name='recipient', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='sent_notices', verbose_name='sender', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'notice',
                'verbose_name_plural': 'notices',
            },
        ),
    ]

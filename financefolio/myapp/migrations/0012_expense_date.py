# Generated by Django 5.1 on 2024-10-15 13:38

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0011_remove_expense_planned_expense_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='expense',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

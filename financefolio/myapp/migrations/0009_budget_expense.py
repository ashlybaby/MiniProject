# Generated by Django 5.1 on 2024-09-22 11:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_user_address_user_age_user_city_user_gender_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('month', models.DateField()),
                ('planned_income', models.DecimalField(decimal_places=2, max_digits=12)),
                ('actual_income', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(max_length=100)),
                ('planned_expense', models.DecimalField(decimal_places=2, max_digits=12)),
                ('actual_expense', models.DecimalField(decimal_places=2, max_digits=12)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='expenses', to='myapp.budget')),
            ],
        ),
    ]
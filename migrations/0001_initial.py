# Generated by Django 4.2.2 on 2023-11-04 18:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tickers', models.CharField(max_length=10)),
                ('hourly', models.CharField(max_length=20)),
                ('daily', models.CharField(max_length=20)),
                ('weekly', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Signal',
            fields=[
                ('create_date', models.DateTimeField(auto_now_add=True, primary_key=True, serialize=False)),
                ('ticker', models.CharField(max_length=10)),
                ('category', models.CharField(max_length=10)),
                ('message', models.CharField(max_length=200)),
                ('message_type', models.CharField(max_length=15)),
                ('time_range', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='SignalTrend',
            fields=[
                ('create_date', models.DateTimeField(auto_now_add=True, primary_key=True, serialize=False)),
                ('ticker', models.CharField(max_length=10)),
                ('category', models.CharField(blank=True, max_length=10)),
                ('message', models.CharField(blank=True, max_length=200)),
                ('message_type', models.CharField(max_length=15)),
                ('time_range', models.CharField(max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='TickerData',
            fields=[
                ('ticker', models.CharField(max_length=10, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Trend',
            fields=[
                ('ticker', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('weekly', models.CharField(max_length=200)),
                ('weekly_update_dt', models.DateTimeField(auto_now_add=True)),
                ('daily', models.CharField(max_length=200)),
                ('daily_update_dt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('name', models.CharField(max_length=200)),
                ('email', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('phone', models.IntegerField(default=0)),
                ('username', models.CharField(max_length=200)),
                ('notification', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='WatchList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tickers', models.CharField(max_length=5000)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mauka_api.user')),
            ],
        ),
    ]

# Generated by Django 4.0.4 on 2023-08-14 17:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('borrowing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Paid', 'Paid')], default='Pending', max_length=8)),
                ('type', models.CharField(choices=[('Payment', 'Payment'), ('Fine', 'Fine')], default='Payment', max_length=8)),
                ('session_url', models.URLField()),
                ('session_id', models.CharField(max_length=255)),
                ('money_to_pay', models.DecimalField(decimal_places=2, max_digits=6)),
                ('borrowing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='borrowing.borrowing')),
            ],
        ),
    ]

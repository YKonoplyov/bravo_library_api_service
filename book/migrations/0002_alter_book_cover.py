# Generated by Django 4.2.4 on 2023-08-14 11:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("book", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="book",
            name="cover",
            field=models.CharField(
                choices=[(1, "Hard cover"), (2, "Soft cover")], max_length=10
            ),
        ),
    ]

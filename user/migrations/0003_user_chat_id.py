from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_telegram_nick'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='chat_id',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]

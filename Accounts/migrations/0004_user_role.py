# Generated migration for adding role field to User model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Accounts', '0003_alter_user_options_alter_user_managers_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[('admin', 'Administrator'), ('user', 'Regular User')],
                default='user',
                max_length=10
            ),
        ),
    ]

# Generated by Django 5.1.2 on 2024-10-18 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_alter_user_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.ImageField(default='user/images/default_user.png', upload_to='user/images/'),
        ),
    ]
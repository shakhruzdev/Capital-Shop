# Generated by Django 5.1.2 on 2024-11-28 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_remove_card_expired_at_card_expired_month_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='card',
            name='created_at',
        ),
        migrations.AddField(
            model_name='card',
            name='created_month',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='card',
            name='created_year',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='card',
            name='bank_name',
            field=models.PositiveIntegerField(choices=[(1, 'IPOTEKABANK'), (2, 'QQBBANK'), (3, 'ORIENTFINANSBANK'), (4, 'KAPITALBANK'), (5, 'ASIAALLIANCEBANK')]),
        ),
        migrations.AlterField(
            model_name='card',
            name='card_name',
            field=models.PositiveIntegerField(choices=[(1, 'VISA'), (2, 'MASTERCARD'), (3, 'UZCARD'), (4, 'HUMO')]),
        ),
    ]

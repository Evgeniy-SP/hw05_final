# Generated by Django 2.2.16 on 2022-11-02 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20221013_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(
                blank=True,
                upload_to='posts/',
                verbose_name='Картинка'
            ),
        ),
    ]

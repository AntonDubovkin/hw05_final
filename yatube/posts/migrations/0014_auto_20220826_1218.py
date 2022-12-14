# Generated by Django 2.2.16 on 2022-08-26 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Описание групы', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(help_text='Заголовок группы', max_length=200, verbose_name='Заголовок'),
        ),
    ]

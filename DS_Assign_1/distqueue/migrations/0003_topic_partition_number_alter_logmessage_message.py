# Generated by Django 4.1.7 on 2023-03-05 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distqueue', '0002_delete_ids'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='partition_number',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='logmessage',
            name='message',
            field=models.TextField(),
        ),
    ]
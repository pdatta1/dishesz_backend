# Generated by Django 4.0.2 on 2022-12-04 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0005_alter_photo_src'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='src',
            field=models.ImageField(upload_to='uploads/<function photo_path at 0x7fd757ba3dc0>'),
        ),
    ]
# Generated by Django 4.1.2 on 2023-01-02 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notify", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="notification",
            name="reffered_id",
            field=models.CharField(max_length=15, null=True),
        ),
    ]

# Generated by Django 4.1.2 on 2022-10-31 18:08

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipe", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="photo",
            name="photo",
            field=models.ImageField(
                upload_to="uploads/<function photo_path at 0x7f0246bf58b0>"
            ),
        ),
        migrations.CreateModel(
            name="SavedRecipes",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "recipe",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="users_saved",
                        to="recipe.recipe",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="my_saved_recipes",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

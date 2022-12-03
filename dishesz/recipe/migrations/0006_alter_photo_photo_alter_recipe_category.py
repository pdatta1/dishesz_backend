# Generated by Django 4.1.2 on 2022-11-30 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recipe", "0005_alter_photo_photo_alter_recipe_created_on"),
    ]

    operations = [
        migrations.AlterField(
            model_name="photo",
            name="photo",
            field=models.ImageField(
                upload_to="uploads/<function photo_path at 0x7f2e92b37280>"
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="category",
            field=models.CharField(
                choices=[
                    (1, "Vegan"),
                    (2, "Spanish/Latin"),
                    (3, "Greek"),
                    (4, "American"),
                    (5, "Korean"),
                    (6, "Japanese"),
                    (7, "Chinese"),
                    (8, "Italian"),
                    (8, "Desserts"),
                    (9, "Smoothie"),
                ],
                default=1,
                max_length=16,
            ),
        ),
    ]
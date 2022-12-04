# Generated by Django 4.0.2 on 2022-12-03 23:32

from django.db import migrations, models


def fill_user_profile(apps, schema_editor): 

    User = apps.get_model('users', 'DisheszUser')
    Profile = apps.get_model('users', 'DisheszUserProfile')
    for user in User.objects.all(): 
        profile = Profile.objects.create(dishesz_user=user)
        user.user_profile = profile 
        user.save() 


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_disheszuserprofile_profile_pic'),
    ]

    operations = [
        migrations.RunPython(fill_user_profile)
    ]

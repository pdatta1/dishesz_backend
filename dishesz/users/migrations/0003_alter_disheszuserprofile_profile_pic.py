# Generated by Django 4.0.2 on 2022-12-03 22:50

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
        ('users', '0002_disheszuserprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disheszuserprofile',
            name='profile_pic',
            field=models.ImageField(upload_to='profile/<function photo_path at 0x7f90822b4d30>'),
        ),
        migrations.RunPython(fill_user_profile)
    ]
from django.db import migrations 

def fill_user_profile(apps, schema_editor): 

    User = apps.get_model('users', 'DisheszUser')
    Profile = apps.get_model('users', 'DisheszUserProfile')
    for user in User.objects.all(): 

        if not hasattr(user, 'user_profile'): 
            profile = Profile.objects.create(dishesz_user=user)
            user.user_profile = profile 
            user.save() 


class Migration(migrations.Migration): 

    dependencies = [ 
        ('users', '0004_alter_disheszuserprofile_profile_pic')
    ]

    operations = [ 
        migrations.RunPython(fill_user_profile)
    ]
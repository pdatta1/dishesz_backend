

from django.db import migrations


def fill_user_interest_containers(apps, schema_editor): 

    User = apps.get_model('users', 'DisheszUser')
    container = apps.get_model('users', 'InterestContainer')

    for user in User.objects.all(): 
        
        if not hasattr(user, 'user_interest_container'):
            container.objects.create(dishesz_user=user)



class Migration(migrations.Migration): 

    dependencies = [ 
        ('users', '0004_alter_disheszuserprofile_profile_pic'),
    ]
    operations = [ 
        migrations.RunPython(fill_user_interest_containers)
    ]

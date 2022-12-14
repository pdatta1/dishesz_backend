

from users.generator.scripts.generate_data import GenerateData


def run(): 

    data = GenerateData(clean_database=True)
    data.generate_fake_users(file_directory='generator/json/users.json') 
    data.generate_recipes(file_directory='generator/json/recipes.json')
    data.generate_ingredients(file_directory='generator/json/ingredients.json')
    data.generate_stores(file_directory='generator/json/stores.json')
    #data.generate_photos()



    #data.randomize_follow()


run() 
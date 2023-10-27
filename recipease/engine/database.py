"""
This is used to set up the database tables and import data from a given JSON file
Run using py database.py [method-name] [arguments separated by space]
Example: py database.py get_table Recipe
Another: py database.py sql "SELECT * FROM User"
"""
from contextlib import closing
import mysql.connector

from recipease_sub.settings import DATABASE_URL, DATABASE_NAME, USER_NAME, USER_PASSWORD
from recipease_sub.settings import CREATE_TABLES

# Command Line Stuff
import sys
import json

# String formatting for ingredients
import re

# Slow down a little bit geez the database needs some time
import time


# Do NOT run directly unless you run close on the connection
def __connect():
    db = mysql.connector.connect(
        host=DATABASE_URL,
        user=USER_NAME,
        passwd=USER_PASSWORD
    )
    db.database = DATABASE_NAME
    return db


def __close(db):
    db.commit()
    db.close()


# Helper method for connecting to the database, running SQL code, then closing both the database connection and cursor
# Returns an array of values (if something like Select is called)
# Do NOT run sql directly using c.execute, use this instead to handle closing cursors and everything else
def __run_sql(_sql, is_one=False):
    db = __connect()
    with closing(db.cursor()) as c:
        if is_one:
            try:
                c.execute(_sql)
                a = c.fetchone()
            except:
                print(Exception)
            __close(db)
            return a

        statements = _sql.split(";")
        a = []
        for s in statements:
            try:
                c.execute(s + ";")
                a.append(c.fetchall())
            except Exception as e:
                print(e) # pass  # print("Exception: " + str(e))
    __close(db)
    return a


def create_tables():
    __run_sql(CREATE_TABLES)


def get_table(table_name):
    print(__run_sql('SELECT * FROM {};'.format(str(table_name))))


def delete_data(table_name):
    __run_sql("DELETE FROM {};".format(str(table_name)))


# Allows you to run sql directly from command line
# Example: py database.py sql "SELECT * FROM Recipe"
# Prints value to console if something like SELECT is run
def sql(_sql, is_one=False):
    output = __run_sql(_sql, is_one)
    if output:
        print(output)


# Intended for non-command-line use, returns value instead of printing
def sql_return(_sql, is_one=False):
    return __run_sql(_sql, is_one)


def sql_from_file(path):
    with open(path) as f:
        sql(f.read())


# To confirm it's been added, running "SELECT COUNT(*) FROM recipe" should return [[(259,)]]
def add_json_to_database(path):
    sql_batch = ""
    sql_batch += "INSERT INTO User (email) VALUES ('API');"

    iset = []
    qset = []
    cset = []
    ingredient_counter = 0
    recipe_counter = 0
    category_counter = 0
    wait_timer = 0

    with open(path) as file:
        text = file.read()
    json_data = json.loads(text)
    for id in json_data:
        recipe = json_data[id]
        name = recipe['name']
        source = recipe['source']
        preptime = recipe['preptime']
        waittime = recipe['waittime']
        cooktime = recipe['cooktime']
        servings = recipe['servings']
        comments = recipe['comments']
        calories = recipe['calories']
        fat = recipe['fat']
        satfat = recipe['satfat']
        carbs = recipe['carbs']
        fiber = recipe['fiber']
        sugar = recipe['sugar']
        protein = recipe['protein']
        instructions = recipe['instructions']
        ingredients = recipe['ingredients']
        tags = recipe['tags']

        # Recipes

        _sql = (f"INSERT INTO Recipe (recipeID, email, title, description, cook_time, instructions) "
                f"VALUES ({int(recipe_counter)}, 'API', '{str(name)}', 'Added by the API', {int(cooktime)}, "
                f"'{str(instructions)}');")
        sql_batch += _sql  # sql_return(_sql)

        # Nutrition

        _sql = (f"INSERT INTO Nutrition (recipeID, calories, fat, satfat, carbs, fiber, sugar, protein) "
                f"VALUES ({int(recipe_counter)}, {int(calories)}, {int(fat)}, {int(satfat)}, {int(carbs)}, "
                f"{int(fiber)}, {int(sugar)}, {int(protein)});")
        sql_batch += _sql  # sql_return(_sql)

        # Comments

        if len(comments) > 0:
            _sql = (f"INSERT INTO Comment (recipeID, commentID, content, email) VALUES ({int(recipe_counter)}, 0, "
                    f"'{comments}', 'API');")
            sql_batch += _sql  # sql_return(_sql)

        # Ingredients

        for l in ingredients:
            amount = 0
            for word in l.strip().split(" "):
                if re.search("www.|http", word):  # No links please, thank you
                    continue
                if re.search('[0-9]', word):  # This is a number, but get it anyway
                    qset.append(re.sub('[()\[\],]', '', word.lower()))
                    if re.sub('[()\[\],]', '', word.lower()).isnumeric():
                        amount = re.sub('[()\[\],]', '', word.lower())
                else:
                    w = re.sub('[()\[\],]', '', word.lower())
                    if not (w in iset):
                        iset.append(w)
                        _sql = (f"INSERT INTO Ingredient (ingredientID, name, food_type) "
                                f"VALUES ({int(ingredient_counter)}, '{w}', '');")
                        sql_batch += _sql  # sql_return(_sql)
                        loc = ingredient_counter
                        ingredient_counter += 1
                    else:
                        loc = iset.index(w)

                    _sql = (f"INSERT INTO Recipe_Ingredients (recipeID, ingredientID, amount) "
                            f"VALUES ({int(recipe_counter)}, {int(loc)}, {amount});")
                    sql_batch += _sql  # sql_return(_sql)

        # Tags

        for c in tags:
            if not (c in cset):
                cset.append(c)
                _sql = (f"INSERT INTO Category (categoryID, name) "
                        f"VALUES ({int(category_counter)}, '{c}');")
                sql_batch += _sql  # sql_return(_sql)
                loc = category_counter
                category_counter += 1
            else:
                loc = cset.index(c)
            _sql = (f"INSERT INTO Belongs_To (recipeID, categoryID) "
                f"VALUES ({int(recipe_counter)}, {int(loc)});")
            sql_batch += _sql  # sql_return(_sql)

        recipe_counter += 1

        wait_timer += 1
        if wait_timer > 29:
            time.sleep(2)
            wait_timer = 0
        if recipe_counter % 150 == 0:
            time.sleep(3)
            wait_timer = 0

        # Stop after 300 have been uploaded for now, don't wanna get too crazy with the requests
        if recipe_counter >= 300:
            break

        sql_return(sql_batch)
        sql_batch = ""

        print(f"Progress: {recipe_counter}/{300}\r", end="", flush=True)

def user_exists(email):
    # SQL query to check if the user exists in the users table
    sql_query = f"SELECT COUNT(*) FROM User WHERE email = '{email}';"
    
    # Execute the SQL query 
    result = __run_sql(sql_query)

    # Check if the result indicates that the user exists
    user_exists = result[0][0][0] 
    return user_exists

def add_user(email, username):
    sql_query = f"INSERT INTO User (email, username) VALUES ('{email}', '{username}');"
    __run_sql(sql_query)

def get_user_info(username):
    sql_query = f"SELECT username FROM User WHERE username = '{username}';"
    result = __run_sql(sql_query)
    return result[0][0][0]

# used to figure out the next recipeID
def max_recipeID():
    maxID = __run_sql("SELECT MAX(recipeID) FROM Recipe;")
    print(maxID[0][0][0])
    return maxID[0][0][0]

def add_new_recipe(email, recipe_id, title, description, cook_time, instructions):
    sql_query = (
        f"INSERT INTO Recipe (recipeID, email, title, description, cook_time, instructions) "
        f"VALUES ({int(recipe_id)}, '{str(email)}', \"{str(title)}\", \"{str(description)}\", {int(cook_time)}, "
        f"\"{str(instructions)}\");"
    )
    __run_sql(sql_query)

def add_nutrition_info(recipe_id, calories , fat, satfat, carbs, fiber, sugar, protein):
    sql_query = (f"INSERT INTO Nutrition (recipeID, calories, fat, satfat, carbs, fiber, sugar, protein) "
                f"VALUES ({int(recipe_id)}, {int(calories)}, {int(fat)}, {int(satfat)}, {int(carbs)}, "
                f"{int(fiber)}, {int(sugar)}, {int(protein)});")
    __run_sql(sql_query)

# used to figure out the next ingredientID
def max_ingredientID():
    maxID = __run_sql("SELECT MAX(ingredientID) FROM Ingredient;")
    print(maxID[0][0][0])
    return maxID[0][0][0]

def add_ingredient(ingredientID, recipeID, name, food_type, amount):
    sql_query = (f"INSERT INTO Ingredient (ingredientID, name, food_type) "
            f"VALUES ({int(ingredientID)}, '{str(name)}', '{str(food_type)}');")

    __run_sql(sql_query)
                    
    sql_query = (f"INSERT INTO Recipe_Ingredients (recipeID, ingredientID, amount) "
            f"VALUES ({int(recipeID)}, {int(ingredientID)}, '{str(amount)}');")
    
    __run_sql(sql_query)


def rating_exists(email, recipe_id):
    sql_query = (f"SELECT value FROM Rates WHERE email = '{email}' AND recipeID = {recipe_id};")

    result = __run_sql(sql_query)

    if result and result[0]:  
        rating_exists = result[0][0]
        return rating_exists
    else:
        return None
    

def add_rating(email, recipe_id, rating):
    sql_query = (f" INSERT INTO Rates (email, recipeID, value)"
                 f" VALUES ('{str(email)}', {int(recipe_id)}, {int(rating)});")
    __run_sql(sql_query)


def update_rating(email, recipe_id, rating):
    sql_query = (f"UPDATE Rates SET value = {int(rating)} "
                f"WHERE email = '{str(email)}' AND recipeID = {int(recipe_id)};")
    __run_sql(sql_query)

def get_recipe(recipe_id):
    sql_query = (f" SELECT * FROM Recipe WHERE recipeID = {recipe_id};")
    __run_sql(sql_query)

def max_commentID():
    maxID = __run_sql("SELECT MAX(commentID) FROM Comment;")
    print(maxID[0][0][0])
    return maxID[0][0][0]

def get_comments(recipe_id):
    sql_query = f"SELECT content, email FROM Comment WHERE recipeID = {recipe_id};"
    __run_sql(sql_query)

def add_new_comment(email, recipe_id, content, commentID ):
    sql_query = (f"INSERT INTO Comment (email, recipeID, content, commentID) "
                 f"VALUES ('{str(email)}',{int(recipe_id)}, '{str(content)}',{int(commentID)});")
    __run_sql(sql_query)

def edit_comment(comment_id):
    sql_query = (f"UPDATE Comment SET content = '{str(content)}' "
                f"WHERE commentID = {int(comment_id)};")
    __run_sql(sql_query)

def edit_recipe(recipe_id, new_title, new_description, new_cook_time, new_instructions):
    sql_query = (f"UPDATE Recipe SET title = '{str(new_title)}', description = '{str(new_description)}', "
                 f"cook_time = {int(new_cook_time)}, instructions = '{str(new_instructions)}' "
                 f"WHERE recipeID = {int(recipe_id)};")

    __run_sql(sql_query)

def get_all_user_recipes(email):
    sql_query = (f"SELECT recipeID, title, description FROM Recipe WHERE email = '{str(email)}';")
    return __run_sql(sql_query)

def get_ingredient_info(ingredient_id):
    sql_query = f"SELECT name, food_type FROM Ingredient WHERE ingredientID = {int(ingredient_id)};"
    return __run_sql(sql_query)

def add_to_favorite(email, recipe_id):
    sql_query = f"INSERT INTO Favorite (email, recipeID) VALUES ('{str(email)}', int(recipe_id));"
    __run_sql(sql_query)

def view_favorites(email):
    sql_query = f"SELECT * FROM Recipe NATURAL JOIN Favorite WHERE email = '{str(email)}';"
    __run_sql(sql_query)

def comment_length_check():
    sql_query = "ALTER TABLE Comment ADD CONSTRAINT MaxCommentLengthCheck CHECK (LENGTH(content) <= 128);"
    __run_sql(sql_query)




# Make this command-line-able
if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])

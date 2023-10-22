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


# Make this command-line-able
if __name__ == "__main__":
    globals()[sys.argv[1]](*sys.argv[2:])

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .database import sql_return, user_exists, add_user, get_user_info, max_recipeID, add_new_recipe, add_nutrition_info, max_ingredientID, add_ingredient
from .forms import SearchForm, RecipeForm, IngredientForm, IngredientFormSet
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user

def index(request):
    user = get_user(request)  # Get the authenticated user
    if user.is_authenticated:
        if not user_exists(user.email):
            add_user(user.email, user.username)
    if request.method == "POST":
        form = SearchForm(request.POST, request.FILES)
        if form.is_valid():
            search_term = request.POST.get('search')
            ingredient_search = (f"SELECT recipeID "
                                 f"FROM Recipe NATURAL JOIN Recipe_Ingredients "
                                 f"NATURAL JOIN Ingredient "
                                 f"WHERE Ingredient.name LIKE '%{search_term}%'")
            full_search = (f"SELECT * "
                           f"FROM Recipe NATURAL JOIN Ingredient NATURAL JOIN Recipe_Ingredients "
                           f"WHERE Recipe.recipeID IN ({ingredient_search});")
            search_result = sql_return(full_search)

            cleaned = []
            last = ""
            for s in search_result[0]:
                if s[3] != last:
                    last = s[3]
                    cleaned.append(s)
                else:
                    l = list(cleaned[-1])
                    l[8] = l[8] + ", " + s[8]
                    cleaned[-1] = tuple(l)

            print(cleaned)

            return render(request, 'search.html', {'search': cleaned})

    form = SearchForm()
    return render(request, 'index.html', {'form': form})

def search(request):
    return render(request, "search.html")

@login_required
def view_profile(request, owner = None):
    curr_user = get_user(request)
    if owner:
        owner_user = get_user_info(owner) #returns username
    else:
        owner_user = curr_user
    return render(request, 'profile.html',
        {"request_type":request.method, "user":curr_user, "owner":owner_user,})

def success_view(request):
    return render(request, 'success.html') 

@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST)
        ingredients_formset = IngredientFormSet(request.POST)

        if form.is_valid() and ingredients_formset.is_valid():
            recipe_id = max_recipeID() + 1  
            title = form.cleaned_data['title']
            description = form.cleaned_data['description']
            cook_time = form.cleaned_data['cook_time']
            instructions = form.cleaned_data['instructions']

            #add to Recipe table
            add_new_recipe(get_user(request).email, recipe_id, title, description, cook_time, instructions)

            #add to Nutrition table
            calories = form.cleaned_data['calories']
            fat = form.cleaned_data['fat']
            sat_fat = form.cleaned_data['sat_fat']
            carbs = form.cleaned_data['carbs']
            fiber = form.cleaned_data['fiber']
            sugar = form.cleaned_data['sugar']
            protein = form.cleaned_data['protein']
            add_nutrition_info(recipe_id, calories , fat, sat_fat, carbs, fiber, sugar, protein)

          
            for ingredient_form in ingredients_formset:
                name = ingredient_form.cleaned_data.get('name')
                amount = ingredient_form.cleaned_data.get('amount')
                ingredient_type = ingredient_form.cleaned_data.get('ingredient_type')
                ingredientID = max_ingredientID() + 1 

                #add to DB 
                add_ingredient(ingredientID, recipe_id, name, ingredient_type, amount)

            return redirect('success_view') 

    else:
        form = RecipeForm()
        ingredients_formset = IngredientFormSet()

    return render(request, 'add_recipe.html', {'form': form, 'ingredients_formset': ingredients_formset})


    

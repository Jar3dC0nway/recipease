from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect

from .database import sql_return, user_exists, add_user, get_user_info, max_recipeID, add_new_recipe, \
    add_nutrition_info, max_ingredientID, add_ingredient, rating_exists, add_rating, update_rating, add_new_comment, \
    max_commentID, edit_comment, delete_comment, favorite_exists, add_favorite, get_favorites
from .forms import SearchForm, RecipeForm, IngredientForm, IngredientFormSet, RecipeRatingForm, CommentForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user


def index(request):
    user = get_user(request)  # Get the authenticated user
    if user.is_authenticated:
        if not user_exists(user.email):
            add_user(user.email, user.username)

    form = SearchForm()
    return render(request, 'index.html', {'form': form})


def search(request):
    if request.method != "GET":
        return HttpResponseRedirect('index')
    form = SearchForm(request.GET, request.FILES)
    if form.is_valid():
        search_term = str(request.GET.get('search'))
        terms = search_term.split(" ")
        ingredient_search = "SELECT recipeID FROM Recipe WHERE false"  # Start with empty table
        for term in terms:
            ingredient_search += (f" UNION (SELECT recipeID "  # Add each term to recipe search
                                  f"FROM Recipe NATURAL JOIN Recipe_Ingredients "
                                  f"NATURAL JOIN Ingredient "
                                  f"WHERE Ingredient.name LIKE '%{term}%')")
        full_search = (f"SELECT * "  # Convert recipeIDs back into recipe data
                       f"FROM Recipe NATURAL JOIN Ingredient NATURAL JOIN Recipe_Ingredients "
                       f"WHERE Recipe.recipeID IN ({ingredient_search});")
        search_result = sql_return(full_search)

        cleaned = []
        last = ""
        for s in search_result[0]:  # Remove duplicate recipeIDs and combine ingredient data
            if s[3] != last:  # If you haven't seen this recipe yet, add it
                last = s[3]
                cleaned.append(s)
                li = list(cleaned[-1])

                recipeID = li[0]
                comments = sql_return(f"SELECT content, email, recipeID, commentID FROM Comment WHERE recipeID = {recipeID};")
                li.append(comments[0])

                li[8] = [s[8]]
            else:  # Otherwise, don't add it and just add the ingredient info
                li = list(cleaned[-1])
                li[8].append(s[8])
            cleaned[-1] = tuple(li)

            for term in terms:  # Make it so matching ingredients will become highlighted in the search results page
                if term in li[8][-1]:
                    if term != li[8][-1]:
                        terms.append(li[8][-1])

        # print(cleaned)

        return render(request, 'search.html', {'search': cleaned, 'terms': terms})

    return render(request, "search.html")


@login_required
def view_profile(request, owner=None):
    curr_user = get_user(request)
    favorites = get_favorites(curr_user.email)
    if owner:
        owner_user = get_user_info(owner)  # returns username
    else:
        owner_user = curr_user
    return render(request, 'profile.html',
                  {"request_type": request.method, "user": curr_user, "owner": owner_user, "favorites": favorites})


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

            # add to Recipe table
            add_new_recipe(get_user(request).email, recipe_id, title, description, cook_time, instructions)

            # add to Nutrition table
            calories = form.cleaned_data['calories']
            fat = form.cleaned_data['fat']
            sat_fat = form.cleaned_data['sat_fat']
            carbs = form.cleaned_data['carbs']
            fiber = form.cleaned_data['fiber']
            sugar = form.cleaned_data['sugar']
            protein = form.cleaned_data['protein']
            add_nutrition_info(recipe_id, calories, fat, sat_fat, carbs, fiber, sugar, protein)

            for ingredient_form in ingredients_formset:
                name = ingredient_form.cleaned_data.get('name')
                amount = ingredient_form.cleaned_data.get('amount')
                ingredient_type = ingredient_form.cleaned_data.get('ingredient_type')
                ingredientID = max_ingredientID() + 1

                # add to DB
                add_ingredient(ingredientID, recipe_id, name, ingredient_type, amount)

            return redirect('success_view')

    else:
        form = RecipeForm()
        ingredients_formset = IngredientFormSet()

    return render(request, 'add_recipe.html', {'form': form, 'ingredients_formset': ingredients_formset})


@login_required
def favorite_recipe(request, recipe_id):
    exists = favorite_exists(get_user(request).email, recipe_id)
    if not(exists):
        add_favorite(get_user(request).email, recipe_id)

    return render(request, 'favorite_success.html')


def rating_success_view(request):
    return render(request, 'rating_success.html')


@login_required
def rate_recipe(request, recipe_id):
    if request.method == 'POST':
        rating = request.POST.get('rating')
        form = RecipeRatingForm(request.POST)

        if form.is_valid():
            email = get_user(request).email
            rating = form.cleaned_data['rating']

            # Check if the user has already rated this recipe
            exists = rating_exists(email, recipe_id)
            print(exists)

            if exists:
                # Update the existing rating
                update_rating(email, recipe_id, rating)
            else:
                # Create a new rating
                add_rating(email, recipe_id, rating)

            return redirect('rating_success_view')

    return render(request, 'rate_recipe.html', {'recipe_id': recipe_id})


def comment_success_view(request):
    return render(request, 'comment_success.html')


@login_required
def add_comment(request, recipe_id):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            email = get_user(request).email
            commentID = max_commentID() + 1

            # Insert the new comment using custom SQL
            add_new_comment(email, recipe_id, content, commentID)

            return redirect('comment_success_view')

    return render(request, 'add_comment.html', {'recipe_id': recipe_id})


def check_matching_email(request, recipe_id, comment_id):

    if not (str(recipe_id).isnumeric() and str(comment_id).isnumeric()):  # Imagine sql injecting comments
        print(f"{request.user} tried modifying/deleting comment with recipeID: {recipe_id} and commentID: {comment_id}")
        return False, HttpResponseRedirect("/")

    c = sql_return(f"SELECT email FROM Comment WHERE recipeID = {recipe_id} AND commentID = {comment_id};")
    try:
        c = c[0][0]
    except Exception:
        return False, HttpResponseRedirect("/")
    if len(c) == 0:
        print("email not found")
        return False, HttpResponseRedirect("/")
    if c[0] != get_user(request).email:
        print("email not matched")
        return False, HttpResponseRedirect("/")
    return True, None


@login_required
def edit_comment_info(request, recipe_id, comment_id):
    success, http = check_matching_email(request, recipe_id, comment_id)
    if not success:
        return http

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            edit_comment(recipe_id, comment_id, content)
            return redirect('comment_edit_success_view')

    return render(request, 'edit_comment.html', {'recipe_id': recipe_id, 'comment_id': comment_id})


@login_required
def edit_comment_info(request, recipe_id, comment_id):
    success, http = check_matching_email(request, recipe_id, comment_id)
    if not success:
        return http

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data['content']
            edit_comment(recipe_id, comment_id, content)
            return redirect('comment_edit_success_view')

    return render(request, 'edit_comment.html', {'recipe_id': recipe_id, 'comment_id': comment_id})


def comment_edit_success_view(request):
    return render(request, 'comment_edit_success.html')


@login_required
def delete_comment_info(request, recipe_id, comment_id):
    success, http = check_matching_email(request, recipe_id, comment_id)
    if not success:
        return http

    delete_comment(int(recipe_id), int(comment_id))

    return redirect('comment_delete_success_view')


def comment_delete_success_view(request):
    return render(request, 'comment_delete_success.html')
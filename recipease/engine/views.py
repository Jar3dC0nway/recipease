from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .database import sql_return, user_exists, add_user
from .forms import SearchForm
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

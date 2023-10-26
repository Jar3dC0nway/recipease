from django import forms
from django.forms import formset_factory



class SearchForm(forms.Form):
    search = forms.CharField(label="Search")
    

class IngredientForm(forms.Form):
    name = forms.CharField(max_length=32)
    amount = forms.CharField(max_length=32)
    ingredient_type = forms.CharField(max_length=32)

IngredientFormSet = formset_factory(IngredientForm, extra=1)


class RecipeForm(forms.Form):
    title = forms.CharField(max_length=255)
    description = forms.CharField(widget=forms.Textarea)
    cook_time = forms.IntegerField()
    instructions = forms.CharField(widget=forms.Textarea)
    calories = forms.IntegerField()
    fat = forms.IntegerField()
    sat_fat = forms.IntegerField()
    carbs = forms.IntegerField()
    fiber = forms.IntegerField()
    sugar = forms.IntegerField()
    protein = forms.IntegerField()
    ingredients = IngredientFormSet()


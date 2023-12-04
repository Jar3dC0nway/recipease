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
    calories = forms.IntegerField(required=False, initial=0)
    fat = forms.IntegerField(required=False, initial=0)
    sat_fat = forms.IntegerField(required=False, initial=0)
    carbs = forms.IntegerField(required=False, initial=0)
    fiber = forms.IntegerField(required=False, initial=0)
    sugar = forms.IntegerField(required=False, initial=0)
    protein = forms.IntegerField(required=False, initial=0)
    ingredients = IngredientFormSet()


class RecipeRatingForm(forms.Form):
    rating = forms.IntegerField(
        label='Rating',
        min_value=1,
        max_value=5,
        widget=forms.NumberInput(attrs={'type': 'number', 'min': 1, 'max': 5}),
    )

class CommentForm(forms.Form):
    content = forms.CharField(label='Comment', widget=forms.Textarea(attrs={'rows': 3}))

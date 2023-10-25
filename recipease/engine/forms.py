from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(label="Search")


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


#! python3

# Grocery List Maker
# Takes in a list of urls and creates a list of grocery ingredients for shopping
# options to export list and manually add items to it

import requests, lxml, re, sys, pyperclip, shelve, pprint
from bs4 import BeautifulSoup
from recipe_parser import RecipeNLP

grocery_list_shelf = shelve.open('grocery_list_data')
if 'grocery_list' in grocery_list_shelf:  # if this not the first time we've opened the program
    print("getting grocery list from file")
    grocery_list = grocery_list_shelf['grocery_list']  # dict containing all items, ordered like "ingredient":"amount"
else:
    print("creating new grocery list")
    grocery_list = {}
    grocery_list_shelf['grocery_list'] = grocery_list

if 'recipes' in grocery_list_shelf:
    recipe_list = grocery_list_shelf['recipes']
    print('found a recipe list')
else:
    recipe_list = []
    grocery_list_shelf['recipes'] = recipe_list


def parse_recipe(url):

    # TODO: capture url webpage and open
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')

    # TODO: scan webpage for ingredients
    ingredient_lines = soup.find_all("span", itemprop="recipeIngredient")

    nlp = RecipeNLP()

    for line in ingredient_lines:
        parsed_line = nlp.parse(line.text)

        ingredient = parsed_line.ingredient
        measurement = parsed_line.measurement
        amount = parsed_line.amount

        # TODO: add item to list if necessary. if not, add additional reference to item
        if ingredient in grocery_list:
            if measurement in grocery_list[ingredient]:  # if we've used the same measurement before
                grocery_list[ingredient][measurement] += amount
        else:
            grocery_list[ingredient] = {measurement: amount}

        # TODO: remove qualifiers from ingredient (to reduce duplicates)


    # TODO: prompt to ask for additional ingredients

    # TODO: prompt to ask for manual adding of ingredients

    # TODO: prompt to ask for export

    grocery_list_shelf['grocery_list'] = grocery_list  # save updated list to file

    recipe_list.append(url)
    grocery_list_shelf['recipes'] = recipe_list # save the recipe to file

    print(grocery_list_shelf['recipes'])

def clear_list():
    if 'grocery_list' in grocery_list_shelf:
        grocery_list_shelf['grocery_list'] = {}
        print("cleared the grocery list")
    if 'recipes' in grocery_list_shelf:
        grocery_list_shelf['recipes'] = []
        print("cleared the recipe list")


def print_list():
    print(" For all recipes, you will need: ")
    grocery_string = ""
    for k, v in grocery_list.items():
        for measurement, amount in v.items():
            if measurement is not None:
                if amount is not 0:
                    grocery_string += str(amount) + " " + measurement + " "

        grocery_string += k + "\n"

    print(grocery_string)
    return grocery_string

def export_list():
    with open('grocery_list.txt', 'w') as exported_list:
        exported_list.write('Grocery List \n')
        exported_list.write('---------------\n')

        exported_list.write(print_list())

        exported_list.write("\n These ingredients came from these recipes: \n")
        for recipe in grocery_list_shelf['recipes']:
            exported_list.write(recipe + '\n')


if len(sys.argv) < 2:
    print("no arguments. assuming url is on clipboard")
    recipes_to_add = str(pyperclip.paste())
    print("adding {} ".format(recipes_to_add))
    parse_recipe(recipes_to_add)
elif sys.argv[1] == 'clear':
    clear_list()
elif sys.argv[1] == 'print':
    print_list()
elif sys.argv[1] == 'export':
    export_list()
else:
    recipes_to_add = sys.argv[1:]

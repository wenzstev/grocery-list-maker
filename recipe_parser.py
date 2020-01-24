import spacy, pprint, re
from spacy import displacy
from fractions import Fraction
from first_dataset import ingredient_dataset

test_recipe_text = ["1 cup flour, sifted",
                    "1 teaspoons sea salt",
                    "1 egg",
                    "1/2 cup milk",
                    "1 rounded tablespoon baking powder",
                    "2 tablespoons olive oil",
                    "3 cups lightly toasted sesame seeds",
                    "1 (8 oz) package ground beef"]

recipe_example = {'flour': {'cup': 1},
                  'salt': {'teaspoon': 1},
                  'egg': {'whole': 1},
                  'milk': {'cup': .5},
                  'baking powder': {'tablespoon': 1}}


class RecipeNLP:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def parse(self, recipe_line):
        return ParsedLine(self.nlp, recipe_line)


class ParsedLine:
    def __init__(self, nlp, recipe_line):
        nlp_ing = nlp(recipe_line)
        self.measurement_regex = re.compile('(cup|tablespoon|teaspoon|oz|pound|ounce|clove|cube)s?')

        self.ingredient = ""
        self.measurement = ""
        self.amount = 0

        print()
        print(recipe_line)

        for token in nlp_ing:
            print(token, token.dep_, token.pos_)

            # TODO: determine the amount
            if self.measurement_regex.search(token.text):
                print("the measurement is {}".format(token))
                self.measurement = self.measurement_regex.search(token.text).group(1)
            # TODO: determine the ingredient
            elif token.dep_ in ['ROOT', 'nsubj', 'dobj', 'appos']:
                if token.pos_ in ['NOUN', 'PROPN']:
                    print("the ingredient is {}".format(token))

                    if token.lower_ in ['salt', 'water']:   # ignore certain things that pretty much everyone has
                        print('ingredient matches "ignore" list')
                        continue


                    # TODO: check if there are any compound words
                    print(list(token.children))
                    print('checking children for compounds')
                    for child in token.children:
                        print('checking {}'.format(child))
                        if not self.measurement_regex.match(child.text):
                            print('not a measurement')
                            if child.dep_ in ['compound', 'amod']:
                                print('found a compound')
                                self.ingredient += child.text + " "

                    self.ingredient += token.text + " "

                if token.pos_ == 'NUM':  # sometimes the amount is registered as nsubj
                    try:
                        self.amount = Fraction(token.text)
                    except ValueError as err:
                        print("ValueError: {}".format(err))
            # TODO: determine the measurement (if any)
            elif token.pos_ == 'NUM':
                print("the amount is {}".format(token))
                try:
                    self.amount = Fraction(token.text)
                except ValueError as err:
                    print("ValueError: {}".format(err))
            elif token.pos_ == 'X' and token.dep_ == 'nummod':
                print("the amount is {}".format(token))
                try:
                    self.amount = Fraction(token.text)
                except ValueError as err:
                    print("ValueError: {}".format(err))



if __name__ == '__main__':
    training_set = []
    recipe_nlp = RecipeNLP()

    for line in ingredient_dataset:
        parsed_line = recipe_nlp.parse(line)
        training_set.append((line, [parsed_line.amount, parsed_line.measurement, parsed_line.ingredient]))

    pp = pprint.PrettyPrinter()
    pp.pprint(training_set)

    with open('annotated_data.py', 'w') as annotated_file:
        annotated_file.write(pp.pformat(training_set))
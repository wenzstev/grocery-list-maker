import re, pprint
from old_version.combined_data_old_annotations import annotated_for_testing_with_INGREDIENT

test_recipe_text = ["1 cup flour, sifted",
                    "1 teaspoons sea salt",
                    "1 egg",
                    "1/2 cup milk",
                    "1 rounded tablespoon baking powder",
                    "2 tablespoons olive oil",
                    "3 cups lightly toasted sesame seeds",
                    "1 (8 oz) package ground beef"]


def main(training_set, entity_type):
    complete_training_data = []
    # check if the training set is already formatted properly
    is_formatted = isinstance(training_set[0], tuple)  # TODO: more rigorous checks for alternate data types

    # TODO: loop through all lines in the training set
    for line in training_set:
        if is_formatted:
            raw_text = line[0]
        else:
            raw_text = line

        found_entities = entity_search(raw_text)
        while not found_entities:  # repeat the function until all matches are found
            found_entities = entity_search(raw_text)

        # TODO: if so, record the input as the entity and move to the next example
        annotated_entity_list = []
        if not isinstance(found_entities, bool):
            annotated_entity_list = [(entity[0], entity[1], entity_type) for entity in found_entities]
        if is_formatted:
            annotated_entity_list.extend(line[1]["entities"])

        complete_training_data.append((raw_text, {"entities": annotated_entity_list}))

    return complete_training_data


# helper function to search the line for inputted entities
def entity_search(line):
    found_entities = []
    print(line)
    # TODO: prompt the user to say what the entity is
    line_entity = input("Enter the entity (or leave blank if none):")

    # check if user entered nothing
    if not line_entity:
        print("entered nothing. returning")
        return True

    # TODO: check that the user's input matched part of the string
    entities = line_entity.split(', ')  # supports more than one entity, demarcated by ', '
    for entity in entities:  # loop through all entities and see if they match
        entity_regex = re.compile(entity)
        entity_match = entity_regex.search(line)
        if entity_match:
            found_entities.append((entity_match.start(), entity_match.end()))
        # TODO: if not, prompt the user again
        else:
            print("error: {} did not match.".format(entity))

    if len(found_entities) == len(entities):  # if we found all the typed entities
        return found_entities
    else:
        return False


if __name__ == "__main__":
    new_annotated_data = main(annotated_for_testing_with_INGREDIENT, "CARDINAL")

    with open('combined_data_old_annotations.py', 'a') as data_file:
        pp = pprint.PrettyPrinter()
        data_file.write("annotated_for_testing_with_all = " + pp.pformat(new_annotated_data))

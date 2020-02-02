import re, pprint, plac, importlib
from pathlib import Path




@plac.annotations(
    training_file=("The filename containing the text you wish to annotate", "option", "tf", Path),
    entity_type=("The name of the entity you wish to annotate", "option", "e", str)
)
def main(training_file=None, entity_type=None):
    """Script to more easily annotate spaCy NER training examples"""

    list_to_annotate = []
    complete_training_data = []

    if not training_file:
        training_file = input("Please enter the filename of the data you wish to annotate: ")

    if not entity_type:
        entity_type = input("Please enter the name of the entity you wish to annotate for: ")


    # TODO: check the extension to determine what sort of file was entered
    if training_file.suffix == '.txt': # we expect raw lines of text, no annotations
        name_of_list = training_file.stem   # save the name for later
        with open(training_file, 'r') as training_file:
            for line in training_file:
                list_to_annotate.append(line)


    elif training_file.suffix == '.py': # we expect partially annotated text here
        training_file = importlib.import_module(training_file.stem)
        print("Lists found in this module: ")
        print([item for item in dir(training_file) if not item.startswith("__")])

        chosen_list = input("Please type the name of the list you would like to annotate: ")
        if chosen_list in dir(training_file):
            list_to_annotate = eval("training_file.{}".format(chosen_list))

        name_of_list = chosen_list

    else:
        print("Unsupported format entered. Trying to parse.")
        with open(training_file, 'r') as training_file:
            for line in training_file:
                list_to_annotate.append(line)


    # check if the training set is already formatted properly
    is_formatted = isinstance(list_to_annotate[0], tuple)

    # loop through all lines in the training set
    for line in list_to_annotate:
        if is_formatted:
            raw_text = line[0]
        else:
            raw_text = line

        found_entities = entity_search(raw_text)
        while not found_entities:  # repeat the function until all matches are found
            found_entities = entity_search(raw_text)

        # record the input as the entity and move to the next example
        annotated_entity_list = []
        if not isinstance(found_entities, bool):
            annotated_entity_list = [(entity[0], entity[1], entity_type) for entity in found_entities]
        if is_formatted:
            annotated_entity_list.extend(line[1]["entities"])

        complete_training_data.append((raw_text, {"entities": annotated_entity_list}))

    # choose the file to save and the name of the file
    filename_to_save = input("Please enter the name of the .py file you would like to save your annotated data to: ")
    listname_to_save = input("Please enter your name for the annotated data (or leave blank for automatic name):")

    if not listname_to_save:
        listname_to_save = "{}_annotated_with_{}".format(name_of_list, entity_type)

    if not filename_to_save.endswith('.py'):
        filename_to_save += '.py'

    with open(filename_to_save, 'a') as annotated_file:
        pp = pprint.PrettyPrinter()
        annotated_file.write(listname_to_save + ' = ')
        annotated_file.write(pp.pformat(complete_training_data))
        annotated_file.write('\n\n')


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
    plac.call(main)

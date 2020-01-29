
import spacy

from combined_data import annotated_for_testing_with_all, new_annotated_data

test_model = spacy.load('ingredient_test')

success = {
    "CARDINAL": [0, 0],         # first num is success, second num is all attempts
    "QUANTITY": [0, 0],
    "INGREDIENT": [0, 0]
}

for line in annotated_for_testing_with_all:
    doc = test_model(line[0])
    line[1]['entities'].sort()  # we sort because the annotations are not originally in order

    for ent, tup in zip(doc.ents, line[1]['entities']):
        print(ent.start_char, ent.end_char, ent.label_)
        print(tup)

        found_annotation = (ent.start_char, ent.end_char, ent.label_)

        if found_annotation == tup:
            success[tup[2]][0] += 1
        else:
            print(ent.text)

        success[tup[2]][1] += 1

    print()

cardinal = success['CARDINAL']
quantity = success['QUANTITY']
ingredient = success['INGREDIENT']

print("success rates as follows")
print(f"CARDINAL: {cardinal[0]} out of {cardinal[1]} for total of {cardinal[0]/cardinal[1]*100: .2f}%")
print(f"QUANTITY: {quantity[0]} out of {quantity[1]} for total of {quantity[0]/quantity[1]*100: .2f}%")
print(f"INGREDIENT: {ingredient[0]} out of {ingredient[1]} for total of {ingredient[0]/ingredient[1]*100: .2f}%")


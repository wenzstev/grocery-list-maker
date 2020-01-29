from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding

import pprint

from first_dataset import ingredient_dataset
from combined_data import new_annotated_data

TRAIN_DATA = [
    ('1 1/2 cups sugar', {"entities": [(0, 10, "QUANTITY")]}),
    ('3/4 cup rye whiskey', {"entities": [(0, 7, "QUANTITY")]}),
    ('3/4 cup brandy', {"entities": [(0, 7, "QUANTITY")]}),
    ('1/2 cup rum', {"entities": [(0, 7, "QUANTITY")]}),
    ('1 to 2 cups heavy cream, lightly whipped', {"entities": [(0, 11, "QUANTITY")]}),
    ('2 1/2 pounds veal stew meat, cut into 2x1-inch pieces', {"entities": [(0, 12, "QUANTITY")]}),
    ('4 tablespoons olive oil', {"entities": [(0, 13, "QUANTITY")]}),
    ('1 1/2 cups chopped onion', {"entities": [(0, 10, "QUANTITY")]}),
    ('1 1/2 tablespoons chopped garlic', {"entities": [(0, 17, "QUANTITY")]}),
    ('12 egg whites', {"entities": [(0, 2, "CARDINAL")]}),
    ('12 egg yolks', {"entities": [(0, 2, "CARDINAL")]}),
    ('Garnish: ground nutmeg', {"entities": []}),
    ('18 fresh chestnuts', {"entities": [(0, 2, "CARDINAL")]}),
    ('1 bay leaf', {"entities": [(0, 1, "CARDINAL")]}),
    ('6 medium carrots, peeled, cut into 1-inch pieces', {"entities": [(0, 1, "CARDINAL"), (35, 48, "QUANTITY")]}),
    ('4 or 5 slices brioche, or good quality white bread (I like Pepperidge Farm), 1/4 inch thick, crusts removed',
     {"entities": [(0, 13, "QUANTITY"), (77, 85, "QUANTITY")]}),
    ('3 extra-large eggs', {"entities": [(0, 1, "CARDINAL")]}),
    ('2 extra-large egg yolks', {"entities": [(0, 1, "CARDINAL")]})
]


@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int)
)
def main(model=None, output_dir=None, n_iter=100):
    # Load the model, set up the pipeline and train the entity recognizer
    if model is not None:
        nlp = spacy.load(model)  # load existing spaCy model
        print("Loaded model {}".format(model))
    else:
        nlp = spacy.blank("en")  # create blank language class
        print("Created blank 'en' model.")

    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner, last=True)
    # otherwise, get it so we can add labels
    else:
        ner = nlp.get_pipe("ner")


    # add labels
    #    for _, annotations in TRAIN_DATA:
    #        for ent in annotations.get("entities"):
    #            ner.add_label(ent[2])

    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiercer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes):  # only train NER
        # reset and initialize the weights randomly -- but only if we're
        # training a new model
        if model is None:
            nlp.begin_training()
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            losses = {}
            # batch up the examples using spaCy's minibatch
            batches = minibatch(TRAIN_DATA, size=compounding(4.0, 32.0, 1.001))
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(
                    texts,  # batch of texts
                    annotations,  # batch of annotations
                    drop=0.5,  # dropout - make it harder to memorize data
                    losses=losses
                )
            print("Losses: {}".format(losses))

    # test the trained model
    for text, _ in TRAIN_DATA:
        doc = nlp(text)
        print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
        print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.to_disk(output_dir)
        print("Saved model to", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        for text, _ in TRAIN_DATA:
            doc = nlp2(text)
            print("Entities", [(ent.text, ent.label_) for ent in doc.ents])
            print("Tokens", [(t.text, t.ent_type_, t.ent_iob) for t in doc])


def generate_training_data(spacy_model, place_to_save):
    nlp = spacy.load(spacy_model)
    AUTO_TRAIN_DATA = []

    for line in ingredient_dataset:
        doc = nlp(line)
        AUTO_TRAIN_DATA.append((line, {"entities": [(ent.start_char, ent.end_char, ent.label_) for ent in doc.ents]}))

    with open(place_to_save, 'a') as annotated_data:
        pp = pprint.PrettyPrinter()
        annotated_data.write(pp.pformat(AUTO_TRAIN_DATA))


if __name__ == "__main__":
    nlp = spacy.load("test_auto_training")

    for line in ingredient_dataset:
        doc = nlp(line)
        print(line, [(ent.text, ent.label_) for ent in doc.ents])


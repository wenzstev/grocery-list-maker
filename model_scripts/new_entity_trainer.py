from __future__ import unicode_literals, print_function

import plac
import random
from pathlib import Path
import spacy
from spacy.util import minibatch, compounding

from old_version.combined_data_old_annotations import new_annotated_data

LABEL = "INGREDIENT"

TRAIN_DATA = new_annotated_data

@plac.annotations(
    model=("Model name. Defaults to blank 'en' model.", "option", "m", str),
    new_model_name=("New model name for model meta.", "option", "nm", str),
    output_dir=("Optional output directory", "option", "o", Path),
    n_iter=("Number of training iterations", "option", "n", int),
)
def main(model=None, new_model_name="ingredient", output_dir=None, n_iter=30):
    # Set up the pipeline and entity recognizer, and train the new entity
    random.seed(0)
    if model is not None:
        nlp = spacy.load(model)
        print("Loaded model {}".format(model))
    else:
        nlp = spacy.blank("en")
        print("Created blank 'en' model")
    # add entity recognizer to the model if it's not in the pipeline
    # nlp.create_pipe works for built-ins that are registered iwth spaCy
    if "ner" not in nlp.pipe_names:
        ner = nlp.create_pipe("ner")
        nlp.add_pipe(ner)
    # otherwise, get it, so we can add labels to it
    else:
        ner = nlp.get_pipe("ner")

    ner.add_label(LABEL) # add new entity label to entity recognizer

    if model is None:
        optimizer = nlp.begin_training()
    else:
        optimizer = nlp.resume_training()

    move_names = list(ner.move_names)

    # get names of other pipes to disable them during training
    pipe_exceptions = ["ner", "trf_wordpiercer", "trf_tok2vec"]
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]
    with nlp.disable_pipes(*other_pipes):   # only train NER
        sizes = compounding(1.0, 4.0, 1.001)
        # batch up the examples using spaCy's minibatch
        for itn in range(n_iter):
            random.shuffle(TRAIN_DATA)
            batches = minibatch(TRAIN_DATA, size=sizes)
            losses = {}
            for batch in batches:
                texts, annotations = zip(*batch)
                nlp.update(texts, annotations, sgd=optimizer, drop=0.35, losses=losses)
            print("Losses", losses)

    # test the trained model
    test_text = "1 cup brown sugar"
    doc = nlp(test_text)
    print("Entities in {}".format(test_text))
    for ent in doc.ents:
        print(ent.label_, ent.text)

    # save model to output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
        if not output_dir.exists():
            output_dir.mkdir()
        nlp.meta["name"] = new_model_name # rename model
        nlp.to_disk(output_dir)
        print("Saved model to ", output_dir)

        # test the saved model
        print("Loading from", output_dir)
        nlp2 = spacy.load(output_dir)
        # check the classes have loaded back consistently
        assert nlp2.get_pipe("ner").move_names == move_names
        doc2 = nlp2(test_text)
        for ent in doc2.ents:
            print(ent.label_, ent.text)

if __name__ == "__main__":
    plac.call(main)





import spacy 

nlp = None
nlp_error = None


def get_ner_model():
    global nlp, nlp_error

    if nlp is None and nlp_error is None:
        try:
            nlp = spacy.load('en_core_web_md')
        except Exception as exc:
            nlp_error = exc

    if nlp_error is not None:
        raise RuntimeError(
            "spaCy model 'en_core_web_md' could not be loaded. Install it locally before using NER."
        ) from nlp_error

    return nlp

def extract_entities(text):
    doc = get_ner_model()(text)
    entities = []

    for ent in doc.ents:
        entities.append({'text': ent.text, 'label': ent.label_})
    return entities

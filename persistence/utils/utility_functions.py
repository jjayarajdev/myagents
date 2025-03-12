import spacy

# utility funciton to generate a shart name for given user question.
def generate_name(question):
    # Process the question using Spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(question)

    # Remove stopwords and punctuation
    tokens = [token.text for token in doc if not token.is_stop and not token.is_punct]

    # Remove words with length less than 3
    tokens = [token for token in tokens if len(token) > 2]

    # Generate a name based on the meaningful words
    meaningful_tokens = [token.capitalize() for token in tokens]
    if len(meaningful_tokens) > 3:
        name =' '.join(meaningful_tokens[:3])
    elif len(meaningful_tokens) > 1:
        name =' '.join(meaningful_tokens)
    elif len(meaningful_tokens) == 1:
        name = meaningful_tokens[0]
    else:
        # If no meaningful words are found, return the first 3 words of the question
        question_tokens = [token.text for token in doc]
        name =' '.join(question_tokens[:3])

    return name
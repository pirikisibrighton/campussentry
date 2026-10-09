import sys
import spacy, nltk, sklearn, pandas, numpy, gensim
import transformers, datasets, seqeval, streamlit

print("Python:", sys.version.split()[0])
print("spaCy:", spacy.__version__)
print("scikit-learn:", sklearn.__version__)
print("transformers:", transformers.__version__)

nlp = spacy.load("en_core_web_sm")
doc = nlp("There is a fire at the library near the main gate.")
print([(t.text, t.lemma_) for t in doc][:6])
print("All good.")
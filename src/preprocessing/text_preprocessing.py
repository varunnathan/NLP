import sys
import re
import nltk
from autocorrect import Speller
sys.setdefaultencoding('utf-8')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

SPELL = Speller(lang='en')


class TemplateCleaner(object):
    def __init__(self, text):
        self.cleaned_text = text

    def cleaner(self, stri):
        sents = nltk.tokenize.sent_tokenize(self.cleaned_text)
        word_dump = []
        for sent in sents:
            if stri in sent:
                ss = re.split(re.escape(stri), sent)
                word_dump.append(ss[0])
            else:
                word_dump.append(sent)
        self.cleaned_text = " ".join(word_dump)


def regex_cleaning(text):
    text = re.sub(r'http\S+', ' ', text)
    text = re.sub(r'www\S+\.com', ' ', text)
    text = re.sub(r'[!,\#()]', ' ', text)
    return text


def preprocess(text):
    # pos - keep only nouns and adjectives
    text = " ".join(t[0] for t in nltk.pos_tag(nltk.wordpunct_tokenize(text)) if t[1].startswith('N') or t[1].startswith('J'))

    # lower casing
    text = text.strip().lower()

    # contraction

    # regex cleaning

    # remove numerals
    text = re.sub(r'[0-9]+', ' ', text)

    # spell correction
    text = " ".join(SPELL(w) for w in nltk.wordpunct_tokenize(text))

import csv
import preprocessor as p
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from gensim.models import Phrases
from gensim.corpora import Dictionary
from gensim.models import HdpModel 
import logging

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

def extract_tweets():
    with open('./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for tweet in reader: yield tweet[4]

documents = list(extract_tweets())

# cleaning
p.set_options(p.OPT.URL, p.OPT.EMOJI, p.OPT.EMOJI, p.OPT.MENTION, p.OPT.SMILEY, p.OPT.NUMBER)
documents = [p.clean(t) for t in documents]

# tokenizing and removing bad tokens
tokenizer = RegexpTokenizer(r'\w+')
documents = [tokenizer.tokenize(t.lower()) for t in documents]

documents = [[token for token in tweet if not token.isnumeric()] for tweet in documents]
documents = [[token for token in tweet if len(token) > 1] for tweet in documents]


# lematizer
lemmatizer = WordNetLemmatizer()
documents = [[lemmatizer.lemmatize(token) for token in tweet] for tweet in documents]


# bigrams
bigram = Phrases(documents, min_count=20)
# everything is gonna be bow-ed, so we don't need to care abt word order, just add to end
for idx in range(len(documents)): 
    for token in bigram[documents[idx]]: 
        if '_' in token:
            documents[idx].append(token)

# stopwords
stop_words = set(stopwords.words('english'))
documents = [[token for token in tweet if token not in stop_words] for tweet in documents]
print(documents[:4])
dictionary = Dictionary(documents)  
dictionary.filter_extremes(no_below=20, no_above=0.5)

corpus = [dictionary.doc2bow(tweet) for tweet in documents]

# the model itself!!

num_topics = 10
chunksize = 4000
passes = 20
iterations = 400
eval_every = None  # Don't evaluate model perplexity, takes too much time.

# Make an index to word dictionary.
temp = dictionary[0]  # This is only to "load" the dictionary.
id2word = dictionary.id2token

model = HdpModel(
    corpus=corpus,
    id2word=id2word,
    chunksize=chunksize,
)
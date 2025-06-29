import csv
from bertopic import BERTopic
import numpy as np
from sentence_transformers import SentenceTransformer

def get_docs():
    docs = []
    files = ['./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv','./data/mide22/mide22_en_misinfo_tweets_hydrated_conversations.tsv''' ]
    for file in files:
        with open(file) as infile:
            reader = csv.reader(infile, delimiter='\t')
            for t in reader: docs.append(t[0] + " " + t[2] + " " + t[5])
    return docs



docs = get_docs()
print(docs[:10])

topic_model = BERTopic(verbose=True)
embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
embeddings = embedding_model.encode(docs, show_progress_bar=True)
np.save('./data/model/embeddings.npy', embeddings)
topics, probs = topic_model.fit_transform(docs, embeddings=embeddings)
hierarchical_topics = topic_model.hierarchical_topics(docs)
fig = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
fig.write_html('./data/model/out.html')




    
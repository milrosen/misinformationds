import csv
from bertopic import BERTopic
import numpy as np
from sentence_transformers import SentenceTransformer
from hdbscan import HDBSCAN
from umap import UMAP
from sklearn.metrics import adjusted_rand_score, homogeneity_score
import itertools

topics = {'Ukraine':0, 'Covid':1, 'Refugees':2, 'Misc':3}
truth = {'True':0, 'False':1, 'Other':2, 'UNK':3}

def strings_to_labels(topic, truthieness):
    if truthieness in truth: 
        return topics[topic] * 4 + truth[truthieness]
    else: return topics[topic] * 4 + 3


def get_docs():
    docs = []
    true_labels = []
    files = ['./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv','./data/mide22/mide22_en_misinfo_tweets_hydrated_conversations.tsv''' ]
    for file in files:
        with open(file) as infile:
            reader = csv.reader(infile, delimiter='\t')
            for t in reader: 
                truthieness = t[2] if t[2] in truth else ''
                docs.append(t[0] + " " + truthieness + " " + t[5])
                true_labels.append(strings_to_labels(t[0], t[2]))
    return docs, true_labels

docs, true_labels = get_docs()

embeddings = np.load('./data/model/embeddings.npy')
def scuffed_grid_search():
    min_cluster_sizes = [10, 15, 20, 100]
    min_sampless = [5, 8, 10, 15]
    cluster_selection_methods = ['eom']

    n_neighborss = [2, 5, 10, 20, 50]
    min_dists = [0.0, 0.1, 0.2]
    n_componentss = [4, 5, 6, 7, 8]

    for (mcs, ms, csm, nn, md, nc) in itertools.product(min_cluster_sizes, min_sampless, cluster_selection_methods, n_neighborss, min_dists, n_componentss):
        perform_single_search(mcs, ms, csm, nn, md, nc)

scores = []
cutoff_homogeneity = -10
best_homogeneity = []
def perform_single_search(min_cluster_size, min_samples, cluster_selection_method, 
                          n_neighbors, min_dist, n_components):    
    global cutoff_homogeneity
    global best_homogeneity 
    hdbscan_model = HDBSCAN(min_cluster_size=min_cluster_size, min_samples=min_samples, metric='euclidean', cluster_selection_method=cluster_selection_method, prediction_data=True)
    umap_model = UMAP(n_neighbors=n_neighbors, n_components=n_components, min_dist=min_dist, metric='cosine', random_state=42)

    topic_model = BERTopic(verbose=True, hdbscan_model=hdbscan_model, umap_model=umap_model)
    """ embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    embeddings = embedding_model.encode(docs, show_progress_bar=True)
    np.save('./data/model/embeddings.npy', embeddings) """
    topics, probs = topic_model.fit_transform(docs, embeddings=embeddings)
    predicted_labels = hdbscan_model.labels_
    homogeneity = homogeneity_score(true_labels, predicted_labels)
    score = [homogeneity, min_cluster_size, min_samples, cluster_selection_method, n_neighbors, min_dist, n_components]
    scores.append(score)
    if homogeneity > cutoff_homogeneity:
        best_homogeneity.append(score)
        best_homogeneity.sort(key=lambda a: a[1], reverse=True)
        if len(best_homogeneity) > 50:
            best_homogeneity.pop()
        cutoff_homogeneity = max(cutoff_homogeneity, best_homogeneity[-1][1])

    hierarchical_topics = topic_model.hierarchical_topics(docs)
    fig = topic_model.visualize_hierarchy(hierarchical_topics=hierarchical_topics)
    fig.write_html(f'./data/model/out_{homogeneity:.3f}__{min_cluster_size}_{min_samples}_{cluster_selection_method}__{n_neighbors}_{min_dist}_{n_components}.html')

scuffed_grid_search()
print(scores)
print("IMPORTANT")
[print(score) for score in best_homogeneity]


    
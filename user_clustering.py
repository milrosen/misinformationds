import csv
import networkx as nx

retweet_weight = 1
mention_weight = 4
qrt_weight = 6
reply_weight = 6

def add_edge(graph, frm, to, amt):
    if frm + "_" + to not in graph:
        graph[frm + "_" + to] = 0
    graph[frm + "_" + to] += amt

def add_tweets_to_graph(tweets, graph):
    for tweet in tweets:
        from_id = tweet[4]

        if tweet[14] is not None and tweet[14] != "[]":
            mentioned_users = tweet[14]
            id_start = mentioned_users.find("=") - 10
            id_end = mentioned_users.find(",")
            while id_start != -1:
                mentioned_user_id = mentioned_users[id_start+11:id_end]
                add_edge(graph, from_id, mentioned_user_id, mention_weight)
                id_start = mentioned_users.find("UserRef(id=", id_start+1)
                id_end = mentioned_users.find(",", id_start)
        
        if tweet[18] is not None and tweet[18] != '':
            quoted_tweet = tweet[18]
            id_start = quoted_tweet.find("user=User(id=")
            if id_start != -1:
                id_end = quoted_tweet.find(",", id_start)
                quoted_tweet_user_id = quoted_tweet[id_start+13:id_end]
                add_edge(graph, from_id, quoted_tweet_user_id, qrt_weight) 
        
        if tweet[20] is not None and tweet[18] != '': 
            replied_user = tweet[18]
            id_start = replied_user.find("UserRef(id=")
            if id_start != -1:
                id_end = replied_user.find(",", id_start)
                replied_user_id = replied_user[id_start+11:id_end]
                add_edge(graph, from_id, replied_user_id, reply_weight) 
    return graph

def process_retweets(graph):
    with open('./data/mide22/mide22_en_misinfo_tweets_hydrated_retweets.tsv') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for tweet in reader:
            add_edge(graph, tweet[0], tweet[1], retweet_weight)

def process_tweets():
    graph = {}
    with open('./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv') as infile:
        reader = csv.reader(infile, delimiter='\t')
        graph = add_tweets_to_graph(reader, graph)
    with open('./data/mide22/mide22_en_misinfo_tweets_hydrated_conversations.tsv') as infile:
        reader = csv.reader(infile, delimiter='\t')
        graph = add_tweets_to_graph(reader, graph)
    process_retweets(graph)
    return graph

def graph_to_nodex():
    edges_dict = process_tweets()
    G = nx.Graph()
    edgelist = [(edge.split("_")[0], edge.split("_")[1], w) for edge, w in edges_dict.items()]
    G.add_weighted_edges_from(edgelist)
    return G

def main():
    G = graph_to_nodex()
    communities = nx.community.greedy_modularity_communities(G)
    for node in list(G.nodes):
        for idx in range(50):
            community = communities[idx]
            if node in community:
                G.nodes[node]["id"] = idx
    nx.write_gexf(G, "test.gexf")
if __name__=="__main__":
    main()
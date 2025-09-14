# Step one: get all of my user data associated with each CSV in the same area.
# For each tweet, I want to find the shortest distance in the graph to the centroid
# of the cluster, as well as the cosine distance. I want the truth or falsity
# and I want the information about the user (followers, centrality, maybe more later)
# and then if the tweet is labled I want the label

import csv

# Topic, Fold, Truth, Tweet ID, UserID, Content, Date, rts, likes, qrts, bookmarks, conversationID, hashtags, cashtags, mentionedUsers, links, viewCount, retweetedTweet, quotedTweet, inReplyToTweetID, inReplyToUser
def prepare_data():
    data = {} 
    files = ['./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv','./data/mide22/mide22_en_misinfo_tweets_hydrated_conversations.tsv''' ]
    for file in files:
        with open(file) as infile:
            reader = csv.reader(infile, delimiter='\t')
            for t in reader: 
                data[t[3]] = {'truth': t[3], 'topic':t[1]}
    return data 

data = prepare_data()

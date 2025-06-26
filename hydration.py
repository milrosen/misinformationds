# USAGE: 
#   1) Add correct api keys and cookies to a file called "accounts.txt" 
#   2) Find out the correct format of your data, mine was username:password:email:email_password:_:_:cookies
#       (hints: the cookies should be base64 encoded json, so you can check manually if the format isn't supplied)
#   3) Run "twscrape add_accounts ./accounts.txt [FORMAT]" this creates the file accounts.db which 
#       will be used when the script is run

# DATA:
#   public datasets are often in github, it is usefull to copy just the files you want
#       1) add the name of the repo to your gitignore (just in case)
#       2) run these commands
#           git clone -n --depth=1 --filter=tree:0 [REPO]
#           cd [REPO NAME]
#           git sparse-checkout set --no-cone [SPACE DELIMITED LIST OF DIRECTORIES]
#           git checkout 


import asyncio
import twscrape
from twscrape import API
from asyncio import gather
import csv
import os
import httpx
proxy = os.getenv("TWS_PROXY")

def tweet_details_to_row(tweet: twscrape.Tweet):
    return [
        # 
        # 
        # 
        tweet.id,
        tweet.user.id,
        tweet.rawContent.replace('\n', '\\n').replace('\t', '\\t'), 
        tweet.date,
        tweet.retweetCount,
        tweet.likeCount,
        tweet.quoteCount,
        tweet.bookmarkedCount,
        tweet.conversationId,
        tweet.hashtags,
        tweet.cashtags,
        tweet.mentionedUsers,
        tweet.links,
        tweet.viewCount,
        tweet.retweetedTweet, # 12
        tweet.quotedTweet,
        tweet.inReplyToTweetId, # 13
        tweet.inReplyToUser
    ]

async def worker(queue: asyncio.Queue, api: twscrape.API, writer):
    while True:
        row = await queue.get()
        try:
            tweet = await api.tweet_details(int(row[3]))
            writer.writerow(row + [
                tweet.user.id,
                tweet.rawContent.replace('\n', '\\n').replace('\t', '\\t'), 
                tweet.date,
                tweet.retweetCount,
                tweet.likeCount,
                tweet.quoteCount,
                tweet.bookmarkedCount,
                tweet.conversationId,
                tweet.hashtags,
                tweet.cashtags,
                tweet.mentionedUsers,
                tweet.links,
                tweet.viewCount,
                tweet.retweetedTweet, # 15
                tweet.quotedTweet,
                tweet.inReplyToTweetId, # 17
                tweet.inReplyToUser,
            ])
        except AttributeError:
            pass
            # print(row[3])
        finally:
            queue.task_done()


async def worker_retweets(queue: asyncio.Queue, api: twscrape.API, writer, closed_up: set, closed_down: set):
    while True: 
        row = await queue.get()
        id = row[3]
        try: 
            if id not in closed_down:
                closed_down.add(id)
                async for t in api.tweet_replies(int(id), limit=50):
                    row_persist = (row[:3] + tweet_details_to_row(t))
                    writer.writerow(row_persist)
                    closed_up.add(t.id)
                    print(queue.qsize())
                    await queue.put(row_persist)
                
            if id not in closed_up:
                closed_up.add(id)
                if row[17] != "" and row[17] is not None:
                    id_str = str(row[17])
                    idx = id_str.find(",", 9)
                    reply_to_id = row[17][9:idx]
                    if reply_to_id not in closed_up:
                        t = await api.tweet_details(int(reply_to_id))
                        row_persist = (row[:3] + tweet_details_to_row(t))
                        writer.writerow(row_persist)
                        print(queue.qsize())
                        await queue.put(row_persist)

        except AttributeError:
            pass
        except httpx.ConnectTimeout:
            print("Disconnected Error")
            await queue.put(row)
            await asyncio.sleep(60)
            pass
        finally: 
            queue.task_done()


async def hydrate_initial():
    api = API(proxy=proxy)

    queue = asyncio.Queue()
    workers_count = 19

    with open('./mide22/dataset/EN/mide22_en_misinfo_tweets.tsv') as infile:
        reader = csv.reader(infile, delimiter='\t')
        tweets = list(reader)
    with open('./data/mide22/mide22_en_misinfo_tweets_hydrated_users.tsv', "a") as outfile:
        writer = csv.writer(outfile, delimiter='\t')
        workers = [asyncio.create_task(worker(queue, api, writer)) for _ in range(workers_count)]
        for t in tweets:
            queue.put_nowait(t)
        await queue.join()
        for worker_task in workers:
            worker_task.cancel()
       
       
async def main():
    api = API(proxy=proxy)  
    queue = asyncio.Queue() 
    workers_count = 19
    closed_up = set()
    closed_down = set()

    with open('./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv') as infile:
        reader = csv.reader(infile, delimiter='\t')
        for t in reader:
            t[2] = t[3]
            queue.put_nowait(t)
    
    with open('./data/mide22/mide22_en_misinfo_tweets_hydrated_conversations.tsv', "a") as outfile:
        writer = csv.writer(outfile, delimiter='\t')       
        workers = [asyncio.create_task(worker_retweets(queue, api, writer, closed_up, closed_down))]
        await queue.join()
        pass
    # await hydrate_initial()
if __name__ == "__main__": 
    asyncio.run(main())

import asyncio
from twscrape import API
import csv
import os
proxy = os.getenv("TWS_PROXY")


async def worker(queue: asyncio.Queue, writer: csv.DictWriter, api: API):
    while True:
        row = await queue.get()
        try:
            user_info = await api.user_by_id(int(row["id"]))
            user_info = vars(user_info)
            user_info["rawDescription"] = user_info['rawDescription'].replace('\n', '\\n').replace('\t', '\\t') 
            writer.writerow(row|user_info)
        except IndexError:
            print("exception")
            pass
        finally: 
            queue.task_done()

def get_users():
    users = {}
    users_out = {}
    with open("./data/mide22/mide22_en_misinfo_tweets_hydrated.tsv") as infile:
        reader = csv.reader(infile, delimiter='\t')
        for tweet in list(reader):
            if tweet[4] in users: continue
            else: 
                users[tweet[4]] = {"topic": tweet[0], "truth":tweet[2], "id":tweet[4], "confidence":"label"}

    with open("./data/mide22/mide22_en_misinfo_tweets_hydrated_conversations.tsv") as infile:
        reader = csv.reader(infile, delimiter='\t')
        for tweet in list(reader):
            if tweet[4] in users: continue
            else:
                users[tweet[4]] = {"topic": tweet[0], "truth":"UNK", "id":tweet[4], "confidence":"propagation"} 
                
    with open("./data/mide22/mide22_en_misinfo_tweets_hydrated_retweets.tsv") as infile:
        reader = csv.reader(infile, delimiter="\t")
        for [retweeter, retweeted] in list(reader):
            if retweeter not in users:
                if retweeted in users:
                    users[retweeter] = dict.copy(users[retweeted])
                    users[retweeter]["id"] = retweeter
                    users_out[retweeter] = users[retweeter]
                else:
                    print("neither tweeter nor retweeter in users, something very wrong")

    return users_out

async def main():
    queue = asyncio.Queue()
    api = API(proxy=proxy)
    users = get_users()
    workers_count = 19

    with open("./data/mide22/mide22_en_misinfo_user_details.tsv", "a") as outfile:
        fieldnames = ['topic', 'truth', 'id', 'confidence', 'verified', 'id_str', 'blueType', 'displayname', 'descriptionLinks', 'username', 'listedCount', 'profileImageUrl', 'protected', 'blue', 'url', 'friendsCount', 'favouritesCount', 'statusesCount', 'followersCount', '_type', 'mediaCount', 'profileBannerUrl', 'location', 'rawDescription', 'pinnedIds', 'created']

        writer = csv.DictWriter(outfile, fieldnames, delimiter='\t')
        for row in users.values(): 
            queue.put_nowait(row)
        workers = [asyncio.create_task(worker(queue, writer, api)) for _ in range(workers_count)]
        await queue.join()
    
    for worker_task in workers:
        worker_task.cancel()

if __name__=="__main__":
    asyncio.run(main())
       